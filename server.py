"""Local-only, standard-library course server. Python 3.10+."""
import base64, hashlib, hmac, json, mimetypes, os, secrets, threading, time, webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
LOCK=threading.RLock(); SESSIONS={}; ATTEMPTS={}

def read(name,default=None):
 p=DATA/name
 return json.loads(p.read_text('utf-8')) if p.exists() else default

def write(name,obj):
 p=DATA/name; tmp=p.with_suffix('.tmp')
 with tmp.open('w',encoding='utf-8') as f:
  json.dump(obj,f,ensure_ascii=False,indent=2); f.flush(); os.fsync(f.fileno())
 os.replace(tmp,p)

def password(value,salt=None):
 salt=salt or secrets.token_hex(16)
 return {'salt':salt,'hash':hashlib.scrypt(value.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1).hex()}

def valid_course(c):
 if not isinstance(c,dict) or not isinstance(c.get('lessons'),list) or not 1<=len(c['lessons'])<=200: raise ValueError('Invalid course')
 ids=set()
 for l in c['lessons']:
  if not isinstance(l,dict) or not isinstance(l.get('id'),str) or l['id'] in ids: raise ValueError('Invalid lesson identity')
  ids.add(l['id'])
  for key in ('title','body','mistake'):
   if not isinstance(l.get(key),dict) or any(not isinstance(l[key].get(k),str) for k in ('en','ar')): raise ValueError('Invalid bilingual text')
  for lang in ('en','ar'):
   if not isinstance(l.get('lab',{}).get(lang),list) or any(not isinstance(x,str) for x in l['lab'][lang]): raise ValueError('Invalid lab')
   if not isinstance(l.get('quiz',{}).get('question',{}).get(lang),str): raise ValueError('Invalid question')
   op=l['quiz'].get('options',{}).get(lang)
   if not isinstance(op,list) or len(op)!=3 or any(not isinstance(x,str) for x in op): raise ValueError('Invalid options')
  if type(l['quiz'].get('answer')) is not int or not 0<=l['quiz']['answer']<3: raise ValueError('Invalid answer')
  for k in ('video','duration','source'):
   if not isinstance(l.get(k),str): raise ValueError('Invalid link or duration')
  l['revision']=max(1,int(l.get('revision',1)))
 return c

with LOCK:
 if not (DATA/'course.json').exists(): write('course.json',json.loads((ROOT/'course.seed.json').read_text('utf-8')))

