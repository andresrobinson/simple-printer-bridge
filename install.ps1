# Simple Print Server - Installation Script (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Simple Print Server - Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/3] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Upgrade pip
Write-Host "[2/3] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Failed to upgrade pip, continuing anyway..." -ForegroundColor Yellow
}

Write-Host ""

# Install requirements
Write-Host "[2/3] Installing Python packages..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to install packages!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running as Administrator or install manually:" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[3/3] Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Start the server: python server.py" -ForegroundColor White
Write-Host "2. Open example.html in your browser" -ForegroundColor White
Write-Host "3. Connect to your printer and start printing!" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"

