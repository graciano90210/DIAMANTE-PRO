"""
Script para agregar la columna valor_cuota a la tabla prestamos
"""
from app import create_app
from app.models import db
import sqlite3

app = create_app()

with app.app_context():
    print("🔄 Agregando columna valor_cuota a prestamos...")
    
    # Obtener la ruta de la base de datos
    db_path = 'instance/diamante.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(prestamos)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'valor_cuota' not in columns:
            # Agregar la columna
            cursor.execute("ALTER TABLE prestamos ADD COLUMN valor_cuota FLOAT")
            conn.commit()
            print("✅ Columna valor_cuota agregada correctamente!")
            
            # Calcular valor_cuota para préstamos existentes
            cursor.execute("""
                UPDATE prestamos 
                SET valor_cuota = CAST(monto_a_pagar AS FLOAT) / CAST(numero_cuotas AS FLOAT)
                WHERE valor_cuota IS NULL
            """)
            conn.commit()
            print("✅ Valores calculados para préstamos existentes!")
        else:
            print("ℹ️ La columna valor_cuota ya existe")
        
        conn.close()
        print("✅ Migración completada!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
