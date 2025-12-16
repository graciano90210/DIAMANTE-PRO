"""
Script para verificar las rutas existentes en la base de datos
"""
from app import create_app, db
from app.models import Ruta, Usuario, Sociedad

def verificar_rutas():
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 VERIFICANDO RUTAS EN LA BASE DE DATOS\n")
            
            # Todas las rutas
            todas_rutas = Ruta.query.all()
            print(f"📊 Total de rutas en BD: {len(todas_rutas)}")
            
            if todas_rutas:
                print("\n📋 LISTADO DE RUTAS:")
                for ruta in todas_rutas:
                    cobrador_nombre = ruta.cobrador.nombre if ruta.cobrador else "Sin cobrador"
                    sociedad_nombre = ruta.sociedad.nombre if ruta.sociedad else "PROPIO"
                    activo = "✅ ACTIVO" if ruta.activo else "❌ INACTIVO"
                    print(f"   • ID: {ruta.id} | {ruta.nombre} | Cobrador: {cobrador_nombre} | {sociedad_nombre} | {activo}")
            
            # Rutas activas
            rutas_activas = Ruta.query.filter_by(activo=True).all()
            print(f"\n✅ Rutas activas: {len(rutas_activas)}")
            
            # Usuarios
            usuarios = Usuario.query.all()
            print(f"\n👥 Total usuarios: {len(usuarios)}")
            for usuario in usuarios:
                print(f"   • {usuario.nombre} - {usuario.rol}")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    verificar_rutas()
