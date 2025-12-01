# Simple Print Server - System Tray Startup Script (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Simple Print Server (Tray Mode)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will run in the system tray" -ForegroundColor Yellow
Write-Host "Right-click the tray icon for options" -ForegroundColor Yellow
Write-Host ""
Write-Host "This window will close automatically." -ForegroundColor Yellow
Write-Host "The server will continue running in the tray." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Try to use pythonw.exe (no console window) if available
    $pythonw = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($pythonw) {
        Start-Process -FilePath "pythonw.exe" -ArgumentList "server-tray.py" -WindowStyle Hidden
    } else {
        # Fallback: run python.exe in background
        Start-Process -FilePath "python.exe" -ArgumentList "server-tray.py" -WindowStyle Hidden
    }
    
    # Give it a moment to start
    Start-Sleep -Seconds 2
    Write-Host "Server started! Check the system tray for the icon." -ForegroundColor Green
    Start-Sleep -Seconds 1
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to start server!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "1. Python is installed" -ForegroundColor White
    Write-Host "2. Dependencies are installed (run install.ps1)" -ForegroundColor White
    Write-Host "3. pystray and Pillow are installed: pip install pystray pillow" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
}

