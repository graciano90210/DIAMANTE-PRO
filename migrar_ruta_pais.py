"""
Migración: Agregar país y moneda a las rutas
"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("🔧 Agregando campos de país y moneda a rutas...")
    
    try:
        # Agregar columnas
        db.session.execute(text("""
            ALTER TABLE rutas ADD COLUMN pais VARCHAR(50) DEFAULT 'Colombia';
        """))
        
        db.session.execute(text("""
            ALTER TABLE rutas ADD COLUMN moneda VARCHAR(3) DEFAULT 'COP';
        """))
        
        db.session.execute(text("""
            ALTER TABLE rutas ADD COLUMN simbolo_moneda VARCHAR(5) DEFAULT '$';
        """))
        
        db.session.commit()
        print("✅ Campos agregados exitosamente!")
        
        # Verificar
        result = db.session.execute(text("PRAGMA table_info(rutas)")).fetchall()
        print("\n📋 Estructura actual de la tabla rutas:")
        for col in result:
            print(f"   - {col[1]} ({col[2]})")
            
    except Exception as e:
        db.session.rollback()
        if "duplicate column name" in str(e).lower():
            print("⚠️  Las columnas ya existen")
        else:
            print(f"❌ Error: {str(e)}")
