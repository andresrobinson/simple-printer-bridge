# Simple Print Server - Add to Windows Startup (PowerShell)
# This script adds the server tray to Windows startup using Task Scheduler

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Simple Print Server - Add to Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will add the print server to Windows startup" -ForegroundColor Yellow
Write-Host "so it runs automatically when you log in." -ForegroundColor Yellow
Write-Host ""

# Get the current directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if Python is available
$pythonExe = $null
if (Get-Command pythonw.exe -ErrorAction SilentlyContinue) {
    $pythonExe = "pythonw.exe"
} elseif (Get-Command python.exe -ErrorAction SilentlyContinue) {
    $pythonExe = "python.exe"
} else {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Using Python: $pythonExe" -ForegroundColor Green
Write-Host "Script directory: $scriptDir" -ForegroundColor Green
Write-Host ""

# Check if server-tray.py exists
if (-not (Test-Path "$scriptDir\server-tray.py")) {
    Write-Host "ERROR: server-tray.py not found!" -ForegroundColor Red
    Write-Host "Make sure you're running this script from the print-program directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Creating scheduled task..." -ForegroundColor Yellow
Write-Host ""

# Create a scheduled task that runs on user login
$taskName = "Simple Print Server"
$taskAction = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptDir\server-tray.py`""
$taskTrigger = New-ScheduledTaskTrigger -AtLogOn
$taskPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTrigger -Principal $taskPrincipal -Settings $taskSettings -Force -ErrorAction Stop | Out-Null
    
    Write-Host ""
    Write-Host "SUCCESS! Print server has been added to Windows startup." -ForegroundColor Green
    Write-Host ""
    Write-Host "The server will start automatically when you log in." -ForegroundColor Yellow
    Write-Host "You can manage it from Task Scheduler (taskschd.msc)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To remove from startup, run: remove-from-startup.ps1" -ForegroundColor Yellow
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to create scheduled task!" -ForegroundColor Red
    Write-Host ""
    Write-Host "This script requires administrator privileges." -ForegroundColor Yellow
    Write-Host "Please right-click and select 'Run as administrator'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"


