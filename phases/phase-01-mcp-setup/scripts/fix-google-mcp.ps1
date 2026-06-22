# Fix Google MCP connection errors in Cursor
# IMPORTANT: Fully quit Cursor first (File > Exit), then run this script.

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
Set-Location $ProjectRoot

$cursor = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
if ($cursor) {
    Write-Host "ERROR: Close Cursor completely first (File > Exit), then re-run:" -ForegroundColor Red
    Write-Host "  .\phases\phase-01-mcp-setup\scripts\fix-google-mcp.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "=== Step 1: Sync .env OAuth vars to Windows User environment ===" -ForegroundColor Cyan
python "$PSScriptRoot\sync-mcp-env.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== Step 2: Clear stale Google MCP OAuth cache ===" -ForegroundColor Cyan
python "$PSScriptRoot\clear-cursor-mcp-state.py"

Write-Host "`n=== Step 3: Verify mcp.json ===" -ForegroundColor Cyan
python "$PSScriptRoot\verify-mcp-config.py"

Write-Host "`n=== DONE ===" -ForegroundColor Green
Write-Host "1. Reopen Cursor"
Write-Host "2. Settings -> Tools & MCP"
Write-Host "3. Toggle weekly-pulse ON"
Write-Host "4. google-drive + google-gmail: Connect and complete Google sign-in"
Write-Host "5. Test in chat: Using google-drive MCP, list_recent_files"