class Handler(BaseHTTPRequestHandler):
 server_version='GCI-Local/1.0'
 def log_message(self,*args): pass
 def send(self,status,obj=None,raw=None,ctype='application/json; charset=utf-8',headers=None):
  b=raw if raw is not None else json.dumps(obj,ensure_ascii=False).encode()
  self.send_response(status)
  self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(b)))
  self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff')
  self.send_header('X-Frame-Options','DENY'); self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
  self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-src https:; media-src 'self' https:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'")
  for k,v in (headers or {}).items(): self.send_header(k,v)
  self.end_headers(); self.wfile.write(b)
 def body(self):
  n=int(self.headers.get('Content-Length','0'))
  if not 0<n<=20*1024*1024: raise ValueError('Request must be between 1 byte and 20 MB')
  return json.loads(self.rfile.read(n))
 def session(self):
  cookies=dict(item.strip().split('=',1) for item in self.headers.get('Cookie','').split(';') if '=' in item)
  sid=cookies.get('gci_session',''); s=SESSIONS.get(sid)
  if not s or s['expires']<time.time():
   SESSIONS.pop(sid,None); return None
  return s
 def trusted(self):
  host=self.headers.get('Host','')
  if host not in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'):
   self.send(403,{'error':'Local access only'}); return False
  origin=self.headers.get('Origin')
  if origin and origin not in ('http://'+host,):
   self.send(403,{'error':'Invalid origin'}); return False
  return True
 def do_GET(self):
  if not self.trusted(): return
  path=urlsplit(self.path).path
  if path in ('/','/index.html','/app.js','/style.css'):
   p=ROOT/('index.html' if path=='/' else path[1:])
   return self.send(200,raw=p.read_bytes(),ctype=mimetypes.guess_type(p.name)[0] or 'text/plain')
  if path=='/api/status':
   s=self.session(); return self.send(200,{'setup':not bool(read('users.json',{})),'user':{'code':s['code'],'role':s['role']} if s else None,'csrf':s['csrf'] if s else None})
  s=self.session()
  if not s: return self.send(401,{'error':'Please log in'})
  if path=='/api/course': return self.send(200,read('course.json'))
  if path=='/api/progress': return self.send(200,read('progress.json',{}).get(s['code'],{}))
  if path=='/api/backup':
   if s['role']!='admin': return self.send(403,{'error':'Administrator only'})
   return self.send(200,{'format':'gci-course-1','course':read('course.json'),'progress':read('progress.json',{})})
  if path=='/api/users':
   if s['role']!='admin': return self.send(403,{'error':'Administrator only'})
   return self.send(200,[{'code':k,'role':v['role']} for k,v in read('users.json',{}).items()])
  if path.startswith('/videos/'):
   p=(ROOT/unquote(path).lstrip('/')).resolve()
   if not p.is_relative_to((ROOT/'videos').resolve()) or not p.is_file(): return self.send(404,{'error':'Video not found'})
   # Browser seeking support; streamed to avoid loading large files into memory.
   size=p.stat().st_size; start=0; end=size-1; partial=False
   rg=self.headers.get('Range','')
   if rg:
    try:
     kind,spec=rg.split('=',1); a,b=spec.split('-',1)
     if kind!='bytes' or ',' in spec: raise ValueError()
     if a: start=int(a); end=min(int(b),size-1) if b else size-1
     else: start=max(0,size-int(b))
     if not 0<=start<=end<size: raise ValueError()
     partial=True
    except ValueError: return self.send(416,{'error':'Invalid range'},headers={'Content-Range':f'bytes */{size}'})
   self.send_response(206 if partial else 200); self.send_header('Content-Type',mimetypes.guess_type(p.name)[0] or 'application/octet-stream')
   self.send_header('Accept-Ranges','bytes'); self.send_header('Content-Length',str(end-start+1))
   self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff')
   if partial: self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
   self.end_headers()
   try:
    with p.open('rb') as f:
     f.seek(start); left=end-start+1
     while left:
      b=f.read(min(65536,left))
      if not b: break
      self.wfile.write(b); left-=len(b)
   except (BrokenPipeError,ConnectionResetError): pass
   return
  self.send(404,{'error':'Not found'})
 def do_POST(self):
  if not self.trusted(): return
  path=urlsplit(self.path).path
  try:
   b=self.body()
   with LOCK:
    users=read('users.json',{})
    if path in ('/api/setup','/api/login'):
     code=str(b.get('code','')).strip(); pw=b.get('password','')
     if not isinstance(pw,str): raise ValueError('Invalid password')
     if path=='/api/setup':
      if users: return self.send(409,{'error':'Setup already completed'})
      if not 3<=len(code)<=80 or len(pw)<10: raise ValueError('Code: 3–80 characters. Password: at least 10 characters.')
      users[code]={'role':'admin',**password(pw)}; write('users.json',users)
     else:
      # Global local-service limit prevents bypass by rotating account codes.
      failures=ATTEMPTS.setdefault('login',[]); failures[:]=[t for t in failures if t>time.time()-60]
      if len(failures)>=8: return self.send(429,{'error':'Too many attempts. Wait one minute.'})
      u=users.get(code)
      good=bool(u and hmac.compare_digest(password(pw,u['salt'])['hash'],u['hash']))
      if not good: failures.append(time.time()); return self.send(401,{'error':'Incorrect code or password'})
      failures.clear()
     token=secrets.token_urlsafe(32); csrf=secrets.token_urlsafe(24)
     SESSIONS[token]={'code':code,'role':users[code]['role'],'csrf':csrf,'expires':time.time()+8*3600}
     return self.send(200,{'ok':True},headers={'Set-Cookie':f'gci_session={token}; HttpOnly; SameSite=Strict; Path=/'})
    s=self.session()
    if not s: return self.send(401,{'error':'Please log in'})
    if not hmac.compare_digest(self.headers.get('X-CSRF-Token',''),s['csrf']): return self.send(403,{'error':'Invalid session token'})
    if path=='/api/logout':
     for k,v in list(SESSIONS.items()):
      if v is s: del SESSIONS[k]
     return self.send(200,{'ok':True},headers={'Set-Cookie':'gci_session=; Max-Age=0; HttpOnly; SameSite=Strict; Path=/'})
    if path=='/api/progress':
     p=read('progress.json',{}); current=p.setdefault(s['code'],{})
     lid=b.get('id'); known={l['id'] for l in read('course.json')['lessons']}
     if lid not in known: raise ValueError('Unknown lesson')
     current[lid]={'done':bool(b.get('done')),'notes':str(b.get('notes',''))[:100000],'answer':b.get('answer') if type(b.get('answer')) is int and 0<=b['answer']<3 else None}
     write('progress.json',p); return self.send(200,{'ok':True})
    if path=='/api/password':
     u=users[s['code']]
     if not hmac.compare_digest(password(str(b.get('old','')),u['salt'])['hash'],u['hash']): raise ValueError('Current password is incorrect')
     new=b.get('password','')
     if not isinstance(new,str) or len(new)<10: raise ValueError('New password needs at least 10 characters')
     users[s['code']]={'role':u['role'],**password(new)}; write('users.json',users)
     for k,v in list(SESSIONS.items()):
      if v['code']==s['code'] and v is not s: del SESSIONS[k]
     return self.send(200,{'ok':True})
    if s['role']!='admin': return self.send(403,{'error':'Administrator only'})
    if path=='/api/lesson':
     c=read('course.json'); candidate=b.get('lesson',{}); lid=candidate.get('id')
     i=next((i for i,l in enumerate(c['lessons']) if l['id']==lid),None)
     if i is None: raise ValueError('Unknown lesson')
     if b.get('revision')!=c['lessons'][i]['revision']: return self.send(409,{'error':'This lesson changed in another tab. Export your text, then reload before editing.'})
     candidate['revision']=c['lessons'][i]['revision']+1; c['lessons'][i]=candidate
     valid_course(c); write('course.json',c); return self.send(200,{'revision':candidate['revision']})
    if path=='/api/user':
     code=str(b.get('code','')).strip(); pw=b.get('password','')
     if code in users: raise ValueError('Code already exists')
     if not 3<=len(code)<=80 or not isinstance(pw,str) or len(pw)<10: raise ValueError('Code: 3–80 characters. Password: at least 10 characters.')
     users[code]={'role':'student',**password(pw)}; write('users.json',users); return self.send(200,{'ok':True})
    if path=='/api/restore':
     if b.get('format')!='gci-course-1': raise ValueError('Invalid backup format')
     c=valid_course(b.get('course')); progress=b.get('progress',{})
     if not isinstance(progress,dict): raise ValueError('Invalid progress')
     known={l['id'] for l in c['lessons']}
     for code,items in progress.items():
      if not isinstance(items,dict): raise ValueError('Invalid progress')
      for lid,item in items.items():
       if lid not in known or not isinstance(item,dict) or not isinstance(item.get('notes',''),str): raise ValueError('Invalid progress entry')
     # Preserve prior state for recovery; no accounts or passwords are imported.
     write('before-restore.json',{'course':read('course.json'),'progress':read('progress.json',{})})
     write('course.json',c); write('progress.json',progress); return self.send(200,{'ok':True})
    self.send(404,{'error':'Not found'})
  except (ValueError,TypeError,KeyError) as e: self.send(400,{'error':str(e)})
  except Exception: self.send(500,{'error':'Could not save. Check free disk space and folder write permissions.'})

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(); parser.add_argument('--no-browser',action='store_true'); parser.add_argument('--port',type=int,default=0); args=parser.parse_args()
 server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
 url=f'http://127.0.0.1:{server.server_port}'
 print('Odoo ERP Course — local PC mode',flush=True); print(url,flush=True)
 print('Keep this window open. Press Ctrl+C to stop. Your saved files remain in the data folder.',flush=True)
 if not args.no_browser: threading.Timer(0.8,lambda:webbrowser.open(url)).start()
 try: server.serve_forever()
 except KeyboardInterrupt: pass
 finally: server.server_close()
