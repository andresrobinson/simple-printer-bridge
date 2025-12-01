@echo off
echo ========================================
echo Starting Simple Print Server (Tray Mode)
echo ========================================
echo.
echo Server will run in the system tray
echo Right-click the tray icon for options
echo.
echo This window will close automatically.
echo The server will continue running in the tray.
echo.
echo ========================================
echo.

REM Try to use pythonw.exe (no console window) if available
where pythonw.exe >nul 2>&1
if %errorlevel% == 0 (
    start "" pythonw.exe server-tray.py
    timeout /t 2 /nobreak >nul
    exit
)

REM Fallback to python.exe but run detached
start "" /B python server-tray.py

REM Give it a moment to start, then close this window
timeout /t 2 /nobreak >nul
exit

