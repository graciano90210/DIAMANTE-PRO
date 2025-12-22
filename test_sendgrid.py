"""
Script de prueba para SendGrid
"""
from app.email_service import email_service

def test_simple_email():
    """Probar envío simple de email"""
    print("📧 Probando SendGrid...")
    
    success = email_service.send_email(
        to_email="graciano90210@gmail.com",  # Cambiar por tu email
        subject="🧪 Prueba DIAMANTE PRO - SendGrid",
        html_content="""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h1>✅ ¡SendGrid funciona!</h1>
                <p>Tu configuración de SendGrid está correcta.</p>
                <p>Ahora puedes enviar:</p>
                <ul>
                    <li>Confirmaciones de pago</li>
                    <li>Recordatorios de pago</li>
                    <li>Notificaciones de préstamos</li>
                </ul>
                <hr>
                <p style="color: #666;">
                    DIAMANTE PRO - Sistema de Préstamos<br>
                    <a href="https://diamantepro.me">diamantepro.me</a>
                </p>
            </body>
        </html>
        """
    )
    
    if success:
        print("✅ Email enviado exitosamente!")
        print("📬 Revisa tu bandeja de entrada")
    else:
        print("❌ Error enviando email")
        print("💡 Verifica que SENDGRID_API_KEY esté configurado")
        print("💡 Verifica que SENDGRID_FROM_EMAIL esté verificado en SendGrid")


def test_payment_confirmation():
    """Probar email de confirmación de pago"""
    print("\n💰 Probando email de confirmación de pago...")
    
    success = email_service.send_payment_confirmation(
        cliente_email="graciano90210@gmail.com",  # Cambiar por tu email
        cliente_nombre="Juan Pérez",
        monto=500.00,
        fecha="2025-12-22"
    )
    
    if success:
        print("✅ Email de confirmación enviado!")
    else:
        print("❌ Error enviando confirmación")


def test_payment_reminder():
    """Probar email de recordatorio de pago"""
    print("\n📅 Probando email de recordatorio...")
    
    success = email_service.send_payment_reminder(
        cliente_email="graciano90210@gmail.com",  # Cambiar por tu email
        cliente_nombre="María López",
        monto_pendiente=250.00,
        fecha_vencimiento="2025-12-25"
    )
    
    if success:
        print("✅ Email de recordatorio enviado!")
    else:
        print("❌ Error enviando recordatorio")


def test_loan_notification():
    """Probar email de nuevo préstamo"""
    print("\n🎉 Probando email de nuevo préstamo...")
    
    success = email_service.send_new_loan_notification(
        cliente_email="graciano90210@gmail.com",  # Cambiar por tu email
        cliente_nombre="Carlos Ramírez",
        monto=10000.00,
        cuotas=24,
        cuota_valor=500.00
    )
    
    if success:
        print("✅ Email de préstamo enviado!")
    else:
        print("❌ Error enviando notificación de préstamo")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBA DE SENDGRID - DIAMANTE PRO")
    print("=" * 60)
    
    if not email_service.enabled:
        print("\n⚠️  SendGrid NO está configurado")
        print("\n📝 Para configurar:")
        print("1. Obtén tu API key de SendGrid:")
        print("   https://app.sendgrid.com/settings/api_keys")
        print("\n2. Configura las variables de entorno:")
        print("   export SENDGRID_API_KEY='SG.tu-api-key'")
        print("   export SENDGRID_FROM_EMAIL='tu-email@verificado.com'")
        print("\n3. O agrégalas a tu archivo .env")
        print("\n💡 Tip: Verifica tu sender email en SendGrid primero")
        print("   https://app.sendgrid.com/settings/sender_auth")
    else:
        print(f"\n✅ SendGrid configurado")
        print(f"📧 From: {email_service.from_email}")
        print(f"🔑 API Key: {'*' * 20}...{email_service.api_key[-5:]}")
        
        # Ejecutar todas las pruebas
        test_simple_email()
        
        # Descomentar para probar los otros emails
        # test_payment_confirmation()
        # test_payment_reminder()
        # test_loan_notification()
    
    print("\n" + "=" * 60)
    print("✨ Prueba completada")
    print("=" * 60)
