"""Script para verificar y sincronizar tablas"""
from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    # Ver columnas de sociedades
    print("=== Columnas actuales en 'sociedades' ===")
    result = db.session.execute(db.text("PRAGMA table_info(sociedades)"))
    for row in result.fetchall():
        print(f"  {row[1]} ({row[2]})")
    
    # Verificar si existe tabla socios
    print("\n=== Verificando tabla 'socios' ===")
    try:
        result = db.session.execute(db.text("PRAGMA table_info(socios)"))
        cols = result.fetchall()
        if cols:
            print("Tabla socios existe:")
            for row in cols:
                print(f"  {row[1]} ({row[2]})")
        else:
            print("Tabla socios NO existe")
    except Exception as e:
        print(f"Error: {e}")
    
    # Verificar si existe tabla oficinas
    print("\n=== Verificando tabla 'oficinas' ===")
    try:
        result = db.session.execute(db.text("PRAGMA table_info(oficinas)"))
        cols = result.fetchall()
        if cols:
            print("Tabla oficinas existe:")
            for row in cols:
                print(f"  {row[1]} ({row[2]})")
        else:
            print("Tabla oficinas NO existe - se creará")
    except Exception as e:
        print(f"Error: {e}")
    
    # Agregar columnas faltantes a sociedades
    print("\n=== Agregando columnas faltantes ===")
    columnas_faltantes = [
        ("descripcion", "TEXT"),
        ("porcentaje_dueno", "REAL DEFAULT 100"),
    ]
    
    for col_name, col_type in columnas_faltantes:
        try:
            db.session.execute(db.text(f"ALTER TABLE sociedades ADD COLUMN {col_name} {col_type}"))
            print(f"  ✅ Agregada: {col_name}")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print(f"  ⏭️ Ya existe: {col_name}")
            else:
                print(f"  ⚠️ {col_name}: {e}")
    
    # Agregar columna oficina_id a rutas si no existe
    print("\n=== Verificando columna oficina_id en rutas ===")
    try:
        db.session.execute(db.text("ALTER TABLE rutas ADD COLUMN oficina_id INTEGER REFERENCES oficinas(id)"))
        print("  ✅ Agregada columna oficina_id a rutas")
    except Exception as e:
        if "duplicate column" in str(e).lower():
            print("  ⏭️ Ya existe columna oficina_id")
        else:
            print(f"  ⚠️ {e}")
    
    db.session.commit()
    
    # Crear todas las tablas (incluyendo oficinas)
    print("\n=== Creando tablas faltantes ===")
    db.create_all()
    print("✅ db.create_all() ejecutado")
    
    # Verificar de nuevo
    print("\n=== Verificando tablas creadas ===")
    for tabla in ['socios', 'oficinas']:
        result = db.session.execute(db.text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}'"))
        if result.fetchone():
            print(f"✅ Tabla {tabla} OK")
        else:
            print(f"❌ Tabla {tabla} NO existe")
