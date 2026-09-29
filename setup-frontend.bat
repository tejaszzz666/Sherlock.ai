@echo off
echo ========================================
echo Sherlock.ai - Frontend Setup Script
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Step 1: Installing dependencies...
call npm install

if %errorlevel% neq 0 (
    echo.
    echo ERROR: npm install failed!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start the backend server:
echo    cd backend
echo    python app.py
echo.
echo 2. In a new terminal, start the frontend:
echo    cd frontend
echo    npm run dev
echo.
echo The browser should open automatically at http://localhost:3000
echo.
pause
