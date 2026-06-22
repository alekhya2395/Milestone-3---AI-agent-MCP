# Reset ALL MCP servers — run with Cursor fully quit (File > Exit)
$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
Set-Location $ProjectRoot

$cursor = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
if ($cursor) {
    Write-Host "ERROR: Quit Cursor completely first (File > Exit), then re-run:" -ForegroundColor Red
    Write-Host "  .\phases\phase-01-mcp-setup\scripts\reset-all-mcp.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "=== 1/4 Sync Windows environment from .env ===" -ForegroundColor Cyan
python "$PSScriptRoot\sync-mcp-env.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== 2/4 Write local mcp.json (literal credentials) ===" -ForegroundColor Cyan
python "$PSScriptRoot\apply-local-mcp-config.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n=== 3/4 Clear stale MCP OAuth cache ===" -ForegroundColor Cyan
python "$PSScriptRoot\clear-cursor-mcp-state.py"

Write-Host "`n=== 4/4 Verify config ===" -ForegroundColor Cyan
python "$PSScriptRoot\verify-mcp-config.py"

Write-Host "`n=== DONE ===" -ForegroundColor Green
Write-Host "1. Reopen Cursor"
Write-Host "2. Settings -> Tools & MCP"
Write-Host "3. Toggle ON: weekly-pulse, alphavantage, google-drive, google-gmail"
Write-Host "4. google-drive + google-gmail: Connect and sign in with Google"
Write-Host "5. Test: python phases/phase-01-mcp-setup/scripts/project-status.py"
