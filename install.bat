@echo off
echo ========================================
echo Simple Print Server - Installation
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/3] Python found:
python --version
echo.

echo [2/3] Installing Python packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install packages!
    echo.
    echo Try running as Administrator or install manually:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Installation complete!
echo.
echo ========================================
echo Next steps:
echo ========================================
echo 1. Start the server: python server.py
echo 2. Open example.html in your browser
echo 3. Connect to your printer and start printing!
echo.
echo ========================================
pause

