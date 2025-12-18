import sqlite3
import os

db_path = os.path.join('instance', 'diamante.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 Creando tablas de Aportes de Capital y Activos...")
    
    try:
        # Tabla de Aportes de Capital
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aportes_capital (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sociedad_id INTEGER NOT NULL,
                nombre_aportante VARCHAR(100) NOT NULL,
                monto FLOAT NOT NULL,
                moneda VARCHAR(3) DEFAULT 'COP',
                tipo_aporte VARCHAR(20) DEFAULT 'EFECTIVO',
                fecha_aporte DATETIME DEFAULT CURRENT_TIMESTAMP,
                descripcion VARCHAR(200),
                comprobante VARCHAR(300),
                registrado_por_id INTEGER NOT NULL,
                FOREIGN KEY (sociedad_id) REFERENCES sociedades (id),
                FOREIGN KEY (registrado_por_id) REFERENCES usuarios (id)
            )
        ''')
        
        # Tabla de Activos Fijos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                categoria VARCHAR(50) NOT NULL,
                descripcion VARCHAR(200),
                valor_compra FLOAT NOT NULL,
                moneda VARCHAR(3) DEFAULT 'COP',
                fecha_compra DATETIME DEFAULT CURRENT_TIMESTAMP,
                sociedad_id INTEGER,
                ruta_id INTEGER,
                usuario_responsable_id INTEGER,
                marca VARCHAR(50),
                modelo VARCHAR(50),
                placa_serial VARCHAR(50),
                estado VARCHAR(20) DEFAULT 'ACTIVO',
                foto VARCHAR(300),
                notas VARCHAR(500),
                registrado_por_id INTEGER NOT NULL,
                FOREIGN KEY (sociedad_id) REFERENCES sociedades (id),
                FOREIGN KEY (ruta_id) REFERENCES rutas (id),
                FOREIGN KEY (usuario_responsable_id) REFERENCES usuarios (id),
                FOREIGN KEY (registrado_por_id) REFERENCES usuarios (id)
            )
        ''')
        
        conn.commit()
        print("✅ ¡Tablas creadas exitosamente!")
        print("\n📋 Nuevas tablas disponibles:")
        print("   - aportes_capital: Para registrar aportes de socios")
        print("   - activos: Para registrar activos fijos (motos, equipos, etc.)")
        
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()
else:
    print(f"❌ No se encontró la base de datos en: {db_path}")
