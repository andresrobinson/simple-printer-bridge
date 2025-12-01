# Simple Print Server - System Tray Dependencies Installation (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing System Tray Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will install pystray and Pillow for system tray mode" -ForegroundColor Yellow
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

Write-Host ""
Write-Host "Installing system tray dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
Write-Host ""

# Step 1: Try installing Pillow with pre-built wheels (recommended)
Write-Host "Step 1: Installing Pillow with pre-built wheels..." -ForegroundColor Cyan
python -m pip install --only-binary :all: Pillow

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Pre-built wheel not available, trying specific version..." -ForegroundColor Yellow
    python -m pip install Pillow==10.4.0
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Trying latest Pillow from source..." -ForegroundColor Yellow
    python -m pip install Pillow
}

# Step 2: Install pystray
Write-Host ""
Write-Host "Step 2: Installing pystray..." -ForegroundColor Cyan
python -m pip install pystray

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Cyan
$verify = python -c "import pystray; import PIL; print('SUCCESS')" 2>&1

if ($LASTEXITCODE -ne 0 -or $verify -notmatch "SUCCESS") {
    Write-Host ""
    Write-Host "WARNING: Installation had issues, but checking if it works..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can still use the server in console mode (start-server.ps1)" -ForegroundColor Yellow
    Write-Host "Console mode works perfectly - tray mode is just a convenience feature." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "See TROUBLESHOOTING.md for more help." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "You can now use start-server-tray.ps1 to run in system tray mode." -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"

