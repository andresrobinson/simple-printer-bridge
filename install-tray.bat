@echo off
echo ========================================
echo Installing System Tray Dependencies
echo ========================================
echo.
echo This will install pystray and Pillow for system tray mode
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    pause
    exit /b 1
)

echo Installing system tray dependencies...
echo This may take a few minutes...
echo.
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

echo.
echo Step 1: Attempting to install with pre-built wheels (recommended)...
python -m pip install --only-binary :all: Pillow

if errorlevel 1 (
    echo.
    echo Pre-built Pillow wheel not available, trying specific version...
    python -m pip install Pillow==10.4.0
)

if errorlevel 1 (
    echo.
    echo Pillow installation failed. Trying latest version from source...
    python -m pip install Pillow
)

echo.
echo Step 2: Installing pystray...
python -m pip install pystray

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install pystray!
    goto :error
)

:error
if errorlevel 1 (
    echo.
    echo ========================================
    echo Installation had issues, but checking...
    echo ========================================
    echo.
    python -c "import pystray; import PIL; print('SUCCESS: Dependencies are installed!')" 2>nul
    if errorlevel 1 (
        echo.
        echo ERROR: System tray dependencies not fully installed.
        echo.
        echo You can still use the server in console mode (start-server.bat)
        echo Console mode works perfectly - tray mode is just a convenience feature.
        echo.
        echo See TROUBLESHOOTING.md for more help.
        echo.
        pause
        exit /b 1
    ) else (
        echo Installation successful despite warnings!
        goto :success
    )
) else (
    :success
    echo.
    echo ========================================
    echo Installation complete!
    echo ========================================
    echo You can now use start-server-tray.bat to run in system tray mode.
    echo.
)

echo.
echo Installation complete!
echo You can now use start-server-tray.bat to run in system tray mode.
echo.
pause

