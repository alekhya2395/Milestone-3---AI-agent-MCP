# Load GOOGLE_OAUTH_* from project .env into Windows user environment variables.
# Cursor reads ${env:...} from system/user env - not from .env automatically.
# Run once, then fully quit and reopen Cursor.

$ErrorActionPreference = "Stop"

$envFile = Join-Path $PSScriptRoot "..\..\..\.env"
if (-not (Test-Path $envFile)) {
    Write-Error ".env not found at $envFile. Run import-credentials-to-env.py first."
}

$vars = @{}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line -match "^([^=]+)=(.*)$") {
        $vars[$Matches[1]] = $Matches[2]
    }
}

foreach ($name in @("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_CLOUD_PROJECT_ID")) {
    if (-not $vars[$name]) {
        Write-Warning "Skipping $name - not set in .env"
        continue
    }
    [System.Environment]::SetEnvironmentVariable($name, $vars[$name], "User")
    Write-Host "Set user env: $name"
}

Write-Host ""
Write-Host "Done. Fully quit Cursor, then reopen this project."
