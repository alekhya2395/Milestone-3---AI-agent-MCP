# Install Windows Task Scheduler — weekly Groww review refresh + pulse + publish
# Run as Administrator (optional) from project root:
#   .\phases\phase-05-gmail-orchestration\scripts\install-weekly-scheduler.ps1

param(
    [string]$Day = "Monday",
    [string]$Time = "09:00",
    [int]$Weeks = 10
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$Python = (Get-Command python -ErrorAction Stop).Source
$TaskName = "Groww-Weekly-Pulse"
$LogDir = Join-Path $ProjectRoot "data\processed"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$WorkerArgs = "-m src.worker --weeks $Weeks --publish"
$Action = New-ScheduledTaskAction `
    -Execute $Python `
    -Argument $WorkerArgs `
    -WorkingDirectory $ProjectRoot

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Day -At $Time
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Weekly Groww review fetch, pulse, Google Doc + Gmail draft" `
    -Force | Out-Null

Write-Host "Scheduled task '$TaskName' registered."
Write-Host "  When: Every $Day at $Time"
Write-Host "  Run:  python -m src.worker --weeks $Weeks --publish"
Write-Host "  Cwd:  $ProjectRoot"
Write-Host ""
Write-Host "Test now:  python -m src.worker --weeks $Weeks"
Write-Host "View task: Get-ScheduledTask -TaskName '$TaskName'"
