# start-backend.ps1
# Inicia el API .NET en modo Development (para usar con Electron dev).
# Deja el proceso en primer plano para que puedas ver los logs.
#
# Uso: .\scripts\start-backend.ps1

$ErrorActionPreference = "Stop"

$apiProject = Resolve-Path "$PSScriptRoot\..\..\..\Mobile.Remote.Toolkit.Api\Mobile.Remote.Toolkit\Mobile.Remote.Toolkit.Api.csproj"

Write-Host "[backend] Iniciando API .NET en modo Development..." -ForegroundColor Cyan
Write-Host "[backend] Proyecto: $apiProject" -ForegroundColor DarkGray
Write-Host "[backend] URL: https://localhost:59399" -ForegroundColor DarkGray
Write-Host ""

Push-Location (Split-Path $apiProject)
try {
    dotnet run --project $apiProject --configuration Debug
} finally {
    Pop-Location
}
