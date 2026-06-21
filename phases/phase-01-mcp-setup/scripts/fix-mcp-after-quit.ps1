# Run AFTER fully quitting Cursor (File > Exit). Fixes stale mcp.json API key in Settings UI.
$ErrorActionPreference = "Stop"

$cursor = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
if ($cursor) {
    Write-Host "Closing Cursor..."
    $cursor | Stop-Process -Force
    Start-Sleep -Seconds 3
}

$script = Join-Path $PSScriptRoot "fix-stale-mcp-json.py"
python $script

Write-Host ""
Write-Host "Fixed. Reopen Cursor, then Settings -> Tools & MCP -> Add Custom MCP."
Write-Host "If an old mcp.json tab reopens, choose Don't Save."
