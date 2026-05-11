# check-backend.ps1
# Verifica que las herramientas necesarias existen (adb, scrcpy).
#
# Uso: .\scripts\check-backend.ps1

$ErrorActionPreference = "SilentlyContinue"

$toolsBase = Resolve-Path "$PSScriptRoot\..\..\..\Mobile.Remote.Toolkit.Api\Tools" -ErrorAction SilentlyContinue
if (-not $toolsBase) {
    $toolsBase = "$PSScriptRoot\..\..\..\Mobile.Remote.Toolkit.Api\Tools"
}

$tools = @(
    @{ Name = "adb";    Path = Join-Path $toolsBase "Android\adb\adb.exe" },
    @{ Name = "scrcpy"; Path = Join-Path $toolsBase "Android\scrcpy\scrcpy.exe" }
)

$ok = $true
Write-Host "[check-backend] Verificando herramientas..." -ForegroundColor Cyan
Write-Host "[check-backend] Directorio Tools: $toolsBase" -ForegroundColor DarkGray
Write-Host ""

foreach ($tool in $tools) {
    if (Test-Path $tool.Path) {
        $ver = & $tool.Path --version 2>&1 | Select-Object -First 1
        Write-Host "  OK $($tool.Name): $($tool.Path)" -ForegroundColor Green
        Write-Host "    $ver" -ForegroundColor DarkGray
    } else {
        Write-Host "  ERROR $($tool.Name) NO encontrado: $($tool.Path)" -ForegroundColor Red
        $ok = $false
    }
}

Write-Host ""
if ($ok) {
    Write-Host "[check-backend] OK Todas las herramientas disponibles." -ForegroundColor Green
    exit 0
} else {
    Write-Host "[check-backend] ERROR Faltan herramientas. Copialas al directorio Tools/." -ForegroundColor Red
    exit 1
}
