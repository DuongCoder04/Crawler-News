@echo off
REM X-Wise News Crawler - Startup Script for Windows

echo ============================================================
echo X-Wise News Crawler - Starting...
echo ============================================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Check database connection
echo.
echo Checking database connection...
python test_setup.py

if errorlevel 1 (
    echo Database connection failed. Please check .env configuration.
    pause
    exit /b 1
)

echo.
echo Database connection OK
echo.
echo ============================================================
echo Starting crawler in SCHEDULER mode...
echo ============================================================
echo.
echo Crawler will run automatically based on schedule:
echo    - VnExpress: Every 2 hours
echo    - Blockchain sources: Every 3 hours
echo.
echo Press Ctrl+C to stop
echo.

REM Start crawler in scheduler mode
python main.py --mode scheduler

pause
