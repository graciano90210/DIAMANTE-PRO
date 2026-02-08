"""
Script para poblar la base de datos con datos de prueba realistas
- 21 usuarios (20 cobradores + 1 secretaria)
- 4 oficinas internacionales (Brasil, Colombia, Perú, Ecuador)
- 5 rutas por oficina (20 rutas totales)
- 5 clientes por ruta (100 clientes totales)
- 3 meses de movimientos (créditos, abonos, gastos)
- Verificar que usuario 'admin' tenga rol 'dueno'
"""

import sys
import os
from datetime import datetime, timedelta
from random import randint, choice, uniform, randrange
from decimal import Decimal

# Importar la aplicación
sys.path.append(os.getcwd())
from app import create_app, db
from app.models import (
    Usuario, Oficina, Ruta, Cliente, Prestamo, Pago, 
    Transaccion, CajaRuta, CajaDueno, AporteCapital, Sociedad
)

# ==================== DATOS REALISTAS ====================

# Nombres latinos realistas
NOMBRES_MASCULINOS = [
    "Carlos", "José", "Luis", "Miguel", "Juan", "Pedro", "Diego", "Fernando",
    "Roberto", "Antonio", "Manuel", "Francisco", "Rafael", "Andrés", "Jorge",
    "Ricardo", "Alberto", "Sergio", "Javier", "Daniel", "Alejandro", "Pablo",
    "Gustavo", "Raúl", "Héctor", "Óscar", "Víctor", "Eduardo", "Ramón", "Arturo"
]

NOMBRES_FEMENINOS = [
    "María", "Ana", "Carmen", "Rosa", "Lucía", "Isabel", "Patricia", "Laura",
    "Sofía", "Elena", "Gabriela", "Valentina", "Camila", "Daniela", "Andrea",
    "Carolina", "Fernanda", "Mariana", "Claudia", "Beatriz", "Silvia", "Teresa"
]

APELLIDOS = [
    "García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez",
    "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Cruz", "Morales",
    "Reyes", "Jiménez", "Hernández", "Ruiz", "Mendoza", "Castro", "Vargas",
    "Ortiz", "Silva", "Rojas", "Medina", "Gutiérrez", "Chávez", "Vega", "Santos"
]

# Tipos de negocios por país
TIPOS_NEGOCIO = {
    'Brasil': ['Padaria', 'Mercadinho', 'Lanchonete', 'Salão de Beleza', 'Barbearia', 
               'Farmácia', 'Papelaria', 'Açougue', 'Quitanda', 'Loja de Roupas'],
    'Colombia': ['Tienda', 'Panadería', 'Peluquería', 'Restaurante', 'Ferretería',
                 'Droguería', 'Papelería', 'Carnicería', 'Frutería', 'Boutique'],
    'Perú': ['Bodega', 'Panadería', 'Peluquería', 'Restaurante', 'Ferretería',
             'Botica', 'Librería', 'Carnicería', 'Frutería', 'Tienda de Ropa'],
    'Ecuador': ['Tienda', 'Panadería', 'Peluquería', 'Restaurante', 'Ferretería',
                'Farmacia', 'Papelería', 'Carnicería', 'Frutería', 'Boutique']
}

# Calles típicas por país
CALLES = {
    'Brasil': ['Rua das Flores', 'Av. Paulista', 'Rua São João', 'Av. Brasil', 'Rua da Paz'],
    'Colombia': ['Calle 10', 'Carrera 15', 'Avenida Bolívar', 'Calle Real', 'Carrera 7'],
    'Perú': ['Jr. Lima', 'Av. Arequipa', 'Calle Cusco', 'Jr. Puno', 'Av. La Marina'],
    'Ecuador': ['Calle Quito', 'Av. Amazonas', 'Calle Guayaquil', 'Av. 10 de Agosto', 'Calle Sucre']
}

