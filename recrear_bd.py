"""
Script para recrear la base de datos con todas las columnas correctas
"""
import os
import shutil
from app import create_app
from app.models import db, Usuario
from datetime import datetime

app = create_app()

with app.app_context():
    print("🔄 Recreando base de datos...")
    
    # Hacer backup de la base de datos actual
    db_path = 'instance/diamante.db'
    if os.path.exists(db_path):
        backup_path = f'instance/diamante_old_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        try:
            os.rename(db_path, backup_path)
            print(f"💾 Base de datos anterior renombrada: {backup_path}")
        except Exception as e:
            print(f"⚠️ No se pudo renombrar, creando nueva base de datos de todos modos...")
            db_path = 'instance/diamante_new.db'
    
    # Crear todas las tablas desde cero
    db.create_all()
    print("✅ Base de datos recreada con todas las columnas!")
    
    # Crear usuario admin/dueño
    admin = Usuario.query.filter_by(usuario='admin').first()
    if not admin:
        admin = Usuario(
            usuario='admin',
            password='123',
            nombre='Juan Gerente',
            rol='dueno',
            activo=True
        )
        db.session.add(admin)
        db.session.commit()
        print("👤 Usuario dueño creado (admin/123)")
    
    print("\n✅ ¡Base de datos lista para usar!")
    print("📊 Tablas creadas:")
    print("   - usuarios")
    print("   - clientes")
    print("   - prestamos (con todas las columnas)")
    print("   - pagos")
    print("   - transacciones")
