# 🚀 GitHub Student Pack - Guía de Configuración

Esta guía te ayudará a configurar las herramientas gratuitas del GitHub Student Pack implementadas en DIAMANTE PRO.

## 📋 Herramientas Implementadas

1. ✅ **GitHub Actions** - CI/CD automatizado
2. ✅ **Sentry** - Monitoreo de errores (100k eventos/mes gratis)
3. ✅ **SendGrid** - Emails transaccionales (100 emails/día gratis)

---

## 1️⃣ GitHub Actions - CI/CD

### ✨ Beneficios:
- Deploy automático a Heroku cuando hagas push a `main`
- Tests automáticos en cada Pull Request
- Verificación de sintaxis Python
- **100% GRATIS** para repositorios públicos y Student Pack

### 📝 Configuración:

#### Paso 1: Configurar Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Click en **Settings** → **Secrets and variables** → **Actions**
3. Click en **New repository secret** y agrega:

| Secret Name | Valor | Dónde obtenerlo |
|------------|-------|-----------------|
| `HEROKU_API_KEY` | Tu API key de Heroku | [Heroku Account](https://dashboard.heroku.com/account) |
| `HEROKU_APP_NAME` | `diamante-pro` | Nombre de tu app en Heroku |
| `HEROKU_EMAIL` | Tu email de Heroku | Email con el que te registraste |
| `APP_URL` | `https://diamantepro.me` | URL de tu aplicación |

#### Paso 2: Obtener tu Heroku API Key

```bash
heroku auth:token
```

Copia el token y úsalo como `HEROKU_API_KEY`

#### Paso 3: Hacer push y ver la magia ✨

```bash
git add .
git commit -m "feat: Implementar CI/CD con GitHub Actions"
git push origin main
```

Ve a **Actions** en tu repositorio para ver el progreso del deploy.

### 🎯 Workflows Configurados:

1. **deploy.yml**: Deploy automático a Heroku
   - Se ejecuta al hacer push a `main`
   - Corre tests primero
   - Si pasan, hace deploy a Heroku
   - Verifica que la app esté funcionando

2. **tests.yml**: Tests en Pull Requests
   - Se ejecuta en PRs y push a `develop`
   - Corre tests con coverage
   - Verifica linting con flake8

---

## 2️⃣ Sentry - Monitoreo de Errores

### ✨ Beneficios:
- **100,000 eventos/mes GRATIS** para estudiantes
- Tracking de errores en tiempo real
- Stack traces completos
- Alertas por email/Slack
- Performance monitoring

### 📝 Configuración:

#### Paso 1: Crear cuenta en Sentry

1. Ve a [sentry.io](https://sentry.io/signup/)
2. Regístrate con tu email de estudiante
3. Aplica el GitHub Student Pack para obtener el plan gratis

#### Paso 2: Crear Proyecto

1. Click en **Create Project**
2. Selecciona **Flask** como plataforma
3. Nombre del proyecto: `diamante-pro`
4. Copia el **DSN** que te muestra

#### Paso 3: Configurar en Heroku

```bash
heroku config:set SENTRY_DSN="https://tukey@sentry.io/tuproyecto"
```

#### Paso 4: Para desarrollo local

Crea un archivo `.env` en la raíz del proyecto:

```env
SENTRY_DSN=https://tukey@sentry.io/tuproyecto
```

#### Paso 5: Verificar que funciona

```bash
# Reiniciar la app en Heroku
heroku restart

# Ver logs
heroku logs --tail
```

Deberías ver: `✅ Sentry inicializado - Monitoreo activo`

### 🧪 Probar Sentry:

Agrega este endpoint temporal en [app/routes.py](app/routes.py):

```python
@app.route('/sentry-test')
def sentry_test():
    division_by_zero = 1 / 0  # Esto causará un error
```

Visita `https://diamantepro.me/sentry-test` y verás el error en Sentry.

---

## 3️⃣ SendGrid - Emails Transaccionales

### ✨ Beneficios:
- **100 emails/día GRATIS** permanentemente
- **Créditos adicionales** con Student Pack
- APIs simples de usar
- Tracking de emails
- Templates profesionales

### 📝 Configuración:

#### Paso 1: Crear cuenta en SendGrid

1. Ve a [sendgrid.com](https://signup.sendgrid.com/)
2. Regístrate (usa tu email de estudiante para beneficios)
3. Verifica tu email

#### Paso 2: Crear API Key

1. Ve a **Settings** → **API Keys**
2. Click en **Create API Key**
3. Nombre: `diamante-pro-production`
4. Permisos: **Full Access** (o solo Mail Send)
5. Copia la API Key (¡solo se muestra una vez!)

#### Paso 3: Verificar dominio de envío

Para usar `noreply@diamantepro.me`:

1. Ve a **Settings** → **Sender Authentication**
2. Click en **Authenticate Your Domain**
3. Sigue los pasos para verificar `diamantepro.me`

**O usa un email verificado:**

1. Ve a **Settings** → **Sender Authentication**
2. Click en **Verify a Single Sender**
3. Agrega tu email personal (ej: `graciano90210@gmail.com`)
4. Verifica el email

#### Paso 4: Configurar en Heroku

```bash
heroku config:set SENDGRID_API_KEY="SG.tu-api-key-aqui"
heroku config:set SENDGRID_FROM_EMAIL="graciano90210@gmail.com"
```

#### Paso 5: Para desarrollo local

En tu archivo `.env`:

```env
SENDGRID_API_KEY=SG.tu-api-key-aqui
SENDGRID_FROM_EMAIL=graciano90210@gmail.com
```

### 🧪 Probar SendGrid:

Crea un script de prueba [test_email.py](test_email.py):

```python
from app.email_service import email_service

# Prueba simple
success = email_service.send_email(
    to_email="tu-email@gmail.com",
    subject="Prueba DIAMANTE PRO",
    html_content="<h1>¡Funciona!</h1><p>SendGrid está configurado.</p>"
)

print("✅ Email enviado!" if success else "❌ Error enviando email")
```

Ejecuta:
```bash
python test_email.py
```

### 📧 Emails Implementados:

El servicio incluye estos métodos listos para usar:

1. **send_payment_confirmation()** - Confirmación de pago
2. **send_payment_reminder()** - Recordatorio de pago
3. **send_new_loan_notification()** - Notificación de nuevo préstamo

**Ejemplo de uso en tu código:**

```python
from app.email_service import email_service

# Al registrar un pago
email_service.send_payment_confirmation(
    cliente_email="cliente@email.com",
    cliente_nombre="Juan Pérez",
    monto=500.00,
    fecha="2025-12-22"
)
```

---

## 🔧 Mantenimiento

### Ver logs de GitHub Actions:
```bash
# En tu repositorio de GitHub
Actions → Click en el workflow → Ver logs
```

### Ver errores en Sentry:
```bash
# Dashboard de Sentry
https://sentry.io/organizations/tu-org/issues/
```

### Ver estadísticas de SendGrid:
```bash
# Dashboard de SendGrid
https://app.sendgrid.com/statistics
```

### Comandos útiles de Heroku:
```bash
# Ver todas las variables de entorno
heroku config

# Ver logs en tiempo real
heroku logs --tail

# Reiniciar la app
heroku restart

# Abrir en el navegador
heroku open
```

---

## 💰 Costos

| Servicio | Plan Estudiante | Límite |
|----------|----------------|---------|
| GitHub Actions | ✅ GRATIS ilimitado | Repositorios públicos |
| Sentry | ✅ 100k eventos/mes | Suficiente para producción |
| SendGrid | ✅ 100 emails/día | 3,000 emails/mes |
| Heroku | ✅ $13 créditos/mes | Suficiente para hobby dyno |
| PostgreSQL | ✅ Essential plan | Incluido con Heroku |

**Total: $0/mes** con GitHub Student Pack 🎓

---

## ✅ Checklist de Configuración

- [ ] GitHub Actions configurado con secrets
- [ ] Sentry cuenta creada y DSN configurado
- [ ] SendGrid API key creado
- [ ] Sender email verificado en SendGrid
- [ ] Variables de entorno configuradas en Heroku
- [ ] Primer deploy exitoso con GitHub Actions
- [ ] Primer error capturado en Sentry
- [ ] Primer email enviado con SendGrid

---

## 🆘 Solución de Problemas

### GitHub Actions falla:

```bash
# Verifica que los secrets estén configurados correctamente
# Settings → Secrets → Actions
```

### Sentry no captura errores:

```bash
# Verifica que SENTRY_DSN esté configurado
heroku config | grep SENTRY

# Si no está, configúralo:
heroku config:set SENTRY_DSN="tu-dsn"
```

### SendGrid no envía emails:

```bash
# Verifica la API key
heroku config | grep SENDGRID

# Verifica que el sender email esté verificado en SendGrid
```

---

## 📚 Recursos Adicionales

- [GitHub Student Pack](https://education.github.com/pack)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Sentry Flask Docs](https://docs.sentry.io/platforms/python/guides/flask/)
- [SendGrid Python Docs](https://docs.sendgrid.com/for-developers/sending-email/quickstart-python)
- [Heroku Config Vars](https://devcenter.heroku.com/articles/config-vars)

---

💎 **DIAMANTE PRO** - Powered by GitHub Student Pack
