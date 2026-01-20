from app import create_app
from app.models import db
from sqlalchemy import inspect, text

app = create_app()

def diagnosticar():
    print("🕵️‍♂️ Diagnóstico de Base de Datos en Producción...")
    with app.app_context():
        # 1. Verificar tablas existentes
        inspector = inspect(db.engine)
        tablas = inspector.get_table_names()
        print(f"📊 Tablas encontradas ({len(tablas)}):")
        for t in tablas:
            print(f"   - {t}")
        
        # 2. Verificar columnas de Cliente
        print("\n🧐 Verificando columnas de 'clientes':")
        try:
            columnas = [c['name'] for c in inspector.get_columns('clientes')]
            esperadas = ['gastos_mensuales_promedio', 'personas_a_cargo', 'estado_civil', 
                         'tiempo_residencia_meses', 'tipo_documento_fiscal', 'documento_fiscal_negocio']
            found_all = True
            for esp in esperadas:
                if esp in columnas:
                    print(f"   ✅ {esp}")
                else:
                    print(f"   ❌ {esp} (FALTA)")
                    found_all = False
        except Exception as e:
            print(f"   ❌ Error leyendo columnas: {e}")

        # 3. Verificar si Aportes y Activos existen (causa probable de error 500)
        missing_tables = []
        if 'aportes_capital' not in tablas:
            missing_tables.append('aportes_capital')
        if 'activos' not in tablas:
            missing_tables.append('activos')
            
        if missing_tables:
            print("\n⚠️ TABLAS FALTANTES DETECTADAS (Posible causa de Error 500):")
            for mt in missing_tables:
                print(f"   ❌ {mt}")
            
            print("\n🚑 Intentando crear tablas faltantes...")
            try:
                db.create_all()
                print("   ✅ db.create_all() ejecutado. Las tablas deberían existir ahora.")
            except Exception as e:
                print(f"   ❌ Error al crear tablas: {e}")
        else:
            print("\n✅ Todas las tablas críticas parecen existir.")

if __name__ == "__main__":
    diagnosticar()
