@echo off
echo ================================
echo   DIAMANTE PRO - Despliegue
echo ================================
echo.

echo Paso 1: Creando aplicacion en Heroku...
heroku create diamante-pro

echo.
echo Paso 2: Agregando PostgreSQL...
heroku addons:create heroku-postgresql:essential-0 -a diamante-pro

echo.
echo Paso 3: Configurando variables de entorno...
heroku config:set SECRET_KEY=diamante-secret-2025-production -a diamante-pro
heroku config:set JWT_SECRET_KEY=jwt-secret-2025-mobile-app -a diamante-pro

echo.
echo Paso 4: Desplegando codigo...
git push heroku main

echo.
echo Paso 5: Creando usuario admin...
heroku run python crear_admin.py -a diamante-pro

echo.
echo ================================
echo   DESPLIEGUE COMPLETADO
echo ================================
echo.
echo Tu aplicacion esta en: https://diamante-pro.herokuapp.com
echo.
pause
