@echo off
REM Simple Print Server - Remove from Windows Startup

echo ========================================
echo Simple Print Server - Remove from Startup
echo ========================================
echo.
echo This will remove the print server from Windows startup.
echo.

REM Delete the scheduled task
schtasks /Delete /TN "Simple Print Server" /F >nul 2>&1

if %errorlevel% == 0 (
    echo.
    echo SUCCESS! Print server has been removed from Windows startup.
    echo.
) else (
    echo.
    echo ERROR: Failed to remove scheduled task!
    echo.
    echo The task may not exist, or you may need administrator privileges.
    echo Please right-click and select "Run as administrator"
    echo.
)

pause


