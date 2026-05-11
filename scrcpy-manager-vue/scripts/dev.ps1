# dev.ps1
# Inicia el entorno de desarrollo completo:
#   - API .NET en una ventana separada
#   - Electron (con Vite dev server) en la ventana actual
#
# Uso: .\scripts\dev.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent

# Verificar herramientas antes de arrancar
Write-Host "[dev] Verificando herramientas..." -ForegroundColor Cyan
& "$PSScriptRoot\check-backend.ps1"
if ($LASTEXITCODE -ne 0) { exit 1 }

# Lanzar API .NET en ventana separada
Write-Host "[dev] Iniciando API .NET en background..." -ForegroundColor Cyan
$apiProject = Resolve-Path "$root\..\..\Mobile.Remote.Toolkit.Api\Mobile.Remote.Toolkit\Mobile.Remote.Toolkit.Api.csproj"
$apiDir     = Split-Path $apiProject

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$apiDir'; dotnet run --project '$apiProject' --configuration Debug"
) -WindowStyle Normal

# Esperar a que el API esté lista
Write-Host "[dev] Esperando que el API esté lista..." -ForegroundColor Yellow
& "$PSScriptRoot\check-api.ps1" -MaxAttempts 15 -DelaySeconds 2
if ($LASTEXITCODE -ne 0) {
    Write-Host "[dev] ERROR: El API no respondio. Revisa la ventana del backend." -ForegroundColor Red
    exit 1
}

# Iniciar Electron dev
Write-Host "[dev] Iniciando Electron..." -ForegroundColor Cyan
Set-Location $root
& ".\node_modules\.bin\electron-vite.cmd" dev
