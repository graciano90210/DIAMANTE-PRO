from app import create_app, db
from app.models import Cliente, Ruta
from datetime import datetime

app = create_app()

# Crear 3 clientes para la ruta de Tasmania
clientes_data = [
    {
        'nombre': 'María Fernanda López',
        'documento': '43218765',
        'telefono': '3201234567',
        'whatsapp_codigo_pais': '57',
        'whatsapp_numero': '3201234567',
        'documento_negocio': 'CC-987654',
        'direccion_negocio': 'Calle 45 #23-15, Local 3, Barrio Centro',
        'gps_latitud': 6.2442,
        'gps_longitud': -75.5812,
        'es_vip': False
    },
    {
        'nombre': 'Carlos Alberto Ramírez',
        'documento': '71234890',
        'telefono': '3157894561',
        'whatsapp_codigo_pais': '57',
        'whatsapp_numero': '3157894561',
        'documento_negocio': 'RUT-456789123',
        'direccion_negocio': 'Carrera 52 #38-20, Plaza de Mercado',
        'gps_latitud': 6.2514,
        'gps_longitud': -75.5736,
        'es_vip': True  # Cliente VIP - tasa 15%
    },
    {
        'nombre': 'Ana Lucía Martínez',
        'documento': '39876543',
        'telefono': '3009876543',
        'whatsapp_codigo_pais': '57',
        'whatsapp_numero': '3009876543',
        'documento_negocio': '',
        'direccion_negocio': 'Avenida 80 #12-34, Tienda La Esperanza',
        'gps_latitud': 6.2398,
        'gps_longitud': -75.5890,
        'es_vip': False
    }
]

with app.app_context():
    print("🎯 Registrando 3 clientes para ruta de Tasmania...")
    print("-" * 50)
    
    for cliente_data in clientes_data:
        # Verificar si ya existe
        existe = Cliente.query.filter_by(documento=cliente_data['documento']).first()
        
        if existe:
            print(f"⚠️  {cliente_data['nombre']} ya existe (Doc: {cliente_data['documento']})")
        else:
            # Crear nuevo cliente
            nuevo_cliente = Cliente(
                nombre=cliente_data['nombre'],
                documento=cliente_data['documento'],
                telefono=cliente_data['telefono'],
                whatsapp_codigo_pais=cliente_data['whatsapp_codigo_pais'],
                whatsapp_numero=cliente_data['whatsapp_numero'],
                documento_negocio=cliente_data['documento_negocio'],
                direccion_negocio=cliente_data['direccion_negocio'],
                gps_latitud=cliente_data['gps_latitud'],
                gps_longitud=cliente_data['gps_longitud'],
                es_vip=cliente_data['es_vip'],
                fecha_registro=datetime.now()
            )
            
            db.session.add(nuevo_cliente)
            
            vip_badge = "⭐ VIP" if cliente_data['es_vip'] else ""
            print(f"✅ {cliente_data['nombre']} {vip_badge}")
            print(f"   Doc: {cliente_data['documento']}")
            print(f"   Tel: {cliente_data['telefono']}")
            print(f"   Negocio: {cliente_data['direccion_negocio']}")
            print()
    
    db.session.commit()
    
    print("-" * 50)
    print("✅ CLIENTES REGISTRADOS EXITOSAMENTE")
    print()
    print("📋 Resumen:")
    print(f"   Total clientes: {Cliente.query.count()}")
    print(f"   Clientes VIP: {Cliente.query.filter_by(es_vip=True).count()}")
    print()
    print("🎯 Ahora Tasmania puede crear préstamos para estos clientes!")
