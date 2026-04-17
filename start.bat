@echo off
chcp 65001 >nul

echo ================================
echo China University Admission System
echo ================================
echo.

echo Checking environment...
cmd /c "node --version" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found, please install Node.js 18+
    pause
    exit /b 1
)

echo OK: Node.js installed
echo.

echo Checking dependencies...
if not exist "backend\node_modules" (
    echo WARNING: Backend dependencies not installed, installing...
    cmd /c "cd backend && npm install"
) else (
    echo OK: Backend dependencies installed
)

if not exist "frontend\node_modules" (
    echo WARNING: Frontend dependencies not installed, installing...
    cmd /c "cd frontend && npm install"
) else (
    echo OK: Frontend dependencies installed
)

echo.
echo Starting development servers...
echo.
echo Starting backend API server...
start "Backend Server" cmd /k "cd /d backend && npm run dev"

timeout /t 3 /nobreak >nul

echo Starting frontend development server...
start "Frontend Server" cmd /k "cd /d frontend && npm run dev"

timeout /t 2 /nobreak >nul

echo.
echo ================================
echo Server started successfully!
echo.
echo Backend API: http://localhost:3000
echo API Documentation: http://localhost:3000/api
echo Frontend App: http://localhost:5173
echo Health Check: http://localhost:3000/health
echo.
echo Tips:
echo - Keep both command windows open
echo - Press Ctrl+C to stop servers
echo - Visit the URLs above to use the system
echo ================================
echo.

pause
