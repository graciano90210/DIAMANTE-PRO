"""
Servicio de Email con SendGrid para DIAMANTE PRO
"""
import os
import logging

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para enviar emails transaccionales"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@diamantepro.me')
        self.enabled = bool(self.api_key) and SENDGRID_AVAILABLE
        
        if not SENDGRID_AVAILABLE:
            logger.warning("⚠️ SendGrid no instalado. Emails deshabilitados.")
        elif not self.enabled:
            logger.warning("⚠️ SENDGRID_API_KEY no configurada. Emails deshabilitados.")
            logger.warning("SendGrid no configurado. Los emails no se enviarán.")
    
    def send_email(self, to_email, subject, html_content, plain_content=None):
        """
        Enviar un email
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del email
            html_content: Contenido HTML del email
            plain_content: Contenido en texto plano (opcional)
        
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        if not self.enabled:
            logger.info(f"Email simulado a {to_email}: {subject}")
            return False
        
        try:
            message = Mail(
                from_email=Email(self.from_email, "DIAMANTE PRO"),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if plain_content:
                message.plain_text_content = Content("text/plain", plain_content)
            
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            logger.info(f"Email enviado a {to_email}. Status: {response.status_code}")
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return False
    
    def send_payment_confirmation(self, cliente_email, cliente_nombre, monto, fecha):
        """Enviar confirmación de pago"""
        subject = "Confirmación de Pago - DIAMANTE PRO"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>✅ Pago Confirmado</h2>
                <p>Hola {cliente_nombre},</p>
                <p>Tu pago ha sido registrado exitosamente:</p>
                <ul>
                    <li><strong>Monto:</strong> L. {monto:,.2f}</li>
                    <li><strong>Fecha:</strong> {fecha}</li>
                </ul>
                <p>Gracias por tu pago puntual.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    DIAMANTE PRO - Sistema de Préstamos<br>
                    <a href="https://diamantepro.me">diamantepro.me</a>
                </p>
            </body>
        </html>
        """
        plain_content = f"""
        Pago Confirmado
        
        Hola {cliente_nombre},
        
        Tu pago ha sido registrado exitosamente:
        - Monto: L. {monto:,.2f}
        - Fecha: {fecha}
        
        Gracias por tu pago puntual.
        
        DIAMANTE PRO
        """
        
        return self.send_email(cliente_email, subject, html_content, plain_content)
    
    def send_payment_reminder(self, cliente_email, cliente_nombre, monto_pendiente, fecha_vencimiento):
        """Enviar recordatorio de pago"""
        subject = "Recordatorio de Pago - DIAMANTE PRO"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>📅 Recordatorio de Pago</h2>
                <p>Hola {cliente_nombre},</p>
                <p>Te recordamos que tienes un pago pendiente:</p>
                <ul>
                    <li><strong>Monto:</strong> L. {monto_pendiente:,.2f}</li>
                    <li><strong>Fecha de vencimiento:</strong> {fecha_vencimiento}</li>
                </ul>
                <p>Por favor, realiza tu pago a tiempo para evitar cargos adicionales.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    DIAMANTE PRO - Sistema de Préstamos<br>
                    <a href="https://diamantepro.me">diamantepro.me</a>
                </p>
            </body>
        </html>
        """
        plain_content = f"""
        Recordatorio de Pago
        
        Hola {cliente_nombre},
        
        Tienes un pago pendiente:
        - Monto: L. {monto_pendiente:,.2f}
        - Fecha de vencimiento: {fecha_vencimiento}
        
        Por favor, realiza tu pago a tiempo.
        
        DIAMANTE PRO
        """
        
        return self.send_email(cliente_email, subject, html_content, plain_content)
    
    def send_new_loan_notification(self, cliente_email, cliente_nombre, monto, cuotas, cuota_valor):
        """Enviar notificación de nuevo préstamo"""
        subject = "Nuevo Préstamo Aprobado - DIAMANTE PRO"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>🎉 Préstamo Aprobado</h2>
                <p>Hola {cliente_nombre},</p>
                <p>Tu préstamo ha sido aprobado y registrado:</p>
                <ul>
                    <li><strong>Monto:</strong> L. {monto:,.2f}</li>
                    <li><strong>Número de cuotas:</strong> {cuotas}</li>
                    <li><strong>Valor de cada cuota:</strong> L. {cuota_valor:,.2f}</li>
                </ul>
                <p>Gracias por confiar en nosotros.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    DIAMANTE PRO - Sistema de Préstamos<br>
                    <a href="https://diamantepro.me">diamantepro.me</a>
                </p>
            </body>
        </html>
        """
        plain_content = f"""
        Préstamo Aprobado
        
        Hola {cliente_nombre},
        
        Tu préstamo ha sido aprobado:
        - Monto: L. {monto:,.2f}
        - Número de cuotas: {cuotas}
        - Valor de cada cuota: L. {cuota_valor:,.2f}
        
        DIAMANTE PRO
        """
        
        return self.send_email(cliente_email, subject, html_content, plain_content)


# Instancia global del servicio
email_service = EmailService()
