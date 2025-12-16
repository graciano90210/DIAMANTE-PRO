# Script de despliegue automatizado para Heroku
# Ejecutar: .\deploy_heroku.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  DIAMANTE PRO - Despliegue Heroku" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Heroku CLI está instalado
Write-Host "Verificando Heroku CLI..." -ForegroundColor Yellow
$herokuVersion = heroku --version 2>$null

if (!$herokuVersion) {
    Write-Host "❌ Heroku CLI no está instalado" -ForegroundColor Red
    Write-Host "Descargando e instalando Heroku CLI..." -ForegroundColor Yellow
    
    $installerPath = "$env:TEMP\heroku-installer.exe"
    Invoke-WebRequest -Uri "https://cli-assets.heroku.com/heroku-x64.exe" -OutFile $installerPath
    
    Write-Host "Ejecutando instalador (puede requerir permisos de administrador)..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -Wait -ArgumentList "/S"
    
    Write-Host "✅ Heroku CLI instalado. Por favor, cierra y vuelve a abrir PowerShell" -ForegroundColor Green
    Write-Host "Luego ejecuta este script nuevamente." -ForegroundColor Yellow
    exit
}

Write-Host "✅ Heroku CLI instalado: $herokuVersion" -ForegroundColor Green
Write-Host ""

# Login en Heroku
Write-Host "Iniciando sesión en Heroku..." -ForegroundColor Yellow
Write-Host "Se abrirá tu navegador. Presiona cualquier tecla cuando hayas iniciado sesión..." -ForegroundColor Cyan
heroku login

Write-Host ""
Write-Host "✅ Sesión iniciada" -ForegroundColor Green
Write-Host ""

# Crear aplicación
$appName = Read-Host "Nombre de la aplicación en Heroku (ej: diamante-pro)"
Write-Host "Creando aplicación '$appName'..." -ForegroundColor Yellow

heroku create $appName 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Aplicación creada exitosamente" -ForegroundColor Green
} else {
    Write-Host "⚠️ La aplicación ya existe o hubo un error" -ForegroundColor Yellow
    Write-Host "Continuando con la configuración..." -ForegroundColor Yellow
}

Write-Host ""

# Agregar PostgreSQL
Write-Host "Agregando PostgreSQL..." -ForegroundColor Yellow
heroku addons:create heroku-postgresql:essential-0 -a $appName 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL agregado" -ForegroundColor Green
} else {
    Write-Host "⚠️ PostgreSQL ya existe o hubo un error" -ForegroundColor Yellow
}

Write-Host ""

# Configurar variables de entorno
Write-Host "Configurando variables de entorno..." -ForegroundColor Yellow

$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$jwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

heroku config:set SECRET_KEY="$secretKey" -a $appName
heroku config:set JWT_SECRET_KEY="$jwtSecret" -a $appName

Write-Host "✅ Variables de entorno configuradas" -ForegroundColor Green
Write-Host ""

# Desplegar
Write-Host "Desplegando aplicación..." -ForegroundColor Yellow
Write-Host "(Esto puede tomar varios minutos)" -ForegroundColor Cyan
Write-Host ""

git push heroku main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Aplicación desplegada exitosamente" -ForegroundColor Green
    Write-Host ""
    
    # Abrir aplicación
    Write-Host "¿Deseas abrir la aplicación en el navegador? (S/N)" -ForegroundColor Cyan
    $response = Read-Host
    
    if ($response -eq "S" -or $response -eq "s") {
        heroku open -a $appName
    }
    
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "  DESPLIEGUE COMPLETADO" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "URL de la aplicación: https://$appName.herokuapp.com" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Próximos pasos:" -ForegroundColor Yellow
    Write-Host "1. Crear usuario admin: heroku run python crear_admin.py -a $appName" -ForegroundColor White
    Write-Host "2. Ver logs: heroku logs --tail -a $appName" -ForegroundColor White
    Write-Host "3. Configurar dominio personalizado (diamantepro.me)" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host ""
    Write-Host "❌ Error en el despliegue" -ForegroundColor Red
    Write-Host "Revisa los logs: heroku logs --tail -a $appName" -ForegroundColor Yellow
}
