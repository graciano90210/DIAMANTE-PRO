# Script para construir la APK de DiamantePro

# Add Flutter to PATH if not present
if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    if (Test-Path "C:\src\flutter\bin") {
        $env:Path += ";C:\src\flutter\bin"
        Write-Host "Added Flutter to PATH" -ForegroundColor Green
    } else {
        Write-Error "Flutter not found. Please install Flutter."
        exit 1
    }
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Construyendo DiamantePro APK" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Limpiar proyecto
Write-Host "Limpiando proyecto..." -ForegroundColor Yellow
flutter clean

Write-Host ""
Write-Host "Obteniendo dependencias..." -ForegroundColor Yellow
flutter pub get

Write-Host ""
Write-Host "Construyendo APK en modo release..." -ForegroundColor Yellow
flutter build apk --release

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  Verificando resultado..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

$apkPath = "build\app\outputs\flutter-apk\app-release.apk"

if (Test-Path $apkPath) {
    $apk = Get-Item $apkPath
    Write-Host "[OK] APK CREADA EXITOSAMENTE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ubicacion: $($apk.FullName)" -ForegroundColor White
    Write-Host "Tamano: $([math]::Round($apk.Length/1MB,2)) MB" -ForegroundColor White
    Write-Host "Fecha: $($apk.LastWriteTime)" -ForegroundColor White
    Write-Host ""
    Write-Host "Para instalar en tu celular:" -ForegroundColor Cyan
    Write-Host "1. Copia el archivo a tu celular" -ForegroundColor White
    Write-Host "2. Abre el archivo APK en tu celular" -ForegroundColor White
    Write-Host "3. Permite la instalacion de fuentes desconocidas si es necesario" -ForegroundColor White
} else {
    Write-Host "[ERROR] La APK no fue creada" -ForegroundColor Red
    Write-Host ""
    Write-Host "Buscando archivos APK en el directorio build..." -ForegroundColor Yellow
    $apks = Get-ChildItem "build" -Recurse -Filter "*.apk" -ErrorAction SilentlyContinue
    if ($apks) {
        Write-Host "APKs encontradas:" -ForegroundColor Yellow
        $apks | Select-Object Name, FullName, @{Name="Size (MB)";Expression={[math]::Round($_.Length/1MB,2)}} | Format-Table -AutoSize
    } else {
        Write-Host "No se encontraron archivos APK" -ForegroundColor Red
    }
}
