@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
 py -3 server.py
 goto end
)
where python >nul 2>nul
if %errorlevel% equ 0 (
 python server.py
 goto end
)
echo Python 3.10 or newer is required. Install from https://www.python.org/downloads/
echo During setup choose Add Python to PATH, then reopen this file.
:end
pause
