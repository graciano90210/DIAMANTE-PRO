# Paso 1: Instalar Heroku CLI
# Ejecutar como Administrador: Clic derecho > Ejecutar como administrador

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Instalando Heroku CLI" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si ya está instalado
$herokuPath = "C:\Program Files\heroku\bin\heroku.cmd"

if (Test-Path $herokuPath) {
    Write-Host "✅ Heroku CLI ya está instalado" -ForegroundColor Green
    & $herokuPath --version
    Write-Host ""
    Write-Host "Ahora ejecuta el script de despliegue:" -ForegroundColor Yellow
    Write-Host ".\deploy_heroku.ps1" -ForegroundColor Cyan
    exit
}

Write-Host "Descargando Heroku CLI..." -ForegroundColor Yellow
$installerPath = "$env:TEMP\heroku-installer.exe"

try {
    Invoke-WebRequest -Uri "https://cli-assets.heroku.com/heroku-x64.exe" -OutFile $installerPath -ErrorAction Stop
    Write-Host "✅ Descarga completada" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al descargar: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Instalando Heroku CLI..." -ForegroundColor Yellow
Write-Host "(Esto puede tomar unos minutos)" -ForegroundColor Cyan

try {
    Start-Process -FilePath $installerPath -Wait -ErrorAction Stop
    Write-Host "✅ Instalación completada" -ForegroundColor Green
} catch {
    Write-Host "❌ Error en la instalación: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Verificando instalación..." -ForegroundColor Yellow

# Recargar variables de entorno
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

if (Test-Path $herokuPath) {
    Write-Host "✅ Heroku CLI instalado correctamente" -ForegroundColor Green
    & $herokuPath --version
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "  INSTALACIÓN COMPLETADA" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "CIERRA Y VUELVE A ABRIR PowerShell" -ForegroundColor Yellow
    Write-Host "Luego ejecuta: .\deploy_heroku.ps1" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "⚠️ Instalación completada pero heroku no se encuentra en el PATH" -ForegroundColor Yellow
    Write-Host "Por favor, cierra y vuelve a abrir PowerShell" -ForegroundColor Yellow
}
