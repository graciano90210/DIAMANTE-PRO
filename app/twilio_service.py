"""
Servicio de Notificaciones con Twilio
GitHub Student Pack: $50 de crédito gratuito
"""
import os
from twilio.rest import Client
from datetime import datetime

class TwilioService:
    def __init__(self):
        # Credenciales de Twilio (GitHub Student Pack)
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
        self.whatsapp_number = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            print("⚠️ Twilio no configurado - Agregar credenciales")
    
    def enviar_sms(self, telefono, mensaje):
        """Enviar SMS simple"""
        if not self.enabled:
            print(f"🚫 SMS no enviado (Twilio deshabilitado): {telefono}")
            return False
        
        try:
            # Asegurar formato internacional
            if not telefono.startswith('+'):
                telefono = f'+57{telefono}'  # Colombia por defecto
            
            message = self.client.messages.create(
                body=mensaje,
                from_=self.phone_number,
                to=telefono
            )
            
            print(f"✅ SMS enviado a {telefono}: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error enviando SMS: {e}")
            return False
    
    def enviar_whatsapp(self, telefono, mensaje):
        """Enviar mensaje por WhatsApp"""
        if not self.enabled:
            print(f"🚫 WhatsApp no enviado (Twilio deshabilitado): {telefono}")
            return False
        
        try:
            # Formato WhatsApp
            if not telefono.startswith('whatsapp:'):
                if not telefono.startswith('+'):
                    telefono = f'+57{telefono}'
                telefono = f'whatsapp:{telefono}'
            
            message = self.client.messages.create(
                body=mensaje,
                from_=self.whatsapp_number,
                to=telefono
            )
            
            print(f"✅ WhatsApp enviado a {telefono}: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error enviando WhatsApp: {e}")
            return False
    
    # ============ MENSAJES PREDEFINIDOS PARA COBRANZA ============
    
    def recordatorio_pago(self, cliente_nombre, monto, fecha_vencimiento):
        """Recordatorio de pago próximo a vencer"""
        mensaje = f"""
🔔 DIAMANTE PRO - Recordatorio de Pago

Hola {cliente_nombre},

Te recordamos que tienes una cuota por:
💰 ${monto:,.0f}

📅 Fecha de pago: {fecha_vencimiento}

Gracias por tu puntualidad.
        """.strip()
        return mensaje
    
    def cuota_vencida(self, cliente_nombre, monto, dias_mora):
        """Notificación de cuota vencida"""
        mensaje = f"""
⚠️ DIAMANTE PRO - Cuota Vencida

Hola {cliente_nombre},

Tu cuota de ${monto:,.0f} está vencida hace {dias_mora} día(s).

Por favor comunícate con nosotros para regularizar tu pago.

📞 Contacto: [TU_NUMERO]
        """.strip()
        return mensaje
    
    def confirmacion_pago(self, cliente_nombre, monto, saldo_restante):
        """Confirmación de pago recibido"""
        mensaje = f"""
✅ DIAMANTE PRO - Pago Recibido

Hola {cliente_nombre},

Confirmamos el pago de: ${monto:,.0f}

Saldo restante: ${saldo_restante:,.0f}

¡Gracias por tu pago!
        """.strip()
        return mensaje
    
    def prestamo_aprobado(self, cliente_nombre, monto, cuotas, valor_cuota):
        """Notificación de préstamo aprobado"""
        mensaje = f"""
🎉 DIAMANTE PRO - Préstamo Aprobado

Hola {cliente_nombre},

¡Tu préstamo ha sido aprobado!

💰 Monto: ${monto:,.0f}
📊 Cuotas: {cuotas}
💵 Valor cuota: ${valor_cuota:,.0f}

Gracias por confiar en nosotros.
        """.strip()
        return mensaje
    
    def prestamo_cancelado(self, cliente_nombre):
        """Felicitación por préstamo cancelado"""
        mensaje = f"""
🎊 DIAMANTE PRO - ¡Felicitaciones!

Hola {cliente_nombre},

¡Has cancelado completamente tu préstamo!

Gracias por tu compromiso. Esperamos poder servirte nuevamente.
        """.strip()
        return mensaje
    
    # ============ ENVÍOS MASIVOS ============
    
    def enviar_masivo_sms(self, lista_contactos):
        """
        Enviar SMS masivo a lista de contactos
        lista_contactos: [{'telefono': '+573001234567', 'mensaje': '...'}, ...]
        """
        resultados = {
            'exitosos': 0,
            'fallidos': 0,
            'errores': []
        }
        
        for contacto in lista_contactos:
            try:
                if self.enviar_sms(contacto['telefono'], contacto['mensaje']):
                    resultados['exitosos'] += 1
                else:
                    resultados['fallidos'] += 1
            except Exception as e:
                resultados['fallidos'] += 1
                resultados['errores'].append({
                    'telefono': contacto['telefono'],
                    'error': str(e)
                })
        
        return resultados

# Instancia global
twilio_service = TwilioService()
