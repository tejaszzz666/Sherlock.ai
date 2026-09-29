@echo off
echo ================================
echo Starting Sherlock.ai Backend
echo (Simple Version)
echo ================================
echo.

cd /d D:\Sherlock.ai\backend

echo Starting server...
echo Backend: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press CTRL+C to stop
echo.

python app_simple.py

pause
