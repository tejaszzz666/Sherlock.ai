@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Sherlock.ai - System Check
echo ========================================
echo.

set "errors=0"

:: Check if we're in the right directory
if not exist "frontend" (
    echo [ERROR] frontend folder not found!
    echo Please run this from D:\Sherlock.ai\
    set /a errors+=1
) else (
    echo [OK] Frontend folder found
)

if not exist "backend" (
    echo [ERROR] backend folder not found!
    set /a errors+=1
) else (
    echo [OK] Backend folder found
)

echo.
echo Checking Frontend Configuration...
echo.

:: Check tsconfig.json
if not exist "frontend\tsconfig.json" (
    echo [ERROR] tsconfig.json missing!
    set /a errors+=1
) else (
    echo [OK] tsconfig.json exists
)

:: Check tsconfig.node.json
if not exist "frontend\tsconfig.node.json" (
    echo [ERROR] tsconfig.node.json missing!
    set /a errors+=1
) else (
    echo [OK] tsconfig.node.json exists
)

:: Check package.json
if not exist "frontend\package.json" (
    echo [ERROR] package.json missing!
    set /a errors+=1
) else (
    echo [OK] package.json exists
)

:: Check main files
if not exist "frontend\src\main.tsx" (
    echo [ERROR] src\main.tsx missing!
    set /a errors+=1
) else (
    echo [OK] main.tsx exists
)

if not exist "frontend\src\App.tsx" (
    echo [ERROR] src\App.tsx missing!
    set /a errors+=1
) else (
    echo [OK] App.tsx exists
)

if not exist "frontend\src\index.css" (
    echo [ERROR] src\index.css missing!
    set /a errors+=1
) else (
    echo [OK] index.css exists
)

:: Check node_modules
if not exist "frontend\node_modules" (
    echo [WARNING] node_modules folder not found!
    echo You need to run: npm install
    set /a errors+=1
) else (
    echo [OK] node_modules folder exists
)

echo.
echo Checking Backend Files...
echo.

if not exist "backend\app.py" (
    echo [ERROR] backend\app.py missing!
    set /a errors+=1
) else (
    echo [OK] app.py exists
)

echo.
echo ========================================
echo Check Complete
echo ========================================
echo.

if %errors% equ 0 (
    echo [SUCCESS] All checks passed! ✓
    echo.
    echo You can now run:
    echo   1. Backend: cd backend ^&^& python app.py
    echo   2. Frontend: cd frontend ^&^& npm run dev
) else (
    echo [WARNING] Found %errors% issue(s)!
    echo.
    echo Please fix the issues above before starting the application.
    echo.
    echo Quick fixes:
    echo   - Missing node_modules? Run: cd frontend ^&^& npm install
    echo   - Missing config files? The tsconfig files should have been created.
)

echo.
pause
