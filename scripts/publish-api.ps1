# publish-api.ps1
# Publishes the .NET API as a self-contained Windows x64 executable.
# Run this before pnpm electron:dist to bundle the API alongside the Electron app.
#
# Usage: .\publish-api.ps1

$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
$apiProject = Resolve-Path "$root\..\Mobile.Remote.Toolkit.Api\Mobile.Remote.Toolkit\Mobile.Remote.Toolkit.Api.csproj"
$publishOut = Resolve-Path "$root\..\Mobile.Remote.Toolkit.Api\publish" -ErrorAction SilentlyContinue
if (-not $publishOut) {
    $publishOut = "$root\..\Mobile.Remote.Toolkit.Api\publish"
}

Write-Host "[publish] Publishing .NET API to: $publishOut" -ForegroundColor Cyan

dotnet publish $apiProject `
    --configuration Release `
    --runtime win-x64 `
    --self-contained true `
    --output $publishOut `
    /p:PublishSingleFile=false `
    /p:UseAppHost=true

if ($LASTEXITCODE -ne 0) {
    Write-Error "dotnet publish failed with exit code $LASTEXITCODE"
    exit 1
}

Write-Host "[publish] Done. Output: $publishOut" -ForegroundColor Green
Write-Host ""
Write-Host "Next step: pnpm electron:dist" -ForegroundColor Yellow
