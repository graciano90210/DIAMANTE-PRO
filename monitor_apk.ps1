# Script para monitorear la creación de la APK

$apkPath = "build\app\outputs\flutter-apk\app-release.apk"
$maxWaitMinutes = 15
$checkIntervalSeconds = 10
$elapsed = 0

Write-Host "Monitoreando creación de APK..." -ForegroundColor Cyan
Write-Host "Ubicación esperada: $apkPath" -ForegroundColor Gray
Write-Host ""

while ($elapsed -lt ($maxWaitMinutes * 60)) {
    if (Test-Path $apkPath) {
        $apk = Get-Item $apkPath
        Write-Host ""
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host "  ✓ APK CREADA EXITOSAMENTE!" -ForegroundColor Green
        Write-Host "=====================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Ubicación: $($apk.FullName)" -ForegroundColor White
        Write-Host "Tamaño: $([math]::Round($apk.Length/1MB,2)) MB" -ForegroundColor White
        Write-Host "Fecha: $($apk.LastWriteTime)" -ForegroundColor White
        Write-Host ""
        Write-Host "Para instalar en tu celular:" -ForegroundColor Cyan
        Write-Host "1. Conecta tu celular por USB" -ForegroundColor White
        Write-Host "2. Ejecuta: flutter install" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "O copia el archivo APK a tu celular y ábrelo" -ForegroundColor White
        exit 0
    }
    
    $progress = [math]::Round(($elapsed / ($maxWaitMinutes * 60)) * 100, 0)
    Write-Host "`r[$(Get-Date -Format 'HH:mm:ss')] Esperando... $elapsed seg ($progress%) " -NoNewline -ForegroundColor Yellow
    Start-Sleep -Seconds $checkIntervalSeconds
    $elapsed += $checkIntervalSeconds
}

Write-Host ""
Write-Host ""
Write-Host "Tiempo de espera agotado. La APK no fue creada en $maxWaitMinutes minutos." -ForegroundColor Red
Write-Host "Verifica si hay errores en la compilación." -ForegroundColor Yellow
