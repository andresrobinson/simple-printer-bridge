# Simple Print Server - Remove from Windows Startup (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Simple Print Server - Remove from Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will remove the print server from Windows startup." -ForegroundColor Yellow
Write-Host ""

$taskName = "Simple Print Server"

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction Stop | Out-Null
    
    Write-Host ""
    Write-Host "SUCCESS! Print server has been removed from Windows startup." -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to remove scheduled task!" -ForegroundColor Red
    Write-Host ""
    Write-Host "The task may not exist, or you may need administrator privileges." -ForegroundColor Yellow
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"


