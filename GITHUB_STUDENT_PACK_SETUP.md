# 🎓 Configuración GitHub Student Pack - Diamante PRO

Este proyecto utiliza las siguientes herramientas del GitHub Student Pack:

## 🔧 Herramientas Integradas

### 1. ✅ Sentry (Error Tracking)
**Estado:** Código preparado, necesita configuración

**Beneficio:** Monitoreo de errores en tiempo real en producción

**Pasos para configurar:**
1. Ve a https://sentry.io/signup/
2. Inicia sesión con tu cuenta de GitHub (Student Pack)
3. Crea un nuevo proyecto: "Diamante PRO Mobile"
4. Selecciona plataforma: "Flutter"
5. Copia tu DSN (parecido a: `https://xxx@xxx.ingest.sentry.io/xxx`)
6. Edita `mobile-app/lib/config/sentry_config.dart`
7. Reemplaza `YOUR_SENTRY_DSN_HERE` con tu DSN real

**Archivo:** `lib/config/sentry_config.dart`

---

### 2. 🌐 Namecheap (Dominio + SSL)
**Estado:** Pendiente de configuración

**Beneficio:** Dominio .me gratis por 1 año + SSL incluido

**Pasos para configurar:**
1. Ve a https://nc.me/
2. Inicia sesión con tu cuenta de GitHub Education
3. Busca un dominio disponible (ej: `diamante-pro.me`)
4. Activa el dominio gratis con tu Student Pack
5. En Heroku Dashboard:
   - Settings → Domains → Add Domain
   - Agrega tu dominio: `diamante-pro.me` y `www.diamante-pro.me`
6. En Namecheap:
   - Domain List → Manage → Advanced DNS
   - Agrega registros CNAME según Heroku te indique

**Documentación completa:** Ver `CONFIGURAR_DOMINIO.md`

---

### 3. 📱 Twilio (SMS/WhatsApp)
**Estado:** Pendiente de integración

**Beneficio:** $50 de crédito para enviar recordatorios de pago

**Casos de uso:**
- Recordatorios de cuotas vencidas
- Confirmación de pagos recibidos
- Alertas de mora
- Mensajes masivos a clientes

**Pasos para configurar:**
1. Ve a https://www.twilio.com/try-twilio
2. Registra cuenta con email de estudiante
3. Activa Student Pack (verificación puede tardar 24-48h)
4. Obtén: Account SID, Auth Token, Phone Number
5. Crear archivo: `app/twilio_service.py`

**Próxima sesión:** Implementaremos el servicio de notificaciones

---

### 4. 📊 Heroku (Hosting Backend)
**Estado:** ✅ Ya configurado y funcionando

**Beneficio:** $13/mes de créditos (suficiente para Hobby dyno)

**URL actual:** https://diamante-pro-1951dcdb66df.herokuapp.com/

---

### 5. 📧 SendGrid (Email)
**Estado:** ✅ Ya configurado

**Beneficio:** 15,000 emails/mes gratis

**Uso actual:** Recuperación de contraseñas, reportes por email

---

## 🚀 Herramientas Adicionales Disponibles

### DigitalOcean
- **Crédito:** $200 por 1 año
- **Uso potencial:** Hospedar base de datos PostgreSQL separada
- **Ventaja:** Mejor rendimiento que Heroku Postgres gratuito

### MongoDB Atlas
- **Crédito:** $50
- **Uso potencial:** Si necesitas NoSQL para logs o analytics
- **Ventaja:** Búsquedas más rápidas para reportes complejos

### Bootstrap Studio
- **Licencia:** Gratis con Student Pack
- **Uso:** Diseñar landing page profesional para marketing

### Canva Pro
- **Licencia:** 12 meses gratis
- **Uso:** Diseñar logo, banners, material de marketing

---

## 📝 Orden de Implementación Recomendado

### Prioridad Alta (Esta semana)
1. ✅ **Sentry** - Error tracking (código ya integrado)
2. 🔄 **Namecheap** - Dominio personalizado
3. 🔄 **Twilio** - Notificaciones automáticas

### Prioridad Media (Próxima semana)
4. ⏳ **DigitalOcean** - Si necesitamos mejor base de datos
5. ⏳ **Canva Pro** - Diseño de marca profesional

### Prioridad Baja (Futuro)
6. ⏳ **MongoDB Atlas** - Si agregamos analytics avanzados
7. ⏳ **Bootstrap Studio** - Landing page de marketing

---

## 💡 Próximos Pasos Inmediatos

1. **Configurar Sentry DSN** (5 minutos)
   ```bash
   # Editar archivo:
   mobile-app/lib/config/sentry_config.dart
   ```

2. **Registrar dominio Namecheap** (15 minutos)
   - Elegir nombre
   - Configurar DNS
   - Conectar con Heroku

3. **Activar Twilio** (solicitar verificación hoy, configurar mañana)
   - La verificación del Student Pack puede tardar 24-48h
   - Mientras tanto, podemos usar cuenta trial

---

## 📚 Recursos

- **GitHub Student Pack:** https://education.github.com/pack
- **Documentación Sentry Flutter:** https://docs.sentry.io/platforms/flutter/
- **Twilio WhatsApp API:** https://www.twilio.com/whatsapp
- **Heroku Custom Domains:** https://devcenter.heroku.com/articles/custom-domains

---

**Última actualización:** 7 de enero de 2026
**Desarrollador:** cvampi
