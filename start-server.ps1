# Simple Print Server - Startup Script (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Simple Print Server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will start on http://localhost:8888" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    python server.py
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to start server!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "1. Python is installed" -ForegroundColor White
    Write-Host "2. Dependencies are installed (run install.ps1)" -ForegroundColor White
    Write-Host "3. Port 8888 is not in use" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
}

