# build-dist.ps1
# Build completo para distribución:
#   1. Publica el API .NET como self-contained win-x64
#   2. Compila el proyecto Electron (Vue + main + preload)
#   3. Empaqueta con electron-builder -> instalador NSIS en dist-electron/
#
# Uso: .\scripts\build-dist.ps1 [--skip-api] [--skip-build]
#
# Flags:
#   --skip-api    Omite el dotnet publish (usa el publish anterior)
#   --skip-build  Omite el electron-vite build (usa el out/ anterior)

param(
    [switch]$SkipApi,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Mobile Remote Toolkit - Build Dist     " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Publicar API .NET
if (-not $SkipApi) {
    Write-Host "[1/3] Publicando API .NET (self-contained win-x64)..." -ForegroundColor Yellow
    & "$PSScriptRoot\publish-api.ps1"
    if ($LASTEXITCODE -ne 0) { Write-Error "publish-api fallo"; exit 1 }
} else {
    Write-Host "[1/3] Omitiendo publish API (--skip-api)" -ForegroundColor DarkGray
}

# Verificar que el publish existe
$publishDir = Resolve-Path "$root\..\Mobile.Remote.Toolkit.Api\publish" -ErrorAction SilentlyContinue
if (-not $publishDir) {
    Write-Error "No se encontró el directorio publish del API. Ejecuta sin --skip-api primero."
    exit 1
}

# Paso 2: Build Electron
if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "[2/3] Compilando Electron (Vue + main + preload)..." -ForegroundColor Yellow
    Set-Location $root
    & ".\node_modules\.bin\electron-vite.cmd" build
    # exit code 1 por warnings de Sass es esperado; verificamos que out/ exista
    if (-not (Test-Path "out\main\index.js")) {
        Write-Error "electron-vite build fallo; out/main/index.js no encontrado"
        exit 1
    }
    Write-Host "[2/3] OK Build Electron completado." -ForegroundColor Green
} else {
    Write-Host "[2/3] Omitiendo electron-vite build (--skip-build)" -ForegroundColor DarkGray
}

# Paso 3: Empaquetar con electron-builder
Write-Host ""
Write-Host "[3/3] Empaquetando instalador con electron-builder..." -ForegroundColor Yellow
Set-Location $root

$distDir = Join-Path $root "dist-electron-test"
$unpackedDir = Join-Path $distDir "win-unpacked"
$builderOutputDir = $distDir

# Evitar bloqueos del ejecutable previo (error Access is denied)
Write-Host "[3/3] Cerrando procesos previos de Mobile Remote Toolkit (si existen)..." -ForegroundColor DarkGray
try {
    Get-Process -Name "Mobile Remote Toolkit" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
} catch {
    # No-op: si no existe el proceso, continuamos.
}

# Limpiar carpeta de salida previa con reintentos en caso de locks temporales
if (Test-Path $unpackedDir) {
    $cleaned = $false
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            Remove-Item $unpackedDir -Recurse -Force -ErrorAction Stop
            $cleaned = $true
            Write-Host "[3/3] Limpieza de win-unpacked completada." -ForegroundColor DarkGray
            break
        }
        catch {
            Write-Host "[3/3] No se pudo limpiar win-unpacked (intento $attempt/5)." -ForegroundColor Yellow
            if ($attempt -eq 5) { break }
            Start-Sleep -Milliseconds 800
        }
    }

    if (-not $cleaned) {
        $builderOutputDir = Join-Path $root ("dist-electron-test-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
        Write-Host "[3/3] Carpeta previa bloqueada. Se usará salida alternativa: $builderOutputDir" -ForegroundColor Yellow
    }
}

$env:NODE_ENV = "production"
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"
Remove-Item Env:npm_config_user_agent -ErrorAction SilentlyContinue
Remove-Item Env:npm_execpath -ErrorAction SilentlyContinue
& ".\node_modules\.bin\electron-builder.cmd" --win --x64 "--config.directories.output=$builderOutputDir"

if ($LASTEXITCODE -ne 0) {
    Write-Error "electron-builder fallo con codigo $LASTEXITCODE"
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "   OK Distribucion generada correctamente " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Archivos generados en: $builderOutputDir" -ForegroundColor Cyan
Get-ChildItem $builderOutputDir -Filter "*.exe" | ForEach-Object {
    Write-Host "  -> $($_.Name)  ($([math]::Round($_.Length / 1MB, 1)) MB)" -ForegroundColor White
}
Write-Host ""