# Configuración de oficinas
OFICINAS_CONFIG = [
    {
        'nombre': 'Oficina Brasil',
        'pais': 'Brasil',
        'ciudad': 'São Paulo',
        'moneda': 'BRL',
        'simbolo': 'R$',
        'codigo': 'BR-SP'
    },
    {
        'nombre': 'Oficina Colombia',
        'pais': 'Colombia',
        'ciudad': 'Bogotá',
        'moneda': 'COP',
        'simbolo': '$',
        'codigo': 'CO-BOG'
    },
    {
        'nombre': 'Oficina Perú',
        'pais': 'Perú',
        'ciudad': 'Lima',
        'moneda': 'PEN',
        'simbolo': 'S/',
        'codigo': 'PE-LIM'
    },
    {
        'nombre': 'Oficina Ecuador',
        'pais': 'Ecuador',
        'ciudad': 'Quito',
        'moneda': 'USD',
        'simbolo': '$',
        'codigo': 'EC-UIO'
    }
]

# ==================== FUNCIONES AUXILIARES ====================

def generar_nombre_completo(genero='M'):
    """Genera un nombre completo realista"""
    if genero == 'M':
        nombre = choice(NOMBRES_MASCULINOS)
    else:
        nombre = choice(NOMBRES_FEMENINOS)
    
    apellido1 = choice(APELLIDOS)
    apellido2 = choice(APELLIDOS)
    return f"{nombre} {apellido1} {apellido2}"

def generar_documento(pais):
    """Genera un documento según el país"""
    if pais == 'Brasil':
        # CPF: 000.000.000-00
        return f"{randint(100,999)}.{randint(100,999)}.{randint(100,999)}-{randint(10,99)}"
    elif pais == 'Colombia':
        # Cédula: 1000000000
        return str(randint(10000000, 99999999))
    elif pais == 'Perú':
        # DNI: 00000000
        return str(randint(10000000, 99999999))
    else:  # Ecuador
        # Cédula: 1000000000
        return str(randint(1000000000, 1999999999))

def generar_telefono(pais):
    """Genera un teléfono según el país"""
    if pais == 'Brasil':
        return f"(11) 9{randint(1000,9999)}-{randint(1000,9999)}"
    elif pais == 'Colombia':
        return f"300{randint(1000000,9999999)}"
    elif pais == 'Perú':
        return f"9{randint(10000000,99999999)}"
    else:  # Ecuador
        return f"09{randint(10000000,99999999)}"

def generar_direccion(pais):
    """Genera una dirección según el país"""
    calle = choice(CALLES[pais])
    numero = randint(100, 999)
    return f"{calle} #{numero}"

def generar_email(nombre):
    """Genera un email basado en el nombre"""
    nombre_limpio = nombre.lower().replace(' ', '.').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    dominios = ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com']
    return f"{nombre_limpio}{randint(1,99)}@{choice(dominios)}"

def calcular_fecha_aleatoria(dias_atras_min, dias_atras_max):
    """Calcula una fecha aleatoria en el pasado"""
    dias_atras = randint(dias_atras_min, dias_atras_max)
    return datetime.now() - timedelta(days=dias_atras)

# ==================== FUNCIONES PRINCIPALES ====================

def limpiar_movimientos():
    """Limpia movimientos y préstamos previos para empezar de cero"""
    print("\n🧹 Limpiando movimientos y préstamos previos...")
    
    try:
        # Eliminar en orden para respetar las foreign keys
        num_transacciones = Transaccion.query.delete()
        num_pagos = Pago.query.delete()
        num_prestamos = Prestamo.query.delete()
        num_aportes = AporteCapital.query.delete()
        
        db.session.commit()
        
        print(f"   ✅ {num_transacciones} transacciones eliminadas")
        print(f"   ✅ {num_pagos} pagos eliminados")
        print(f"   ✅ {num_prestamos} préstamos eliminados")
        print(f"   ✅ {num_aportes} aportes eliminados")
        print("   ✅ Base de datos lista para nueva simulación")
        
    except Exception as e:
        print(f"   ⚠️  Error al limpiar: {e}")
        db.session.rollback()

