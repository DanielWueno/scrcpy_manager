# Backend API Status Check
Write-Host "Checking backend API status..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/devices" -Method GET -TimeoutSec 5
    Write-Host "SUCCESS: Backend API is running!" -ForegroundColor Green
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Backend API is not available" -ForegroundColor Red
    Write-Host "Please start your backend server on port 5000" -ForegroundColor Yellow
}
