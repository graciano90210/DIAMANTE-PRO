import sys, os
from sqlalchemy import inspect

# Añadimos la ruta actual para encontrar tu proyecto
sys.path.append(os.getcwd())

print("🕵️‍♂️ INICIANDO OPERACIÓN ESPÍA...")

try:
    # Intentamos importar tu aplicación
    from wsgi import app
    from app.models import Usuario, Cliente, CajaDueno
except ImportError:
    print("⚠️ No encontré 'wsgi.py'. Intentando importar desde 'app'...")
    try:
        from app import create_app, db
        from app.models import Usuario, Cliente, CajaDueno
        app = create_app()
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: No pude importar la app.\nDetalle: {e}")
        exit()

def ver_datos():
    with app.app_context():
        # 1. BUSCAR EL ROL EXACTO
        print("\n--- 👑 BUSCANDO AL JEFE ---")
        # Buscamos al usuario admin o cualquiera que parezca jefe
        jefes = Usuario.query.filter(Usuario.usuario.in_(['admin', 'Admin', 'administrador'])).all()
        
        if jefes:
            for j in jefes:
                print(f"✅ ENCONTRADO: Usuario='{j.usuario}' | ROL='{j.rol}'")
        else:
            print("⚠️ No vi un usuario 'admin'. Listando los primeros 3 usuarios:")
            for u in Usuario.query.limit(3).all():
                print(f"   -> User: {u.usuario} | Rol: {u.rol}")

        # 2. VER CLIENTES (Para copiar sus datos)
        print("\n--- 👥 FORMATO DE CLIENTES ---")
        un_cliente = Cliente.query.first()
        if un_cliente:
            inspector = inspect(Cliente)
            cols = [c.key for c in inspector.attrs]
            print(f"📋 Columnas reales: {cols}")
            print(f"ejemplo: Nombre='{un_cliente.nombre}' | Dirección='{getattr(un_cliente, 'direccion_negocio', 'NO TIENE')}'")
        else:
            print("⚠️ No tienes clientes locales.")

if __name__ == "__main__":
    ver_datos()