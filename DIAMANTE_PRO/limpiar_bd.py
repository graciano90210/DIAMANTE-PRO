"""
Script para limpiar datos de prueba en PostgreSQL
CUIDADO: Esto borra TODOS los datos excepto el usuario admin
"""
from app import create_app, db
from app.models import Usuario, Cliente, Prestamo, Pago, Ruta, Sociedad

app = create_app()

with app.app_context():
    print("🗑️  Limpiando base de datos...")
    
    # Borrar en orden de dependencias
    Pago.query.delete()
    print("  ✓ Pagos eliminados")
    
    Prestamo.query.delete()
    print("  ✓ Préstamos eliminados")
    
    Cliente.query.delete()
    print("  ✓ Clientes eliminados")
    
    Ruta.query.delete()
    print("  ✓ Rutas eliminadas")
    
    Sociedad.query.delete()
    print("  ✓ Sociedades eliminadas")
    
    # Borrar usuarios excepto admin
    Usuario.query.filter(Usuario.usuario != 'admin').delete()
    print("  ✓ Usuarios (excepto admin) eliminados")
    
    db.session.commit()
    print("\n✅ Base de datos limpia y lista para importar")
