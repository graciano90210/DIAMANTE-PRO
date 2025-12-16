"""
Script para agregar el campo grupo_operativo a la tabla usuarios
Permite separar rutas PROPIAS de rutas en SOCIEDAD
"""
from app import create_app, db
from app.models import Usuario

def agregar_grupo_operativo():
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('usuarios')]
            
            if 'grupo_operativo' in columns:
                print("✅ La columna 'grupo_operativo' ya existe en la tabla usuarios")
            else:
                # Agregar la columna
                with db.engine.connect() as conn:
                    conn.execute(db.text("""
                        ALTER TABLE usuarios 
                        ADD COLUMN grupo_operativo VARCHAR(20) DEFAULT 'PROPIO'
                    """))
                    conn.commit()
                print("✅ Columna 'grupo_operativo' agregada exitosamente")
            
            # Actualizar todos los usuarios existentes a 'PROPIO' por defecto
            usuarios = Usuario.query.all()
            for usuario in usuarios:
                if not hasattr(usuario, 'grupo_operativo') or usuario.grupo_operativo is None:
                    usuario.grupo_operativo = 'PROPIO'
            
            db.session.commit()
            print(f"✅ {len(usuarios)} usuarios actualizados con grupo operativo 'PROPIO'")
            print("\n📋 Usuarios en el sistema:")
            for usuario in usuarios:
                print(f"   - {usuario.nombre} ({usuario.rol}) → {usuario.grupo_operativo}")
            
            print("\n✅ Migración completada exitosamente")
            print("\n💡 Ahora puedes cambiar el grupo operativo de los cobradores a 'SOCIEDAD'")
            print("   cuando sea necesario desde la interfaz de administración.")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    agregar_grupo_operativo()
