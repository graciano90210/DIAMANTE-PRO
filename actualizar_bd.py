"""
Script para actualizar la base de datos con los nuevos modelos
"""
from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    print("🔄 Actualizando base de datos...")
    db.create_all()
    print("✅ Base de datos actualizada correctamente!")
    print("📊 Tablas disponibles:")
    print("   - usuarios")
    print("   - clientes")
    print("   - prestamos")
    print("   - pagos (NUEVO)")
    print("   - transacciones")
