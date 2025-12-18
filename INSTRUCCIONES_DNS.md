# 🌐 Configuración DNS para diamantepro.me

## 📍 Estado Actual
Veo que ya tienes registros CNAME configurados en Namecheap, pero están apuntando a valores incorrectos (cellular-forest y whispering-wombat).

## ✅ Configuración Correcta

### Paso 1: Eliminar registros actuales
En la sección **HOST RECORDS** de Namecheap Advanced DNS, elimina estos registros:
- ❌ CNAME @ → cellular-forest-19c9kiz26hrmf9pgplve5icr.herokuapp.com
- ❌ CNAME www → whispering-wombat-bkf0s782fb4hudxo0rpak6e0.herokuapp.com

### Paso 2: Agregar registros correctos

Agrega estos dos registros CNAME:

| Type  | Host | Value/Target                              | TTL       |
|-------|------|-------------------------------------------|-----------|
| CNAME | www  | diamante-pro-1951dcdb66df.herokuapp.com  | Automatic |
| ALIAS | @    | diamante-pro-1951dcdb66df.herokuapp.com  | Automatic |

**NOTA:** Si Namecheap no permite ALIAS en @, puedes:
1. Usar CNAME Flattening (si está disponible)
2. O configurar URL Redirect de @ hacia www

### Paso 3: Configurar en Heroku

Ejecuta estos comandos en tu terminal:

```bash
# 1. Instalar Heroku CLI (si no lo tienes)
# Descarga de: https://devcenter.heroku.com/articles/heroku-cli

# 2. Iniciar sesión en Heroku
heroku login

# 3. Agregar dominios personalizados
heroku domains:add www.diamantepro.me -a diamante-pro-1951dcdb66df
heroku domains:add diamantepro.me -a diamante-pro-1951dcdb66df

# 4. Habilitar SSL automático
heroku certs:auto:enable -a diamante-pro-1951dcdb66df

# 5. Ver información del dominio
heroku domains -a diamante-pro-1951dcdb66df
```

### Paso 4: Esperar propagación DNS
- Tiempo estimado: 5-30 minutos
- Puede tomar hasta 24 horas en algunos casos
- Verificar en: https://dnschecker.org/#CNAME/diamantepro.me

## 🔍 Verificar Configuración

Una vez propagado, prueba estos URLs:
- ✅ https://diamantepro.me
- ✅ https://www.diamantepro.me  
- ✅ https://diamantepro.me/dashboard
- ✅ https://diamantepro.me/api/v1/login

## 🔒 Certificado SSL

Heroku configurará automáticamente el certificado SSL (HTTPS) cuando:
1. Los registros DNS apunten correctamente
2. Heroku detecte la propagación
3. Let's Encrypt emita el certificado (automático)

## 📱 Actualizar la Aplicación

Después de configurar el dominio, actualiza estas URLs en tu app:

### En `app/__init__.py` o configuración:
```python
# URLs permitidas para CORS
ALLOWED_ORIGINS = [
    'https://diamantepro.me',
    'https://www.diamantepro.me',
    'http://localhost:5001'  # Para desarrollo local
]
```

### En documentación API:
- URL Base Producción: `https://diamantepro.me/api/v1`
- URL Base Local: `http://localhost:5001/api/v1`

## ⚠️ Problemas Comunes

### 1. "DNS_PROBE_FINISHED_NXDOMAIN"
- Espera más tiempo (propagación DNS)
- Verifica que los registros estén guardados en Namecheap

### 2. "Application Error" en Heroku
- Verifica que la app esté desplegada: `heroku logs --tail -a diamante-pro-1951dcdb66df`
- Asegúrate que la base de datos esté configurada

### 3. SSL no funciona
- Espera 30-60 minutos después de agregar el dominio
- Ejecuta: `heroku certs:auto:refresh -a diamante-pro-1951dcdb66df`

## 🎯 Comandos Útiles

```bash
# Ver logs en tiempo real
heroku logs --tail -a diamante-pro-1951dcdb66df

# Ver estado de dominios
heroku domains -a diamante-pro-1951dcdb66df

# Ver estado de SSL
heroku certs:auto -a diamante-pro-1951dcdb66df

# Reiniciar la app
heroku restart -a diamante-pro-1951dcdb66df
```

## 📞 Soporte

Si tienes problemas:
1. Verifica los logs de Heroku
2. Comprueba los registros DNS en Namecheap
3. Usa https://dnschecker.org para verificar propagación
