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
    
    # Hacer backup de la base de datos actual (si existe)
    db_path = 'instance/diamante.db'
    if os.path.exists(db_path):
        backup_path = f'instance/diamante_old_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        try:
            os.rename(db_path, backup_path)
            print(f"💾 Base de datos anterior renombrada: {backup_path}")
        except Exception as e:
            print(f"⚠️ No se pudo renombrar, creando nueva base de datos de todos modos...")
            # En GitHub Actions esto no importa mucho porque empieza limpio, 
            # pero es bueno mantenerlo para tu uso local.
    
    # Crear todas las tablas desde cero
    db.create_all()
    print("✅ Base de datos recreada con todas las columnas!")
    
    # --- 1. Crear usuario ADMIN ---
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

    # --- 2. Crear usuario CRISTIAN (PARA LOS TESTS) ---
    # Este es el bloque nuevo que necesitamos para que pase el check verde ✅
    test_user = Usuario.query.filter_by(usuario='cristian').first()
    if not test_user:
        test_user = Usuario(
            usuario='cristian',
            password='1234',  # ¡IMPORTANTE! Coincide con lo que pide test_api.py
            nombre='Cristian Pruebas',
            rol='cobrador',   # Le ponemos rol cobrador para que tenga acceso a rutas
            activo=True
        )
        db.session.add(test_user)
        db.session.commit()
        print("👤 Usuario de prueba creado (cristian/1234)")
    
    print("\n✅ ¡Base de datos lista para usar!")
    print("📊 Tablas creadas:")
    print("   - usuarios")
    print("   - clientes")
    print("   - prestamos (con todas las columnas)")
    print("   - pagos")
    print("   - transacciones")