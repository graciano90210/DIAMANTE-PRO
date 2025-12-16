# 🌐 Configuración de Dominio diamantepro.me

## ✅ Estado Actual:
- Aplicación desplegada: https://diamante-pro-1951dcdb66df.herokuapp.com
- SSL Automático: Habilitándose...
- Dominios: Esperando configuración DNS

## 📋 Pasos para Configurar DNS en Namecheap:

### 1. Ir a Namecheap
Ve a: https://ap.www.namecheap.com/domains/list/

### 2. Seleccionar diamantepro.me
- Click en "Manage" junto a diamantepro.me
- Ir a la pestaña "Advanced DNS"

### 3. Agregar Registros DNS

**Eliminar los registros existentes que apunten a @ y www (si los hay)**

**Agregar estos 2 registros CNAME:**

| Type  | Host | Value/Target                              | TTL       |
|-------|------|-------------------------------------------|-----------|
| CNAME | www  | diamante-pro-1951dcdb66df.herokuapp.com   | Automatic |
| CNAME | @    | diamante-pro-1951dcdb66df.herokuapp.com   | Automatic |

**IMPORTANTE:** Si Namecheap no permite CNAME en @, usa:
- Type: ALIAS o ANAME (si está disponible)
- O configura un redirect de @ a www

### 4. Guardar Cambios
Click en "Save All Changes" (botón verde)

### 5. Esperar Propagación DNS
- Tiempo: 5-30 minutos (puede ser hasta 24 horas)
- Verificar en: https://dnschecker.org/#CNAME/diamantepro.me

## 🔍 Verificar que funciona:

Después de que propague, estos URLs deben funcionar:
- ✅ https://diamantepro.me
- ✅ https://www.diamantepro.me
- ✅ https://diamantepro.me/api/v1/login

## 🔒 SSL Automático (HTTPS)

Heroku configurará automáticamente el certificado SSL cuando:
1. Los registros DNS estén propagados
2. Heroku detecte que apuntan correctamente

Verificar estado:
```powershell
heroku certs:auto -a diamante-pro
```

## ⚡ Comandos Útiles:

```powershell
# Ver dominios configurados
heroku domains -a diamante-pro

# Ver estado SSL
heroku certs:auto -a diamante-pro

# Esperar a que SSL esté activo
heroku certs:auto:wait -a diamante-pro

# Abrir aplicación
heroku open -a diamante-pro
```

## 📞 Si algo sale mal:

1. **DNS no propaga:**
   - Espera 30 minutos más
   - Verifica que los valores sean exactos
   - Sin espacios al inicio/final

2. **SSL no se habilita:**
   - Espera a que DNS propague primero
   - Ejecuta: `heroku certs:auto:refresh -a diamante-pro`

3. **Error "Parked Domain":**
   - Desactiva "URL Redirect" en Namecheap
   - Asegúrate que los CNAME estén correctos

---

**Una vez configurado, tu sistema estará en:**
- 🌐 Web: https://diamantepro.me
- 📱 API: https://diamantepro.me/api/v1
- 🔐 Login: https://diamantepro.me (admin / admin123)

¡Tu sistema estará 100% profesional y listo para producción! 🚀
