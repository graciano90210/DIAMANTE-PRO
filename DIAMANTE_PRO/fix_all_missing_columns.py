import sqlite3
import os
def add_missing_columns():
    db_path = os.path.join('DIAMANTE_PRO', 'instance', 'diamante.db')
    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos en: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columnas = [
        ("clientes", "gastos_mensuales_promedio", "FLOAT"),
        ("clientes", "personas_a_cargo", "INTEGER DEFAULT 0"),
        ("clientes", "estado_civil", "VARCHAR(20)"),
        ("clientes", "tiempo_residencia_meses", "INTEGER"),
        ("clientes", "tipo_negocio", "VARCHAR(50)"),
        ("clientes", "nombre_negocio", "VARCHAR(100)"),
        ("clientes", "antiguedad_negocio_meses", "INTEGER"),
        ("clientes", "local_propio", "BOOLEAN DEFAULT 0"),
        ("clientes", "dias_trabajo", "VARCHAR(20)"),
        ("clientes", "hora_cobro_preferida", "VARCHAR(10)"),
        ("clientes", "ingresos_diarios_estimados", "FLOAT"),
        ("clientes", "referido_por_cliente_id", "INTEGER"),
        ("clientes", "negocio_formalizado", "BOOLEAN DEFAULT 0"),
        ("clientes", "tipo_documento_fiscal", "VARCHAR(20) DEFAULT 'CNPJ'"),
        ("clientes", "documento_fiscal_negocio", "VARCHAR(30)"),
        ("clientes", "fecha_verificacion_fiscal", "DATETIME"),
        ("clientes", "tiene_comprobante_residencia", "BOOLEAN DEFAULT 0"),
        ("clientes", "tipo_comprobante_residencia", "VARCHAR(30)"),
        ("clientes", "comprobante_a_nombre_propio", "BOOLEAN DEFAULT 0"),
        ("clientes", "nombre_titular_comprobante", "VARCHAR(100)"),
        ("clientes", "parentesco_titular", "VARCHAR(30)"),
        ("clientes", "fecha_comprobante", "DATE"),
        ("clientes", "foto_comprobante_residencia", "VARCHAR(300)"),
        ("clientes", "score_crediticio", "INTEGER DEFAULT 500"),
        ("clientes", "nivel_riesgo", "VARCHAR(20) DEFAULT 'NUEVO'"),
        ("clientes", "limite_credito_sugerido", "FLOAT"),
        ("clientes", "credito_bloqueado", "BOOLEAN DEFAULT 0"),
        ("clientes", "motivo_bloqueo", "VARCHAR(200)"),
        ("clientes", "fecha_ultimo_calculo_score", "DATETIME"),
        ("clientes", "gps_latitud_casa", "FLOAT"),
        ("clientes", "gps_longitud_casa", "FLOAT")
    ]

    for tabla, columna, tipo in columnas:
        try:
            cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
            print(f"✅ Columna agregada: {columna} a {tabla}")
        except sqlite3.OperationalError as e:
            if f"duplicate column name: {columna}" in str(e) or "duplicate column name" in str(e):
                print(f"ℹ️ La columna {columna} ya existe en {tabla}")
            else:
                print(f"❌ Error al agregar {columna} a {tabla}: {e}")
    conn.commit()
    conn.close()
    print("✔️ Migración de columnas completada.")

if __name__ == "__main__":
    add_missing_columns()
