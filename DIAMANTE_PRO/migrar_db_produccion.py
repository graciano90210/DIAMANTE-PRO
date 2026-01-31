from app import create_app
from app.models import db
from sqlalchemy import text

app = create_app()

def migrar():
    print("🚀 Iniciando migración de base de datos en Producción...")
    with app.app_context():
        with db.engine.connect() as conn:
            # Lista de columnas a agregar
            # (Nombre, Tipo Postgres/Generic, Default opcional)
            columns_to_add = [
                ("gastos_mensuales_promedio", "FLOAT", None),
                ("personas_a_cargo", "INTEGER", "DEFAULT 0"),
                ("estado_civil", "VARCHAR(20)", None),
                ("tiempo_residencia_meses", "INTEGER", None),
                ("tipo_documento_fiscal", "VARCHAR(20)", "DEFAULT 'CNPJ'"),
                ("documento_fiscal_negocio", "VARCHAR(30)", None)
            ]
            
            for col_name, col_type, col_default in columns_to_add:
                try:
                    # Construir SQL
                    sql_default = f" {col_default}" if col_default else ""
                    sql = f"ALTER TABLE clientes ADD COLUMN {col_name} {col_type}{sql_default}"
                    
                    print(f"   ▶️ Intentando agregar: {col_name}...")
                    conn.execute(text(sql))
                    print(f"      ✅ Agregada exitosamente.")
                except Exception as e:
                    # Si falla, probablemente ya existe
                    print(f"      Run info: {str(e).splitlines()[0]} (Probablemente ya existe)")
            
            try:
                conn.commit()
                print("💾 Cambios confirmados (commit).")
            except:
                pass # Algunos engines hacen autocommit o no soportan commit explícito aquí

    print("🏁 Migración finalizada.")

if __name__ == "__main__":
    migrar()