def verificar_y_actualizar_admin():
    """Verifica que el usuario admin tenga rol 'dueno'"""
    print("\n🔍 Verificando usuario admin...")
    admin = Usuario.query.filter_by(usuario='admin').first()
    
    if admin:
        if admin.rol != 'dueno':
            print(f"   ⚠️  Admin tenía rol '{admin.rol}', cambiando a 'dueno'...")
            admin.rol = 'dueno'
            db.session.commit()
            print("   ✅ Rol actualizado correctamente")
        else:
            print(f"   ✅ Admin ya tiene rol 'dueno'")
    else:
        print("   ⚠️  Usuario admin no existe, creándolo...")
        admin = Usuario(
            nombre='Administrador Principal',
            usuario='admin',
            rol='dueno',
            activo=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("   ✅ Usuario admin creado con rol 'dueno'")
    
    return admin

def crear_usuarios():
    """Crea 20 cobradores y 1 secretaria (idempotente)"""
    print("\n👥 Creando usuarios...")
    usuarios_creados = []
    
    # Crear 1 secretaria
    print("   📋 Verificando secretaria...")
    secretaria = Usuario.query.filter_by(usuario='secretaria').first()
    if not secretaria:
        secretaria = Usuario(
            nombre=generar_nombre_completo('F'),
            usuario=f"secretaria",
            rol='secretaria',
            activo=True
        )
        secretaria.set_password('secretaria123')
        db.session.add(secretaria)
        db.session.commit()
        print(f"      ✅ Secretaria creada: {secretaria.nombre}")
    else:
        print(f"      ℹ️  Secretaria ya existe: {secretaria.nombre}")
    usuarios_creados.append(secretaria)
    
    # Crear 20 cobradores
    print("   💼 Verificando 20 cobradores...")
    for i in range(1, 21):
        cobrador = Usuario.query.filter_by(usuario=f"cobrador{i}").first()
        if not cobrador:
            cobrador = Usuario(
                nombre=generar_nombre_completo('M'),
                usuario=f"cobrador{i}",
                rol='cobrador',
                activo=True
            )
            cobrador.set_password(f'cobrador{i}123')
            db.session.add(cobrador)
            db.session.commit()
            if i % 5 == 0:
                print(f"      ✅ {i} cobradores verificados...")
        else:
            if i % 5 == 0:
                print(f"      ℹ️  {i} cobradores verificados (algunos ya existían)...")
        usuarios_creados.append(cobrador)
    
    print(f"   ✅ Total: {len(usuarios_creados)} usuarios disponibles")
    return usuarios_creados

def crear_oficinas(admin):
    """Crea 4 oficinas internacionales (idempotente)"""
    print("\n🏢 Verificando oficinas internacionales...")
    oficinas_creadas = []
    
    for config in OFICINAS_CONFIG:
        oficina = Oficina.query.filter_by(nombre=config['nombre']).first()
        if not oficina:
            oficina = Oficina(
                nombre=config['nombre'],
                codigo=config['codigo'],
                descripcion=f"Oficina principal en {config['ciudad']}",
                direccion=generar_direccion(config['pais']),
                ciudad=config['ciudad'],
                pais=config['pais'],
                responsable_id=admin.id,
                telefono_oficina=generar_telefono(config['pais']),
                email_oficina=f"oficina.{config['codigo'].lower()}@diamantepro.com",
                activo=True,
                meta_cobro_diario=5000.0,
                meta_prestamos_mes=50000.0
            )
            db.session.add(oficina)
            db.session.commit()
            print(f"   ✅ {oficina.nombre} creada ({config['pais']}) - {config['moneda']}")
        else:
            print(f"   ℹ️  {oficina.nombre} ya existe ({config['pais']}) - {config['moneda']}")
        oficinas_creadas.append(oficina)
    
    print(f"   ✅ Total: {len(oficinas_creadas)} oficinas disponibles")
    return oficinas_creadas

def crear_rutas(oficinas, cobradores):
    """Crea 5 rutas por cada oficina (20 rutas totales) - idempotente"""
    print("\n🛣️  Verificando rutas...")
    rutas_creadas = []
    cobrador_idx = 0
    
    for oficina in oficinas:
        config = next(c for c in OFICINAS_CONFIG if c['nombre'] == oficina.nombre)
        print(f"   📍 Rutas para {oficina.nombre}:")
        
        for i in range(1, 6):
            nombre_ruta = f"Ruta {config['codigo']}-{i}"
            ruta = Ruta.query.filter_by(nombre=nombre_ruta).first()
            
            if not ruta:
                ruta = Ruta(
                    nombre=nombre_ruta,
                    cobrador_id=cobradores[cobrador_idx].id,
                    oficina_id=oficina.id,
                    pais=config['pais'],
                    moneda=config['moneda'],
                    simbolo_moneda=config['simbolo'],
                    activo=True,
                    descripcion=f"Ruta {i} de {config['ciudad']}"
                )
                db.session.add(ruta)
                db.session.flush()  # Para obtener el ID de la ruta
                
                # Crear caja para la ruta
                caja_ruta = CajaRuta(
                    ruta=ruta,
                    saldo=0.0,
                    moneda=config['moneda']
                )
                db.session.add(caja_ruta)
                db.session.commit()
                
                print(f"      ✅ {ruta.nombre} creada - Cobrador: {cobradores[cobrador_idx].nombre}")
            else:
                print(f"      ℹ️  {ruta.nombre} ya existe - Cobrador: {ruta.cobrador.nombre}")
            
            rutas_creadas.append(ruta)
            cobrador_idx += 1
    
    print(f"   ✅ Total: {len(rutas_creadas)} rutas disponibles")
    return rutas_creadas

def crear_clientes(rutas):
    """Crea 5 clientes por cada ruta (100 clientes totales)"""
    print("\n👨‍💼 Creando clientes...")
    clientes_creados = []
    
    for ruta in rutas:
        config = next(c for c in OFICINAS_CONFIG if c['moneda'] == ruta.moneda)
        
        for i in range(1, 6):
            genero = choice(['M', 'F'])
            nombre = generar_nombre_completo(genero)
            tipo_negocio = choice(TIPOS_NEGOCIO[config['pais']])
            
            cliente = Cliente(
                nombre=nombre,
                documento=generar_documento(config['pais']),
                tipo_documento='CPF' if config['pais'] == 'Brasil' else 'CC',
                fecha_nacimiento=calcular_fecha_aleatoria(7300, 18250),  # 20-50 años
                telefono=generar_telefono(config['pais']),
                email=generar_email(nombre),
                whatsapp_codigo_pais='55' if config['pais'] == 'Brasil' else '57',
                whatsapp_numero=generar_telefono(config['pais']),
                direccion_negocio=generar_direccion(config['pais']),
                direccion_casa=generar_direccion(config['pais']),
                gps_latitud=uniform(-10, 10),
                gps_longitud=uniform(-80, -40),
                gps_latitud_casa=uniform(-10, 10),
                gps_longitud_casa=uniform(-80, -40),
                ruta_id=ruta.id,
                tipo_negocio=tipo_negocio,
                nombre_negocio=f"{tipo_negocio} {choice(APELLIDOS)}",
                antiguedad_negocio_meses=randint(6, 120),
                local_propio=choice([True, False]),
                dias_trabajo='L-S',
                hora_cobro_preferida=f"{randint(8,17):02d}:00",
                ingresos_diarios_estimados=uniform(100, 1000),
                gastos_mensuales_promedio=uniform(500, 3000),
                personas_a_cargo=randint(0, 5),
                estado_civil=choice(['SOLTERO', 'CASADO', 'UNION_LIBRE']),
                tiempo_residencia_meses=randint(12, 240),
                negocio_formalizado=choice([True, False]),
                tiene_comprobante_residencia=True,
                tipo_comprobante_residencia=choice(['LUZ', 'AGUA', 'INTERNET']),
                comprobante_a_nombre_propio=choice([True, False]),
                score_crediticio=randint(400, 900),
                nivel_riesgo=choice(['EXCELENTE', 'BUENO', 'REGULAR', 'NUEVO']),
                limite_credito_sugerido=uniform(500, 5000),
                es_vip=False,
                fecha_registro=calcular_fecha_aleatoria(90, 180)
            )
            db.session.add(cliente)
            clientes_creados.append(cliente)
        
        if len(clientes_creados) % 20 == 0:
            print(f"   ✅ {len(clientes_creados)} clientes creados...")
    
    db.session.commit()
    print(f"   ✅ Total: {len(clientes_creados)} clientes creados")
    return clientes_creados

def generar_movimientos(clientes, rutas, admin):
    """Genera 3 meses de movimientos (créditos, abonos, gastos)"""
    print("\n💰 Generando 3 meses de movimientos...")
    
    prestamos_creados = []
    pagos_creados = []
    transacciones_creadas = []
    
    # Para cada cliente, crear préstamos y pagos
    for cliente in clientes:
        ruta = next(r for r in rutas if r.id == cliente.ruta_id)
        config = next(c for c in OFICINAS_CONFIG if c['moneda'] == ruta.moneda)
        
        # Crear 1-2 préstamos por cliente en los últimos 3 meses
        num_prestamos = randint(1, 2)
        
        for p in range(num_prestamos):
            # Fecha del préstamo (entre 90 y 10 días atrás)
            fecha_prestamo = calcular_fecha_aleatoria(10, 90)
            
            # Monto del préstamo según la moneda
            if config['moneda'] == 'BRL':
                monto_prestado = uniform(500, 3000)
            elif config['moneda'] == 'COP':
                monto_prestado = uniform(200000, 1000000)
            elif config['moneda'] == 'PEN':
                monto_prestado = uniform(500, 3000)
            else:  # USD
                monto_prestado = uniform(100, 800)
            
            tasa_interes = 0.15 if cliente.es_vip else 0.20
            monto_a_pagar = monto_prestado * (1 + tasa_interes)
            numero_cuotas = randint(20, 60)
            valor_cuota = monto_a_pagar / numero_cuotas
            
            # Calcular cuántas cuotas se han pagado (entre 50% y 90% del tiempo transcurrido)
            dias_transcurridos = (datetime.now() - fecha_prestamo).days
            cuotas_esperadas = int(dias_transcurridos * 0.7)  # 70% de cumplimiento
            cuotas_pagadas = min(cuotas_esperadas, numero_cuotas)
            
            saldo_actual = monto_a_pagar - (cuotas_pagadas * valor_cuota)
            estado = 'CANCELADO' if cuotas_pagadas >= numero_cuotas else 'ACTIVO'
            
            prestamo = Prestamo(
                cliente_id=cliente.id,
                ruta_id=ruta.id,
                cobrador_id=ruta.cobrador_id,
                monto_prestado=round(monto_prestado, 2),
                tasa_interes=tasa_interes,
                monto_a_pagar=round(monto_a_pagar, 2),
                saldo_actual=round(max(0, saldo_actual), 2),
                valor_cuota=round(valor_cuota, 2),
                moneda=config['moneda'],
                frecuencia='DIARIO',
                numero_cuotas=numero_cuotas,
                cuotas_pagadas=cuotas_pagadas,
                cuotas_atrasadas=randint(0, 3),
                estado=estado,
                fecha_inicio=fecha_prestamo,
                fecha_fin_estimada=fecha_prestamo + timedelta(days=numero_cuotas),
                fecha_ultimo_pago=fecha_prestamo + timedelta(days=cuotas_pagadas) if cuotas_pagadas > 0 else None
            )
            db.session.add(prestamo)
            db.session.flush()  # Asegurar que el ID del préstamo esté disponible
            prestamos_creados.append(prestamo)
            
            # Crear transacción de préstamo (salida de caja)
            transaccion_prestamo = Transaccion(
                naturaleza='SALIDA',
                concepto='PRESTAMO',
                descripcion=f'Préstamo a {cliente.nombre}',
                monto=round(monto_prestado, 2),
                moneda=config['moneda'],
                fecha=fecha_prestamo,
                usuario_origen_id=admin.id,
                prestamo_id=prestamo.id,
                ruta_origen_id=ruta.id
            )
            db.session.add(transaccion_prestamo)
            transacciones_creadas.append(transaccion_prestamo)
            
            # Crear pagos para las cuotas pagadas
            for cuota in range(cuotas_pagadas):
                fecha_pago = fecha_prestamo + timedelta(days=cuota + 1)
                saldo_antes = monto_a_pagar - (cuota * valor_cuota)
                saldo_despues = saldo_antes - valor_cuota
                
                pago = Pago(
                    prestamo_id=prestamo.id,
                    cobrador_id=ruta.cobrador_id,
                    monto=round(valor_cuota, 2),
                    numero_cuotas_pagadas=1,
                    saldo_anterior=round(saldo_antes, 2),
                    saldo_nuevo=round(max(0, saldo_despues), 2),
                    fecha_pago=fecha_pago,
                    tipo_pago='NORMAL',
                    metodo_pago='EFECTIVO'
                )
                db.session.add(pago)
                pagos_creados.append(pago)
                
                # Crear transacción de cobro (entrada de caja)
                transaccion_cobro = Transaccion(
                    naturaleza='ENTRADA',
                    concepto='COBRO',
                    descripcion=f'Cobro cuota #{cuota+1} - {cliente.nombre}',
                    monto=round(valor_cuota, 2),
                    moneda=config['moneda'],
                    fecha=fecha_pago,
                    usuario_origen_id=ruta.cobrador_id,
                    prestamo_id=prestamo.id,
                    ruta_destino_id=ruta.id
                )
                db.session.add(transaccion_cobro)
                transacciones_creadas.append(transaccion_cobro)
        
        # Commit cada 10 clientes para evitar sobrecarga
        if len(prestamos_creados) % 10 == 0:
            db.session.commit()
            print(f"   ✅ {len(prestamos_creados)} préstamos procesados...")
    
    # Crear algunos gastos aleatorios
    print("   💸 Creando gastos operativos...")
    for ruta in rutas:
        config = next(c for c in OFICINAS_CONFIG if c['moneda'] == ruta.moneda)
        
        # 3-5 gastos por ruta en los últimos 3 meses
        for g in range(randint(3, 5)):
            fecha_gasto = calcular_fecha_aleatoria(10, 90)
            
            if config['moneda'] == 'BRL':
                monto_gasto = uniform(50, 300)
            elif config['moneda'] == 'COP':
                monto_gasto = uniform(20000, 150000)
            elif config['moneda'] == 'PEN':
                monto_gasto = uniform(50, 300)
            else:  # USD
                monto_gasto = uniform(10, 80)
            
            concepto_gasto = choice(['GASOLINA', 'MANTENIMIENTO', 'ALIMENTACION', 'PAPELERIA', 'OTROS'])
            
            transaccion_gasto = Transaccion(
                naturaleza='SALIDA',
                concepto=concepto_gasto,
                descripcion=f'Gasto operativo - {concepto_gasto}',
                monto=round(monto_gasto, 2),
                moneda=config['moneda'],
                fecha=fecha_gasto,
                usuario_origen_id=ruta.cobrador_id,
                ruta_origen_id=ruta.id
            )
            db.session.add(transaccion_gasto)
            transacciones_creadas.append(transaccion_gasto)
    
    db.session.commit()
    print(f"   ✅ {len(prestamos_creados)} préstamos creados")
    print(f"   ✅ {len(pagos_creados)} pagos registrados")
    print(f"   ✅ {len(transacciones_creadas)} transacciones generadas")

def crear_aportes_capital(admin, rutas):
    """Crea aportes de capital iniciales para cada ruta"""
    print("\n💵 Creando aportes de capital...")
    
    # Verificar si existe alguna sociedad, si no, crear una por defecto
    print("   🔍 Verificando sociedad...")
    sociedad = Sociedad.query.first()
    
    if not sociedad:
        print("   ⚠️  No existe ninguna sociedad, creando 'Diamante Pro International'...")
        sociedad = Sociedad(
            nombre='Diamante Pro International',
            descripcion='Sociedad principal para operaciones internacionales',
            activo=True
        )
        db.session.add(sociedad)
        db.session.flush()  # Obtener el ID de la sociedad
        print(f"   ✅ Sociedad creada: {sociedad.nombre} (ID: {sociedad.id})")
    else:
        print(f"   ℹ️  Usando sociedad existente: {sociedad.nombre} (ID: {sociedad.id})")
    
    aportes_creados = []
    
    for ruta in rutas:
        config = next(c for c in OFICINAS_CONFIG if c['moneda'] == ruta.moneda)
        
        # Aporte inicial según la moneda
        if config['moneda'] == 'BRL':
            monto_aporte = uniform(10000, 30000)
        elif config['moneda'] == 'COP':
            monto_aporte = uniform(5000000, 15000000)
        elif config['moneda'] == 'PEN':
            monto_aporte = uniform(10000, 30000)
        else:  # USD
            monto_aporte = uniform(2000, 8000)
        
        fecha_aporte = calcular_fecha_aleatoria(90, 120)
        
        aporte = AporteCapital(
            sociedad_id=sociedad.id,  # Asignar el ID de la sociedad
            nombre_aportante='Administrador Principal',
            monto=round(monto_aporte, 2),
            moneda=config['moneda'],
            tipo_aporte='EFECTIVO',
            fecha_aporte=fecha_aporte,
            descripcion=f'Capital inicial para {ruta.nombre}',
            registrado_por_id=admin.id,
            ruta_id=ruta.id
        )
        db.session.add(aporte)
        aportes_creados.append(aporte)
    
    db.session.commit()
    print(f"   ✅ {len(aportes_creados)} aportes de capital creados")

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal para ejecutar el seed"""
    print("=" * 60)
    print("🌟 SEED DATA - DIAMANTE PRO")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Preguntar si desea limpiar movimientos previos
            print("\n❓ ¿Desea limpiar movimientos y préstamos previos?")
            print("   Esto eliminará todos los préstamos, pagos, transacciones y aportes")
            print("   pero mantendrá usuarios, oficinas, rutas y clientes.")
            respuesta = input("   Escriba 'SI' para limpiar o presione Enter para continuar: ").strip().upper()
            
            if respuesta == 'SI':
                limpiar_movimientos()
            else:
                print("\n   ℹ️  Continuando sin limpiar movimientos previos...")
            
            # 1. Verificar y actualizar admin
            admin = verificar_y_actualizar_admin()
            
            # 2. Crear usuarios
            usuarios = crear_usuarios()
            cobradores = [u for u in usuarios if u.rol == 'cobrador']
            
            # 3. Crear oficinas
            oficinas = crear_oficinas(admin)
            
            # 4. Crear rutas
            rutas = crear_rutas(oficinas, cobradores)
            
            # 5. Crear clientes
            clientes = crear_clientes(rutas)
            
            # 6. Generar movimientos
            generar_movimientos(clientes, rutas, admin)
            
            # 7. Crear aportes de capital
            crear_aportes_capital(admin, rutas)
            
            print("\n" + "=" * 60)
            print("✅ SEED COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print(f"\n📊 RESUMEN:")
            print(f"   • Usuarios: {len(usuarios) + 1} (20 cobradores + 1 secretaria + 1 admin)")
            print(f"   • Oficinas: {len(oficinas)}")
            print(f"   • Rutas: {len(rutas)}")
            print(f"   • Clientes: {len(clientes)}")
            print(f"   • Préstamos: ~{len(clientes) * 1.5:.0f}")
            print(f"   • Movimientos: 3 meses de historial")
            print(f"\n🔐 CREDENCIALES:")
            print(f"   • Admin: usuario='admin', password='admin123', rol='dueno'")
            print(f"   • Secretaria: usuario='secretaria', password='secretaria123'")
            print(f"   • Cobradores: usuario='cobrador1-20', password='cobrador1-20123'")
            print("\n" + "=" * 60)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    main()
