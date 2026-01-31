import sqlite3
import os

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'diamante.db')

print(f"📂 Conectando a la base de datos en: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Nuevas columnas a agregar a la tabla 'clientes'
    new_columns = [
        ("gastos_mensuales_promedio", "REAL"),
        ("personas_a_cargo", "INTEGER DEFAULT 0"),
        ("estado_civil", "TEXT"),
        ("tiempo_residencia_meses", "INTEGER"),
        ("tipo_documento_fiscal", "TEXT DEFAULT 'CNPJ'"),
        ("documento_fiscal_negocio", "TEXT")
    ]
    
    table_name = "clientes"
    
    print(f"🛠️  Verificando columnas en tabla '{table_name}'...")
    
    # Obtener columnas existentes
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                print(f"   ➕ Agregando columna: {col_name} ({col_type})...")
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                print(f"      ✅ Éxito.")
            except Exception as e:
                print(f"      ❌ Error al agregar {col_name}: {e}")
        else:
            print(f"   ℹ️  La columna '{col_name}' ya existe.")

    conn.commit()
    conn.close()
    print("\n✅ Proceso de actualización finalizado exitosamente.")

except Exception as e:
    print(f"\n❌ Error General: {e}")
