"""
Script para crear tablas de Aportes de Capital y Activos
"""
from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    print("🔧 Creando tablas de Aportes de Capital y Activos...")
    
    try:
        # Crear todas las tablas que no existan
        db.create_all()
        print("✅ ¡Tablas creadas exitosamente!")
        print("\n📋 Nuevas tablas disponibles:")
        print("   - aportes_capital: Para registrar aportes de socios")
        print("   - activos: Para registrar activos fijos (motos, equipos, etc.)")
    except Exception as e:
        print(f"❌ Error: {e}")
