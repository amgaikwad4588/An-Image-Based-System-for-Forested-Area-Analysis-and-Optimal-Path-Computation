@echo off
echo.
echo ========================================
echo    EcoView Imaging - Starting Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Please reinstall Python with pip included
    echo.
    pause
    exit /b 1
)

echo ✓ pip found
echo.

REM Install/upgrade dependencies
echo Installing Python dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    echo.
    pause
    exit /b 1
)

echo ✓ Dependencies installed
echo.

REM Check if treesense directory exists
if not exist "treesense" (
    echo ERROR: treesense directory not found
    echo Please make sure you're running this from the project root directory
    echo.
    pause
    exit /b 1
)

echo ✓ Web files found
echo.

REM Start the API server in background
echo Starting API server...
start /B python PythonScripts\unified_api.py
timeout /t 3 /nobreak >nul

REM Start the web server
echo Starting web server...
echo.
echo ========================================
echo    EcoView Imaging is now running! 
echo ========================================
echo.
echo API Server: http://localhost:8000
echo Web Interface: http://localhost:3000
echo.
echo Press Ctrl+C to stop the servers
echo.

REM Change to treesense directory and start HTTP server
cd /d treesense
if %errorlevel% neq 0 (
    echo ERROR: Could not change to treesense directory
    echo Please check the directory structure
    echo.
    pause
    exit /b 1
)

REM Start Python HTTP server
python -m http.server 3000
if %errorlevel% neq 0 (
    echo ERROR: Failed to start web server
    echo Please check if port 3000 is available
    echo Try running: netstat -ano ^| findstr :3000
    echo.
    pause
    exit /b 1
)
