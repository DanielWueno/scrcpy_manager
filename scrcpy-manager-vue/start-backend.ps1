# Script para iniciar el backend API

Write-Host "Iniciando Scrcpy Backend API..." -ForegroundColor Cyan

# Cambiar al directorio del backend
$backendPath = "C:\Users\DSOFT03.CORP\Documents\Soft\scrcpy_manager"
Set-Location $backendPath

Write-Host " Directorio: $backendPath" -ForegroundColor Yellow

# Verificar que existe el archivo
if (Test-Path "api\server.py") {
    Write-Host " Archivo server.py encontrado" -ForegroundColor Green
    
    # Intentar ejecutar el servidor
    Write-Host " Iniciando servidor Flask en puerto 5000..." -ForegroundColor Yellow
    
    # Ejecutar en el directorio correcto
    Set-Location $backendPath
    python "api\server.py"
} else {
    Write-Host " No se encontró el archivo api\server.py" -ForegroundColor Red
}
