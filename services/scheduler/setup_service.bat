@echo off
echo Setting up Active Time Scheduler...
echo -----------------------------------
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install requirements. Check if pip is installed.
    pause
    exit /b %ERRORLEVEL%
)
echo [SUCCESS] Dependencies installed!
echo -----------------------------------
echo To start the service, run: python active_time_sync.py
echo -----------------------------------
pause
