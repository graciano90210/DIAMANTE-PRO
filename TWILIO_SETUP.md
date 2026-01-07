# 📱 Integración Twilio - DIAMANTE PRO

## 🎯 Configuración Rápida

### 1. Obtener credenciales Twilio (GitHub Student Pack)

1. Ve a https://www.twilio.com/try-twilio
2. Regístrate con tu email de estudiante
3. Solicita beneficios Student Pack: https://www.twilio.com/students
4. Una vez verificado, ve a Console Dashboard
5. Copia:
   - **Account SID**
   - **Auth Token**  
   - **Phone Number** (número de Twilio)

### 2. Configurar variables de entorno

**Local (.env):**
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**Heroku:**
```bash
heroku config:set TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
heroku config:set TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
heroku config:set TWILIO_PHONE_NUMBER=+1234567890
heroku config:set TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 3. Instalar dependencias

```bash
pip install twilio==8.11.1
```

### 4. Para WhatsApp (opcional pero recomendado)

1. Conecta tu número de WhatsApp Business en Twilio Console
2. O usa el Sandbox de Twilio:
   - Envía "join [palabra-clave]" al número +1 415 523 8886 desde WhatsApp
   - Recibirás confirmación y podrás enviar/recibir mensajes

---

## 🚀 Endpoints Disponibles

### Verificar estado
```bash
GET /api/v1/notificaciones/estado
Authorization: Bearer {token}
```

### Enviar SMS de prueba
```bash
POST /api/v1/notificaciones/test-sms
Content-Type: application/json
Authorization: Bearer {token}

{
  "telefono": "+573001234567",
  "mensaje": "Prueba desde DIAMANTE PRO"
}
```

### Enviar WhatsApp de prueba
```bash
POST /api/v1/notificaciones/test-whatsapp
Content-Type: application/json
Authorization: Bearer {token}

{
  "telefono": "+573001234567",
  "mensaje": "Prueba desde DIAMANTE PRO"
}
```

### Recordatorio de pago individual
```bash
POST /api/v1/notificaciones/recordatorio-pago/1
Content-Type: application/json
Authorization: Bearer {token}

{
  "canal": "whatsapp"  # o "sms"
}
```

### Notificar cuotas vencidas (MASIVO)
```bash
POST /api/v1/notificaciones/cuotas-vencidas
Authorization: Bearer {token}
```

### Confirmar pago recibido
```bash
POST /api/v1/notificaciones/confirmar-pago
Content-Type: application/json
Authorization: Bearer {token}

{
  "prestamo_id": 1,
  "monto": 50000
}
```

### Notificar préstamo aprobado
```bash
POST /api/v1/notificaciones/prestamo-aprobado/1
Authorization: Bearer {token}
```

---

## 💡 Casos de Uso

### 1. Recordatorio automático diario
Programa un cron job o tarea de Heroku Scheduler:

```python
# Script: recordatorios_diarios.py
import requests

token = "tu_token_jwt"
response = requests.post(
    'https://diamantepro.me/api/v1/notificaciones/cuotas-vencidas',
    headers={'Authorization': f'Bearer {token}'}
)
print(response.json())
```

### 2. Confirmación inmediata al registrar pago
Desde el cobrador móvil, después de registrar pago:

```dart
// En Flutter
await apiService.post(
  '/notificaciones/confirmar-pago',
  body: {
    'prestamo_id': prestamoId,
    'monto': monto
  }
);
```

### 3. Notificación masiva de cambios
Enviar avisos a todos los clientes:

```python
clientes = Cliente.query.all()
contactos = [
    {
        'telefono': c.whatsapp or c.telefono,
        'mensaje': 'Nuevo horario de atención: 8am - 5pm'
    }
    for c in clientes
]
twilio_service.enviar_masivo_sms(contactos)
```

---

## 📊 Costos Aproximados (con Student Pack)

- **Crédito inicial:** $50 USD
- **SMS Colombia:** ~$0.05 USD por mensaje
- **WhatsApp:** ~$0.005 USD por mensaje (10x más barato!)
- **Total estimado:** ~1000 SMS o ~10,000 WhatsApp

---

## ⚡ Mejoras Futuras

1. **Scheduler automático**
   - Heroku Scheduler para recordatorios diarios
   - Celery para tareas programadas

2. **Respuestas automáticas**
   - Webhook para recibir respuestas de clientes
   - Chatbot básico para consultas

3. **Analytics**
   - Tracking de mensajes entregados/leídos
   - Reportes de efectividad

4. **Plantillas personalizadas**
   - Mensajes con nombre del cobrador
   - Links de pago directo

---

## 🔧 Troubleshooting

**Error: "Unable to create record: Permission denied"**
- Verifica que el número esté en formato internacional (+57...)
- Para WhatsApp sandbox, asegúrate de haber enviado "join [palabra]"

**Error: "Account not authorized"**
- Tu cuenta Twilio puede estar en modo trial
- Verifica números en Twilio Console → Phone Numbers → Verified Caller IDs

**Error: "Message body is required"**
- El mensaje no puede estar vacío
- Verifica que los datos del préstamo existan

---

**¿Necesitas ayuda?** Revisa la documentación oficial: https://www.twilio.com/docs
