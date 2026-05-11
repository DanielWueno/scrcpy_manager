# check-api.ps1
# Verifica que el API .NET está respondiendo correctamente.
#
# Uso: .\scripts\check-api.ps1 [-Port 59399] [-MaxAttempts 5]

param(
    [int]$Port = 59399,
    [int]$MaxAttempts = 5,
    [int]$DelaySeconds = 2
)

$ErrorActionPreference = "SilentlyContinue"

$url = "https://localhost:$Port/api/android/devices"

Write-Host "[check-api] Verificando API en: $url" -ForegroundColor Cyan

# Ignorar errores de certificado para dev
Add-Type @"
using System.Net;
using System.Security.Cryptography.X509Certificates;
public class TrustAll : ICertificatePolicy {
    public bool CheckValidationResult(ServicePoint sp, X509Certificate cert,
        WebRequest req, int problem) { return true; }
}
"@ -ErrorAction SilentlyContinue
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAll -ErrorAction SilentlyContinue

for ($i = 1; $i -le $MaxAttempts; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3 -SkipCertificateCheck 2>$null
        if ($resp.StatusCode -lt 500) {
            Write-Host "[check-api] OK API OK (HTTP $($resp.StatusCode)) - Intento $i/$MaxAttempts" -ForegroundColor Green
            exit 0
        }
    } catch {
        $msg = $_.Exception.Message
    }
    Write-Host "[check-api] Intento $i/$MaxAttempts fallido. Reintentando en ${DelaySeconds}s..." -ForegroundColor Yellow
    if ($i -lt $MaxAttempts) { Start-Sleep -Seconds $DelaySeconds }
}

Write-Host "[check-api] ERROR API no disponible en https://localhost:$Port" -ForegroundColor Red
Write-Host "[check-api]   Ejecuta: .\scripts\start-backend.ps1" -ForegroundColor DarkGray
exit 1
