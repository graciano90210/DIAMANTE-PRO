from app import create_app
from app.models import Usuario, Prestamo, Ruta, Cliente, db

app = create_app()

with app.app_context():
    print("=== VERIFICANDO DATOS ===")
    
    # 1. Buscar usuario 'cvampi'
    usuario = Usuario.query.filter_by(usuario='cvampi').first()
    if not usuario:
        print("ERROR: Usuario 'cvampi' no encontrado")
        exit()
        
    print(f"Usuario Logueado: {usuario.usuario} (ID: {usuario.id}, Rol: {usuario.rol})")
    
    # 2. Buscar rutas asignadas
    rutas = Ruta.query.filter_by(cobrador_id=usuario.id).all()
    print(f"\nRutas asignadas ({len(rutas)}):")
    for r in rutas:
        print(f" - ID: {r.id}, Nombre: {r.nombre}")
        
    # 3. Buscar préstamos asignados DIRECTAMENTE al cobrador
    prestamos = Prestamo.query.filter_by(cobrador_id=usuario.id, estado='ACTIVO').all()
    print(f"\nPréstamos Activos asignados a cobrador_id={usuario.id}: {len(prestamos)}")
    
    # 4. Ver préstamos totales en el sistema
    total_prestamos = Prestamo.query.count()
    print(f"\nTotal préstamos en BD: {total_prestamos}")
    
    if total_prestamos > 0 and len(prestamos) == 0:
        print("\n!!! HAY DATOS, PERO NO ASIGNADOS A ESTE USUARIO !!!")
        
        # Asignar todo a cvampi para pruebas
        print("Asignando todos los préstamos a 'cvampi' para demostración...")
        Prestamo.query.update({Prestamo.cobrador_id: usuario.id})
        
        # Asignar rutas también
        Ruta.query.update({Ruta.cobrador_id: usuario.id})
        
        db.session.commit()
        print("✅ ASIGNACIÓN COMPLETADA. Recarga la app.")
    elif total_prestamos == 0:
        print("\n⚠️ LA BASE DE DATOS ESTÁ VACÍA DE PRÉSTAMOS.")
        # Aquí podríamos crear datos dummy
