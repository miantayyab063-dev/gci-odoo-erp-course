GCI — ODOO ERP LEARNING STUDIO
English / العربية | Local PC edition | 30 October 2026

ROMAN URDU QUICK START
1. ZIP par right-click kar ke Extract All karein. ZIP ke andar se launcher na chalayein.
2. Python 3.10 ya newer install hona chahiye: https://www.python.org/downloads/
   Installation mein Add Python to PATH select karein.
3. START_WINDOWS.bat double-click karein. Browser khud khulega.
4. Pehli dafa apna ADMIN LOGIN CODE aur PASSWORD set karein (kam az kam 10 characters).
   Yeh Odoo ka login nahi; is local course portal ka login hai.
5. Launcher ki console window khuli rakhein. Band karne par website service ruk jayegi.
6. English / العربية button se language badlein.
7. Har lesson ke akhir mein Video URL paste karein. Field se bahar click karne par
   player refresh hoga. Duration apni marzi se neeche likhein. Saved on this PC dekhein.
8. Manage se student accounts banayein. Student course dekh sakta hai, apni notes
   aur progress save kar sakta hai. Course text/video sirf admin edit karta hai.
9. Edit lesson se English aur Arabic body, tasks, quiz aur title edit karein.
   Bari text (30,000 words per lesson) supported hai. Actual word counts dikhte hain.
10. Manage > Export backup JSON se backup download karein. Course ki original
    extracted folder ko delete na karein; data usi ke andar save hota hai.

IMPORTANT CONTENT SCOPE
This package contains 12 original, bilingual practical foundation lessons, labs,
worked numeric examples and one quiz per lesson. It DOES NOT contain 30,000 words
per lesson. The English + Arabic explanation bodies total about 3,990 words.
They are short teaching notes, not a complete 360,000-word textbook. The editor
and local storage support expanding each lesson to 30,000 words or more. No
repeated filler has been used to simulate length. Arabic is written as real text,
not an image or automated placeholder. Five user-supplied Google Drive video links are now inserted into lessons 1–5.
See VIDEO_LINKS_ADDED.txt for filenames, links and topic-matching limitations.
No video files are bundled. The other lesson video fields remain editable.

LESSONS
01 ERP foundations
02 Navigation and working safely
03 Company setup and access roles
04 Contacts and product master data
05 CRM pipeline and follow-up
06 Sales: quotation to customer order
07 Purchasing and supplier control
08 Inventory, delivery and returns
09 Invoices, bills and reconciliation
10 Manufacturing fundamentals
11 Projects, employees and operating reports
12 Implementation capstone and handover

VIDEO LINK GUIDE
- Direct HTTPS .mp4, .webm, .ogg or .m4v URL: built-in HTML video player.
- YouTube watch, short, youtu.be or embed URL: converted to provider player.
- Vimeo public URLs and supported unlisted hashes: converted to provider player.
- Google Drive /file/d/FILE_ID/view or open?id=FILE_ID: converted to preview.
  Drive must permit your browser to view the file. An owner may disable embedding;
  large-file, quota, authentication and browser cookie restrictions can interfere.
- Other HTTPS links: Open original video button. Arbitrary webpages cannot always
  be embedded. The portal does not bypass permissions or download paid videos.
- Offline local file: copy your MP4 to the videos folder, then use
  /videos/lesson01.mp4 as the lesson URL. Keep filenames simple.
- Browser will not autoplay with sound; press Play. Streaming needs internet.
- Actual playback against a particular remote video depends on the provider.

SAVE / BACKUP / TRANSFER
The standard-library Python server saves data/course.json, data/users.json and
per-user progress in data/progress.json. Writes are atomic. Do not edit these
while the server runs. Wait for Saved on this PC before closing. Click the save
status to retry if it says Not saved. A conflict between two editing tabs is
reported; copy unsaved text elsewhere and reload before continuing.

Export backup includes course content, video links and learner progress/notes.
It does NOT include credentials or actual MP4 files. Restore is administrator-only
and replaces course/progress after confirmation. Previous course/progress is kept
in data/before-restore.json. The export limit is 20 MB per restore request.

To transfer EVERYTHING: stop the server and copy the ENTIRE extracted folder,
including data and videos, to another PC. Install Python and launch there. Treat
this folder and JSON backups as private; they may contain learner notes.
Changing browser or server port does not erase saved data. Closing the browser
ends the browser session; the server also expires sessions after eight hours.

LOGIN LIMITS
Passwords are salted and scrypt-hashed. Server listens only on 127.0.0.1, not the
network. Students cannot write course content through the server API. Local videos
also require login. This is a local course access gate, NOT encrypted DRM. Someone
who can read/edit your PC files can copy the content or reset local data. Do not
use this package as a public hosting service or a paid-content protection system.
For hosted multi-device access, use a separately designed production service.

If all admin credentials are lost, stop the server and move data/users.json to a
private backup location, then relaunch and set up a new administrator. Existing
course text remains, but previous learner progress stays linked to old codes.
A PC administrator can do this, which is another reason this is not DRM.

LANGUAGE AND REFERENCE NOTES
The learner-facing lesson body, objectives, lab, caution and quiz have English and
Arabic versions with RTL layout. Some administrator and system utility messages
are English or bilingual. This is independent training material; no official Odoo
endorsement, certification, Saudi accreditation or employment guarantee is claimed.
It does not execute Odoo transactions; use your own separate training database.
Features vary by Odoo version/edition/modules. Country tax and payroll setup must
be checked separately by qualified specialists.

Official version 19 references consulted / linked on 30 October 2026:
https://www.odoo.com/documentation/19.0/applications/sales/sales.html
https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/purchase.html
https://www.odoo.com/documentation/19.0/applications/finance/accounting.html
https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp.html
Other lesson reference links point to corresponding Odoo documentation topics;
if a topic URL changes, use the official documentation search.

MAC / LINUX
Use Python 3.10+. In Terminal: python3 server.py
Or make START_MAC_LINUX.command executable and open it. No pip packages required.

HELP
Blank page after opening index.html directly: use the launcher; a server is required.
Windows shows Python missing: install Python and reopen launcher.
Save fails: check folder write permissions and free disk space; avoid read-only media.
Video blank: verify sharing permissions and try Open original video.
Audio/video codec unsupported: use a browser-compatible MP4 (e.g. H.264/AAC).
No internet: course notes and local videos work; remote videos need internet.
Do not start two server instances from the same course folder simultaneously.
