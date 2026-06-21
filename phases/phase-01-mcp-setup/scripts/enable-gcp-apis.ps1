# Enable Google Workspace + MCP APIs (Windows)
# Usage: .\enable-gcp-apis.ps1 -ProjectId YOUR_PROJECT_ID

param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId
)

$ErrorActionPreference = "Stop"

Write-Host "Enabling Workspace APIs on project: $ProjectId"

gcloud services enable `
    gmail.googleapis.com `
    drive.googleapis.com `
    --project=$ProjectId

Write-Host "Enabling MCP services..."

gcloud services enable `
    gmailmcp.googleapis.com `
    drivemcp.googleapis.com `
    --project=$ProjectId

Write-Host "Done. Verify in Cloud Console: APIs & Services > Enabled APIs"
