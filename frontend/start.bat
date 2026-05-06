@echo off
cd /d "%~dp0"
echo Starting Toddly Frontend...
echo.
echo Frontend: http://localhost:8000
echo Signup: http://localhost:8000/signup.html
echo Login: http://localhost:8000/login.html
echo Tests: http://localhost:8000/test.html
echo.
echo Make sure the backend is running on http://localhost:8001 first!
echo.
python -m http.server 8000
pause
