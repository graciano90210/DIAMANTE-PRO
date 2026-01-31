import os
os.environ['SENDGRID_API_KEY'] = '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'
os.environ['SENDGRID_FROM_EMAIL'] = 'graciano90210@gmail.com'

from app.email_service import email_service

print("=" * 60)
print("🧪 PRUEBA DE SENDGRID - DIAMANTE PRO")
print("=" * 60)

success = email_service.send_email(
    to_email="graciano90210@gmail.com",
    subject="✅ Prueba DIAMANTE PRO - GitHub Student Pack",
    html_content="""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>🎉 ¡Todo configurado correctamente!</h1>
            <h2>GitHub Student Pack implementado:</h2>
            <ul>
                <li>✅ GitHub Actions - CI/CD automático</li>
                <li>✅ Sentry - Monitoreo de errores</li>
                <li>✅ SendGrid - Emails transaccionales</li>
            </ul>
            <p>Tu sistema DIAMANTE PRO está listo para enviar emails.</p>
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
    print("\n✅ EMAIL ENVIADO EXITOSAMENTE!")
    print("📬 Revisa tu bandeja de entrada: graciano90210@gmail.com")
    print("\n🎯 Configuración completa:")
    print("   ✅ GitHub Actions")
    print("   ✅ Sentry")
    print("   ✅ SendGrid")
else:
    print("\n❌ Error enviando email")

print("\n" + "=" * 60)
