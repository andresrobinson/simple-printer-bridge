@echo off
echo ========================================
echo Starting Simple Print Server...
echo ========================================
echo.
echo Server will start on http://localhost:8888
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

python server.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start server!
    echo.
    echo Make sure:
    echo 1. Python is installed
    echo 2. Dependencies are installed (run install.bat)
    echo 3. Port 8888 is not in use
    echo.
    pause
)

