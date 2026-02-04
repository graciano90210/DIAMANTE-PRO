"""
Script de verificación del sistema de Oficinas
"""
from app import create_app
from app.models import Oficina, Ruta, Sociedad, Usuario
from app.services import OficinaService

app = create_app()

with app.app_context():
    print('='*60)
    print('   VERIFICACION DEL SISTEMA DE OFICINAS')
    print('='*60)
    
    # 1. Verificar tabla oficinas
    print('\n1. OFICINAS:')
    oficinas = Oficina.query.all()
    print(f'   Total: {len(oficinas)}')
    for o in oficinas:
        print(f'   ✓ {o.nombre} (ID:{o.id}, rutas:{o.numero_rutas})')
    
    # 2. Verificar rutas
    print('\n2. RUTAS:')
    rutas = Ruta.query.all()
    print(f'   Total: {len(rutas)}')
    rutas_con = [r for r in rutas if r.oficina_id]
    rutas_sin = [r for r in rutas if not r.oficina_id]
    print(f'   ✓ Con oficina: {len(rutas_con)}')
    print(f'   ⚠ Sin oficina: {len(rutas_sin)}')
    
    # 3. Verificar sociedades
    print('\n3. SOCIEDADES:')
    sociedades = Sociedad.query.all()
    print(f'   Total: {len(sociedades)}')
    for s in sociedades[:3]:
        print(f'   ✓ {s.nombre}')
    
    # 4. Verificar responsables disponibles
    print('\n4. RESPONSABLES DISPONIBLES:')
    responsables = Usuario.query.filter(
        Usuario.rol.in_(['dueno', 'gerente', 'secretaria']),
        Usuario.activo == True
    ).all()
    print(f'   Total: {len(responsables)}')
    for u in responsables[:3]:
        print(f'   ✓ {u.nombre} ({u.rol})')
    
    # 5. Test OficinaService
    print('\n5. TEST OFICINA SERVICE:')
    try:
        rutas_disp = OficinaService.get_rutas_sin_oficina()
        print(f'   ✓ get_rutas_sin_oficina(): {len(rutas_disp)} rutas')
        
        resumen = OficinaService.get_resumen_por_oficinas()
        totales = resumen.get('totales', {})
        print(f'   ✓ get_resumen_por_oficinas():')
        print(f'     - Oficinas: {totales.get("num_oficinas", 0)}')
        print(f'     - Rutas totales: {totales.get("total_rutas", 0)}')
        print(f'     - Sin asignar: {totales.get("rutas_sin_asignar", 0)}')
        print(f'     - Cartera: ${totales.get("total_cartera", 0):,.0f}')
    except Exception as e:
        print(f'   ✗ ERROR: {e}')
    
    # 6. Test crear oficina
    print('\n6. TEST CREAR OFICINA:')
    try:
        # Verificar si ya existe una oficina de prueba
        test_oficina = Oficina.query.filter_by(codigo='TEST-001').first()
        if test_oficina:
            print(f'   ✓ Oficina de prueba existe (ID:{test_oficina.id})')
        else:
            print('   ℹ No hay oficina de prueba')
            print('   → Puedes crearla desde http://localhost:5000/oficinas/nueva')
    except Exception as e:
        print(f'   ✗ ERROR: {e}')
    
    print('\n' + '='*60)
    print('   ✅ VERIFICACION COMPLETADA')
    print('='*60)
    print('\nURLs para probar:')
    print('  • Lista:   http://localhost:5000/oficinas/')
    print('  • Nueva:   http://localhost:5000/oficinas/nueva')
    print('  • Menu:    Sidebar → Oficinas')
