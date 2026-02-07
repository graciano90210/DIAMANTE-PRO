"""
Servicio centralizado de Cajas - Diamante Pro
Maneja: auto-creación, cálculo de saldo cobrador, y traslados entre cajas
"""
from datetime import datetime
from ..models import CajaRuta, CajaDueno, Ruta, Usuario, Transaccion, Pago, Prestamo, db
from sqlalchemy import func


def asegurar_caja_ruta(ruta):
    """Auto-crea CajaRuta si no existe para una ruta dada."""
    caja = CajaRuta.query.filter_by(ruta_id=ruta.id).first()
    if not caja:
        caja = CajaRuta(ruta_id=ruta.id, saldo=0, moneda=ruta.moneda or 'COP')
        db.session.add(caja)
        db.session.flush()
    return caja


def asegurar_cajas_dueno(usuario_id):
    """Auto-crea CajaDueno para cada moneda activa en el sistema."""
    monedas_activas = db.session.query(Ruta.moneda).filter(
        Ruta.activo == True, Ruta.moneda.isnot(None)
    ).distinct().all()
    monedas = set(m[0] for m in monedas_activas if m[0])
    if not monedas:
        monedas = {'COP'}

    cajas_existentes = CajaDueno.query.filter_by(usuario_id=usuario_id).all()
    monedas_existentes = {c.moneda for c in cajas_existentes}

    for moneda in monedas:
        if moneda not in monedas_existentes:
            caja = CajaDueno(usuario_id=usuario_id, saldo=0, moneda=moneda)
            db.session.add(caja)

    db.session.flush()
    return CajaDueno.query.filter_by(usuario_id=usuario_id).all()


def asegurar_todas_las_cajas_ruta():
    """Verifica que todas las rutas activas tengan CajaRuta."""
    rutas_activas = Ruta.query.filter_by(activo=True).all()
    for ruta in rutas_activas:
        caja = CajaRuta.query.filter_by(ruta_id=ruta.id).first()
        if not caja:
            caja = CajaRuta(ruta_id=ruta.id, saldo=0, moneda=ruta.moneda or 'COP')
            db.session.add(caja)
    db.session.flush()


def calcular_saldo_cobrador(cobrador_id, moneda=None):
    """
    Calcula el saldo acumulativo histórico en efectivo de un cobrador.
    Balance = Cobros + Traslados_Recibidos - Gastos - Prestamos_Otorgados - Traslados_Enviados
    """
    # Cobros (pagos recibidos como cobrador)
    query_cobros = db.session.query(func.coalesce(func.sum(Pago.monto), 0))
    query_cobros = query_cobros.filter(Pago.cobrador_id == cobrador_id)
    if moneda:
        query_cobros = query_cobros.join(Prestamo).filter(Prestamo.moneda == moneda)
    cobros = float(query_cobros.scalar())

    # Traslados recibidos
    q_traslados_rec = db.session.query(
        func.coalesce(func.sum(Transaccion.monto), 0)
    ).filter(
        Transaccion.usuario_destino_id == cobrador_id,
        Transaccion.naturaleza == 'TRASLADO'
    )
    if moneda:
        q_traslados_rec = q_traslados_rec.filter(Transaccion.moneda == moneda)
    traslados_recibidos = float(q_traslados_rec.scalar())

    # Gastos
    q_gastos = db.session.query(
        func.coalesce(func.sum(Transaccion.monto), 0)
    ).filter(
        Transaccion.usuario_origen_id == cobrador_id,
        Transaccion.naturaleza == 'EGRESO'
    )
    if moneda:
        q_gastos = q_gastos.filter(Transaccion.moneda == moneda)
    gastos = float(q_gastos.scalar())

    # Prestamos otorgados (monto_prestado = dinero que sale de la caja del cobrador)
    q_prestamos = db.session.query(
        func.coalesce(func.sum(Prestamo.monto_prestado), 0)
    ).filter(Prestamo.cobrador_id == cobrador_id)
    if moneda:
        q_prestamos = q_prestamos.filter(Prestamo.moneda == moneda)
    prestamos = float(q_prestamos.scalar())

    # Traslados enviados
    q_traslados_env = db.session.query(
        func.coalesce(func.sum(Transaccion.monto), 0)
    ).filter(
        Transaccion.usuario_origen_id == cobrador_id,
        Transaccion.naturaleza == 'TRASLADO'
    )
    if moneda:
        q_traslados_env = q_traslados_env.filter(Transaccion.moneda == moneda)
    traslados_enviados = float(q_traslados_env.scalar())

    balance = cobros + traslados_recibidos - gastos - prestamos - traslados_enviados

    return {
        'cobros': cobros,
        'traslados_recibidos': traslados_recibidos,
        'gastos': gastos,
        'prestamos_otorgados': prestamos,
        'traslados_enviados': traslados_enviados,
        'balance': balance
    }


