# 🔐 Guía de Seguridad - Diamante Pro

## 1. Variables de Entorno

### Archivos de Configuración

| Archivo | Propósito | ¿Se sube a Git? |
|---------|-----------|-----------------|
| `.env` | Credenciales reales (desarrollo local) | ❌ NO |
| `.env.example` | Plantilla sin valores reales | ✅ SÍ |

### Generar Claves Seguras

```bash
# Generar SECRET_KEY segura
python -c "import secrets; print(secrets.token_hex(32))"

# Generar JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 2. Rotación de API Keys

### 📧 SendGrid (Emails)

**Cuándo rotar:**
- Si la key fue expuesta en un commit
- Cada 90 días (recomendado)
- Si hay actividad sospechosa

**Pasos para rotar:**

1. Ir a [SendGrid Dashboard](https://app.sendgrid.com/settings/api_keys)
2. Click en "Create API Key"
3. Nombre: `diamante-pro-YYYY-MM-DD`
4. Permisos: "Restricted Access" → Solo "Mail Send"
5. Copiar la nueva key (empieza con `SG.`)
6. Actualizar en Heroku:
   ```bash
   heroku config:set SENDGRID_API_KEY=SG.nueva_key_aqui
   ```
7. Verificar que funciona
8. **ELIMINAR** la key anterior en SendGrid

### ☁️ AWS S3 (Almacenamiento)

**Cuándo rotar:**
- Si las credenciales fueron expuestas
- Cada 90 días (recomendado)

**Pasos para rotar:**

1. Ir a [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Users → Tu usuario → Security credentials
3. "Create access key"
4. Descargar CSV con las credenciales
5. Actualizar en Heroku:
   ```bash
   heroku config:set AWS_ACCESS_KEY_ID=nueva_key
   heroku config:set AWS_SECRET_ACCESS_KEY=nuevo_secret
   ```
6. Verificar acceso al bucket
7. **DESACTIVAR** las credenciales anteriores
8. Después de 24h sin problemas, **ELIMINAR** las anteriores

### 🔍 Sentry (Monitoreo)

**Cuándo rotar:**
- Si el DSN fue expuesto públicamente

**Pasos para rotar:**

1. Ir a [Sentry Settings](https://sentry.io/settings/) → Projects → Tu proyecto
2. Client Keys (DSN) → "Generate New Key"
3. Actualizar en Heroku:
   ```bash
   heroku config:set SENTRY_DSN=https://new_key@o123.ingest.sentry.io/456
   ```
4. Verificar que los errores llegan
5. Revocar el DSN anterior

---

## 3. Configuración en Heroku

### Ver configuración actual
```bash
heroku config
```

### Configurar variables de producción
```bash
# Claves obligatorias
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set FLASK_ENV=production

# SendGrid (opcional)
heroku config:set SENDGRID_API_KEY=SG.xxxxx
heroku config:set SENDGRID_FROM_EMAIL=noreply@tudominio.com

# AWS S3 (opcional)
heroku config:set AWS_ACCESS_KEY_ID=AKIAxxxxx
heroku config:set AWS_SECRET_ACCESS_KEY=xxxxx
heroku config:set AWS_S3_BUCKET=diamante-pro-files
heroku config:set AWS_S3_REGION=us-east-1

# Sentry (opcional)
heroku config:set SENTRY_DSN=https://xxx@o123.ingest.sentry.io/456
```

---

## 4. Checklist de Seguridad

### Antes de hacer deploy
- [ ] `.env` está en `.gitignore`
- [ ] No hay credenciales hardcodeadas en el código
- [ ] SECRET_KEY es única y segura
- [ ] FLASK_ENV=production en Heroku

### Después de exponer credenciales accidentalmente
1. **INMEDIATAMENTE** rotar todas las keys expuestas
2. Revisar logs de acceso en SendGrid/AWS
3. Verificar que no hay actividad maliciosa
4. Considerar limpiar el historial de Git:
   ```bash
   # Solo si es necesario - esto reescribe la historia
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch archivo_con_credenciales" \
     --prune-empty --tag-name-filter cat -- --all
   ```

### Auditoría periódica (mensual)
- [ ] Revisar quién tiene acceso al proyecto en Heroku
- [ ] Verificar que las keys tienen los permisos mínimos necesarios
- [ ] Revisar logs de errores en Sentry
- [ ] Verificar uso de SendGrid/AWS

---

## 5. Contactos de Emergencia

Si detectas una brecha de seguridad:

1. **SendGrid**: Desactivar key inmediatamente en dashboard
2. **AWS**: Desactivar credenciales en IAM Console
3. **Heroku**: `heroku config:unset VARIABLE_COMPROMETIDA`

---

*Última actualización: Febrero 2026*
