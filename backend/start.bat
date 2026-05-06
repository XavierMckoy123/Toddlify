@echo off
cd /d "%~dp0"
echo Starting Toddly Backend with SQLite...
echo.
echo Database: toddly.db (local file)
echo Server: http://localhost:8001
echo.
python run.py
pause
