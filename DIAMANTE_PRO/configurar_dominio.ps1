# Script para configurar dominio personalizado diamantepro.me
# Ejecutar después del despliegue: .\configurar_dominio.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Configurar Dominio Personalizado" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$appName = Read-Host "Nombre de tu aplicación en Heroku (ej: diamante-pro)"

Write-Host ""
Write-Host "Agregando dominios a Heroku..." -ForegroundColor Yellow

# Agregar dominios
heroku domains:add diamantepro.me -a $appName
heroku domains:add www.diamantepro.me -a $appName

Write-Host ""
Write-Host "✅ Dominios agregados" -ForegroundColor Green
Write-Host ""

# Mostrar información DNS
Write-Host "Obtener información DNS..." -ForegroundColor Yellow
$dnsInfo = heroku domains -a $appName

Write-Host ""
Write-Host "================================" -ForegroundColor Yellow
Write-Host "  CONFIGURACIÓN DNS EN NAMECHEAP" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ve a Namecheap > diamantepro.me > Advanced DNS" -ForegroundColor Cyan
Write-Host ""
Write-Host "Agrega estos registros:" -ForegroundColor White
Write-Host ""
Write-Host "Tipo: CNAME" -ForegroundColor Green
Write-Host "Host: www" -ForegroundColor Green
Write-Host "Valor: $appName.herokuapp.com" -ForegroundColor Green
Write-Host "TTL: Automatic" -ForegroundColor Green
Write-Host ""
Write-Host "Tipo: ALIAS o ANAME (si está disponible) o CNAME" -ForegroundColor Green
Write-Host "Host: @" -ForegroundColor Green
Write-Host "Valor: $appName.herokuapp.com" -ForegroundColor Green
Write-Host "TTL: Automatic" -ForegroundColor Green
Write-Host ""

# Habilitar SSL
Write-Host "Habilitando SSL automático..." -ForegroundColor Yellow
heroku certs:auto:enable -a $appName

Write-Host ""
Write-Host "✅ SSL habilitado" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ La propagación DNS puede tardar 5-30 minutos" -ForegroundColor Yellow
Write-Host ""
Write-Host "Puedes verificar el estado con:" -ForegroundColor Cyan
Write-Host "heroku domains -a $appName" -ForegroundColor White
Write-Host ""
Write-Host "Una vez propagado, tu sitio estará disponible en:" -ForegroundColor Green
Write-Host "https://diamantepro.me" -ForegroundColor Cyan
Write-Host "https://www.diamantepro.me" -ForegroundColor Cyan
Write-Host ""