def ejecutar_traslado(tipo_origen, origen_id, tipo_destino, destino_id,
                       monto, moneda, descripcion, usuario_autorizador_id):
    """
    Ejecuta un traslado entre cualquier combinación de cajas.

    tipo_origen / tipo_destino: 'DUENO' | 'RUTA' | 'COBRADOR'
    origen_id / destino_id:
        - CajaDueno.id si tipo=DUENO
        - Ruta.id si tipo=RUTA
        - Usuario.id si tipo=COBRADOR

    Returns: Transaccion creada
    Raises: ValueError si la validación falla
    """
    if monto <= 0:
        raise ValueError('El monto debe ser mayor a cero')

    # --- Resolver origen ---
    desc_origen = ''
    usuario_origen_id = usuario_autorizador_id
    ruta_origen_id_val = None
    caja_dueno_origen_id_val = None

    if tipo_origen == 'DUENO':
        caja = CajaDueno.query.get(origen_id)
        if not caja:
            raise ValueError('Caja del dueño no encontrada')
        if caja.moneda != moneda:
            raise ValueError(f'Moneda de caja origen ({caja.moneda}) no coincide con {moneda}')
        if caja.saldo < monto:
            raise ValueError(f'Saldo insuficiente en Caja Dueño. Disponible: {caja.saldo:,.2f}')
        caja.saldo -= monto
        usuario_origen_id = caja.usuario_id
        caja_dueno_origen_id_val = caja.id
        usuario = Usuario.query.get(caja.usuario_id)
        desc_origen = f'Caja Dueño ({usuario.nombre if usuario else "?"} - {caja.moneda})'

    elif tipo_origen == 'RUTA':
        caja = CajaRuta.query.filter_by(ruta_id=origen_id).first()
        if not caja:
            raise ValueError('Caja de ruta no encontrada')
        if caja.moneda != moneda:
            raise ValueError(f'Moneda de caja origen ({caja.moneda}) no coincide con {moneda}')
        if caja.saldo < monto:
            raise ValueError(f'Saldo insuficiente en Caja Ruta. Disponible: {caja.saldo:,.2f}')
        caja.saldo -= monto
        ruta = Ruta.query.get(origen_id)
        desc_origen = f'Ruta: {ruta.nombre}' if ruta else f'Ruta #{origen_id}'
        ruta_origen_id_val = origen_id
        if ruta and ruta.cobrador_id:
            usuario_origen_id = ruta.cobrador_id

    elif tipo_origen == 'COBRADOR':
        cobrador = Usuario.query.get(origen_id)
        if not cobrador:
            raise ValueError('Cobrador no encontrado')
        saldo_info = calcular_saldo_cobrador(origen_id, moneda)
        if saldo_info['balance'] < monto:
            raise ValueError(f'Saldo insuficiente del cobrador. Balance: {saldo_info["balance"]:,.2f}')
        desc_origen = f'Cobrador: {cobrador.nombre}'
        usuario_origen_id = origen_id

    # --- Resolver destino ---
    desc_destino = ''
    usuario_destino_id = usuario_autorizador_id
    ruta_destino_id_val = None
    caja_dueno_destino_id_val = None

    if tipo_destino == 'DUENO':
        caja = CajaDueno.query.get(destino_id)
        if not caja:
            raise ValueError('Caja del dueño destino no encontrada')
        if caja.moneda != moneda:
            raise ValueError(f'Moneda de caja destino ({caja.moneda}) no coincide con {moneda}')
        caja.saldo += monto
        usuario_destino_id = caja.usuario_id
        caja_dueno_destino_id_val = caja.id
        usuario = Usuario.query.get(caja.usuario_id)
        desc_destino = f'Caja Dueño ({usuario.nombre if usuario else "?"} - {caja.moneda})'

    elif tipo_destino == 'RUTA':
        caja = CajaRuta.query.filter_by(ruta_id=destino_id).first()
        if not caja:
            raise ValueError('Caja de ruta destino no encontrada')
        if caja.moneda != moneda:
            raise ValueError(f'Moneda de caja destino ({caja.moneda}) no coincide con {moneda}')
        caja.saldo += monto
        ruta = Ruta.query.get(destino_id)
        desc_destino = f'Ruta: {ruta.nombre}' if ruta else f'Ruta #{destino_id}'
        ruta_destino_id_val = destino_id
        if ruta and ruta.cobrador_id:
            usuario_destino_id = ruta.cobrador_id

    elif tipo_destino == 'COBRADOR':
        cobrador = Usuario.query.get(destino_id)
        if not cobrador:
            raise ValueError('Cobrador destino no encontrado')
        desc_destino = f'Cobrador: {cobrador.nombre}'
        usuario_destino_id = destino_id

    # --- Crear Transacción ---
    concepto = f'{tipo_origen}_A_{tipo_destino}'
    desc_final = f'Traslado de {desc_origen} a {desc_destino}'
    if descripcion:
        desc_final += f'. {descripcion}'

    transaccion = Transaccion(
        naturaleza='TRASLADO',
        concepto=concepto,
        descripcion=desc_final,
        monto=monto,
        moneda=moneda,
        fecha=datetime.now(),
        usuario_origen_id=usuario_origen_id,
        usuario_destino_id=usuario_destino_id,
        ruta_origen_id=ruta_origen_id_val,
        ruta_destino_id=ruta_destino_id_val,
        caja_dueno_origen_id=caja_dueno_origen_id_val,
        caja_dueno_destino_id=caja_dueno_destino_id_val
    )

    db.session.add(transaccion)
    return transaccion
