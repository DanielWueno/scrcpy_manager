# Scrcpy Backend API Check

Write-Host "🔍 Verificando estado del backend API..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/devices" -Method GET -TimeoutSec 5
    Write-Host "✅ Backend API está funcionando correctamente!" -ForegroundColor Green
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend API no está disponible" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🛠️  Para solucionarlo:" -ForegroundColor Yellow
    Write-Host "1. Asegúrate de tener el servidor backend corriendo" -ForegroundColor White
    Write-Host "2. El servidor debe estar disponible en http://127.0.0.1:5000" -ForegroundColor White
    Write-Host "3. Verifica que no hay firewall bloqueando el puerto 5000" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Si no tienes el backend, necesitas:" -ForegroundColor Yellow
    Write-Host "- Un servidor Python/Flask/FastAPI corriendo en puerto 5000" -ForegroundColor White
    Write-Host "- Que exponga los endpoints de la API para gestión de dispositivos" -ForegroundColor White
}
