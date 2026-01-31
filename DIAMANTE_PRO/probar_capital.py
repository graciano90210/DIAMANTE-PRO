from app import create_app, db
from app.models import Usuario, Sociedad, AporteCapital

# Inicializamos la app para tener acceso a la base de datos
app = create_app()

with app.app_context():
    print("💎 --- INICIANDO PRUEBA DE CAPITAL --- 💎")

    # 1. Asegurarnos de que existe un USUARIO (necesitamos un 'dueño' para registrar)
    usuario = Usuario.query.first()
    if not usuario:
        print("⚙️ No encontré usuarios. Creando uno de prueba...")
        usuario = Usuario(nombre="Juan Admin", usuario="admin", password="123", rol="dueno")
        db.session.add(usuario)
        db.session.commit()
        print(f"✅ Usuario creado: ID {usuario.id}")
    else:
        print(f"✅ Usando usuario existente: {usuario.nombre} (ID: {usuario.id})")

    # 2. Asegurarnos de que existe una SOCIEDAD
    sociedad = Sociedad.query.first()
    if not sociedad:
        print("⚙️ No encontré sociedades. Creando 'Sociedad Principal'...")
        sociedad = Sociedad(nombre="Sociedad Principal", nombre_socio="Juan Fernando")
        db.session.add(sociedad)
        db.session.commit()
        print(f"✅ Sociedad creada: ID {sociedad.id}")
    else:
        print(f"✅ Usando sociedad existente: {sociedad.nombre} (ID: {sociedad.id})")

    # 3. PROBAR LA RUTA (Simulamos que la App Móvil envía dinero)
    client = app.test_client()
    
    datos_inversion = {
        "sociedad_id": sociedad.id,
        "monto": 1000000,           # 1 Millón de prueba
        "nombre_aportante": "Juan Fernando",
        "usuario_id": usuario.id,
        "descripcion": "Inversión inicial de prueba",
        "moneda": "COP"
    }

    print("\n📨 Enviando inversión de prueba al sistema...")
    respuesta = client.post('/api/capital/nuevo', json=datos_inversion)

    # 4. RESULTADO
    if respuesta.status_code == 201:
        data = respuesta.get_json()
        print("\n🎉 ¡ÉXITO TOTAL, MI AMOR! 🎉")
        print(f"💰 Mensaje del sistema: {data['mensaje']}")
        print(f"📝 ID del Aporte: {data['id']}")
        print(f"💵 Monto Guardado: ${data['monto']:,.2f}")
    else:
        print("\n❌ Algo falló:")
        print(respuesta.get_json())

    print("\n-------------------------------------------")