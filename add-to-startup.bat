@echo off
REM Simple Print Server - Add to Windows Startup
REM This script adds the server tray to Windows startup using Task Scheduler

echo ========================================
echo Simple Print Server - Add to Startup
echo ========================================
echo.
echo This will add the print server to Windows startup
echo so it runs automatically when you log in.
echo.

REM Get the current directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Check if Python is available
where pythonw.exe >nul 2>&1
if %errorlevel% == 0 (
    set "PYTHON_EXE=pythonw.exe"
) else (
    where python.exe >nul 2>&1
    if %errorlevel% == 0 (
        set "PYTHON_EXE=python.exe"
    ) else (
        echo ERROR: Python not found!
        echo Please install Python first.
        pause
        exit /b 1
    )
)

echo Using Python: %PYTHON_EXE%
echo Script directory: %SCRIPT_DIR%
echo.

REM Check if server-tray.py exists
if not exist "%SCRIPT_DIR%\server-tray.py" (
    echo ERROR: server-tray.py not found!
    echo Make sure you're running this script from the print-program directory.
    pause
    exit /b 1
)

echo Creating scheduled task...
echo.

REM Create a scheduled task that runs on user login
schtasks /Create /TN "Simple Print Server" /TR "\"%PYTHON_EXE%\" \"%SCRIPT_DIR%\server-tray.py\"" /SC ONLOGON /RL HIGHEST /F >nul 2>&1

if %errorlevel% == 0 (
    echo.
    echo SUCCESS! Print server has been added to Windows startup.
    echo.
    echo The server will start automatically when you log in.
    echo You can manage it from Task Scheduler (taskschd.msc)
    echo.
    echo To remove from startup, run: remove-from-startup.bat
    echo.
) else (
    echo.
    echo ERROR: Failed to create scheduled task!
    echo.
    echo This script requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    echo.
)

pause


