"""
Routes principales - Diamante Pro
Contiene: Dashboard, Selección de ruta, Gestión de usuarios
"""
from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import Usuario, Cliente, Prestamo, Pago, Transaccion, Ruta, Oficina, db
from datetime import datetime, timedelta
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/dashboard')
@login_required
def dashboard():
    print(f"DEBUG DASHBOARD: current_user={current_user}, is_authenticated={current_user.is_authenticated}")
    # 1. Variables Base y Filtros
    hoy = datetime.now().date()
    hoy_str = hoy.strftime('%Y-%m-%d')
    usuario_id = current_user.id
    rol = current_user.rol
    nombre = current_user.nombre

    # Recuperar selección de sesión
    ruta_seleccionada_id = session.get('ruta_seleccionada_id')
    oficina_seleccionada_id = session.get('oficina_seleccionada_id')

    # Variables de entorno para filtros (evitar NameError)
    todas_las_rutas = Ruta.query.all()
    todas_las_oficinas = Oficina.query.all()
    ruta_seleccionada = Ruta.query.get(ruta_seleccionada_id) if ruta_seleccionada_id else None
    oficina_seleccionada = Oficina.query.get(oficina_seleccionada_id) if oficina_seleccionada_id else None
    
    rutas_oficina_ids = []
    if oficina_seleccionada_id:
        rs = Ruta.query.filter_by(oficina_id=oficina_seleccionada_id).all()
        rutas_oficina_ids = [r.id for r in rs]

    # 2. Lógica de Monedas (CRÍTICO PARA TU ERROR ANTERIOR)
    # Detectamos monedas activas en préstamos
    monedas_query = db.session.query(Prestamo.moneda).filter(
        Prestamo.estado == 'ACTIVO', Prestamo.moneda.isnot(None)
    ).distinct().all()
    
    monedas_activas = sorted(set(m[0] for m in monedas_query if m[0]))
    if not monedas_activas:
        monedas_activas = ['COP']

    simbolos_moneda = {'COP': '$', 'BRL': 'R$', 'USD': 'US$', 'PEN': 'S/', 'ARS': '$'}

    # 3. Consultas Generales
    # Definir query base según filtros
    query_prestamos = Prestamo.query.filter_by(estado='ACTIVO')
    
    if rol == 'cobrador':
        query_prestamos = query_prestamos.filter_by(cobrador_id=usuario_id)
    elif oficina_seleccionada_id and rutas_oficina_ids:
        query_prestamos = query_prestamos.filter(Prestamo.ruta_id.in_(rutas_oficina_ids))
    elif ruta_seleccionada_id:
        query_prestamos = query_prestamos.filter_by(ruta_id=ruta_seleccionada_id)
        
    prestamos_activos = query_prestamos.all()
    total_prestamos_activos = len(prestamos_activos)

    # 4. Estadísticas Derivadas (con margen de gracia de 2 días)
    prestamos_al_dia = sum(1 for p in prestamos_activos if p.cuotas_atrasadas <= 2)
    prestamos_atrasados = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 2)
    prestamos_mora = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 5) # Mora grave > 5
    
    capital_prestado = sum(p.monto_prestado for p in prestamos_activos)
    total_cartera = sum(p.saldo_actual for p in prestamos_activos)
    ganancia_esperada = total_cartera - capital_prestado

    # 5. Cálculos de HOY (Cobros y Gastos)
    pagos_hoy_query = Pago.query.join(Prestamo).filter(func.date(Pago.fecha_pago) == hoy)
    if rol == 'cobrador':
        pagos_hoy_query = pagos_hoy_query.filter(Prestamo.cobrador_id == usuario_id)
    
    pagos_hoy = pagos_hoy_query.all()
    total_cobrado_hoy = sum(p.monto for p in pagos_hoy)
    num_pagos_hoy = len(pagos_hoy)

    # Segregación por moneda (Cobrado Hoy)
    cobrado_hoy_por_moneda = {}
    for p in pagos_hoy:
        m = (p.prestamo.moneda if p.prestamo else 'COP') or 'COP'
        cobrado_hoy_por_moneda[m] = cobrado_hoy_por_moneda.get(m, 0) + float(p.monto)

    # Gastos de Hoy
    gastos_hoy_query = Transaccion.query.filter(
        Transaccion.naturaleza == 'EGRESO',
        func.date(Transaccion.fecha) == hoy
    ).all()
    
    total_gastos_hoy = 0
    gastos_hoy_por_moneda = {}
    for g in gastos_hoy_query:
        m = g.moneda or 'COP'
        gastos_hoy_por_moneda[m] = gastos_hoy_por_moneda.get(m, 0) + float(g.monto)
        total_gastos_hoy += float(g.monto)

    # Balances
    balance_dia_por_moneda = {}
    for m in monedas_activas:
        balance_dia_por_moneda[m] = cobrado_hoy_por_moneda.get(m, 0) - gastos_hoy_por_moneda.get(m, 0)

    # 6. Gráficos 7 Días
    cobros_ultimos_7_dias = []
    labels_7_dias = []
    cobros_7_dias_por_moneda = {}
    fecha_inicio = hoy - timedelta(days=6)

    for i in range(7):
        fecha = fecha_inicio + timedelta(days=i)
        
        # Query pagos del dia 'fecha'
        q_dia = Pago.query.join(Prestamo).filter(func.date(Pago.fecha_pago) == fecha)
        if rol == 'cobrador':
            q_dia = q_dia.filter(Prestamo.cobrador_id == usuario_id)
        
        pagos_dia = q_dia.all()
        total_dia = sum(float(p.monto) for p in pagos_dia)
        
        cobros_ultimos_7_dias.append(total_dia)
        labels_7_dias.append(fecha.strftime('%d/%m'))
        
        # Llenar datos por moneda
        dia_moneda = {}
        for p in pagos_dia:
            m = (p.prestamo.moneda if p.prestamo else 'COP') or 'COP'
            dia_moneda[m] = dia_moneda.get(m, 0) + float(p.monto)
            
        for m in monedas_activas: # Asegurar que todas las monedas tengan dato
             if m not in cobros_7_dias_por_moneda:
                 cobros_7_dias_por_moneda[m] = [0] * (i) # Rellenar días previos si es nueva
             cobros_7_dias_por_moneda[m].append(dia_moneda.get(m, 0))

    # 7. Cálculos por moneda para KPIs (Eficacia, Mora, Utilidad)
    dia_semana_hoy = datetime.now().weekday()

    # Flujo de cobro esperado hoy por moneda
    flujo_cobro_por_moneda = {}
    for p in prestamos_activos:
        cobra_hoy = False
        if p.frecuencia == 'DIARIO' and dia_semana_hoy != 6:
            cobra_hoy = True
        elif p.frecuencia == 'DIARIO_LUNES_VIERNES' and dia_semana_hoy < 5:
            cobra_hoy = True
        elif p.frecuencia == 'BISEMANAL':
            cobra_hoy = True
        if cobra_hoy:
            m = p.moneda or 'COP'
            flujo_cobro_por_moneda[m] = flujo_cobro_por_moneda.get(m, 0) + float(p.valor_cuota)

    # Tasa de cobro por moneda
    tasa_cobro_por_moneda = {}
    for m in monedas_activas:
        por_cobrar = flujo_cobro_por_moneda.get(m, 0)
        cobrado = cobrado_hoy_por_moneda.get(m, 0)
        tasa_cobro_por_moneda[m] = (cobrado / por_cobrar * 100) if por_cobrar > 0 else 0

    # Mora por moneda (préstamos con más de 3 cuotas atrasadas)
    mora_por_moneda = {}
    monto_mora_por_moneda = {}
    for p in prestamos_activos:
        if p.cuotas_atrasadas > 3:
            m = p.moneda or 'COP'
            mora_por_moneda[m] = mora_por_moneda.get(m, 0) + 1
            monto_mora_por_moneda[m] = monto_mora_por_moneda.get(m, 0) + float(p.saldo_actual)

    # Ganancia esperada por moneda (cartera - capital)
    capital_por_moneda = {}
    cartera_por_moneda = {}
    for p in prestamos_activos:
        m = p.moneda or 'COP'
        capital_por_moneda[m] = capital_por_moneda.get(m, 0) + float(p.monto_prestado)
        cartera_por_moneda[m] = cartera_por_moneda.get(m, 0) + float(p.saldo_actual)

    ganancia_esperada_por_moneda = {}
    porcentaje_ganancia_por_moneda = {}
    for m in monedas_activas:
        cap = capital_por_moneda.get(m, 0)
        cart = cartera_por_moneda.get(m, 0)
        gan = cart - cap
        ganancia_esperada_por_moneda[m] = gan
        porcentaje_ganancia_por_moneda[m] = (gan / cap * 100) if cap > 0 else 0

    # 8. Listas Adicionales (Feed)
    ultimos_pagos = Pago.query.order_by(Pago.fecha_pago.desc()).limit(10).all()
    ultimos_gastos = Transaccion.query.filter(Transaccion.naturaleza == 'EGRESO').order_by(Transaccion.fecha.desc()).limit(10).all()
    prestamos_recientes = Prestamo.query.order_by(Prestamo.fecha_inicio.desc()).limit(5).all()

    # 9. Placeholders para variables que faltaban en tu código original
    # (Estas consultas deberás ajustarlas a tus modelos reales si existen)
    prestamos_pagados = Prestamo.query.filter_by(estado='PAGADO').count()
    prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO').count()
    riesgo_labels = ['BAJO', 'MEDIO', 'ALTO'] # Dummy data para evitar error
    riesgo_data = [10, 5, 2]
    
    # Variables "extra" que pedía el template
    clientes_vip = [] 
    capital_total_aportado = 0
    capital_invertido_activos = 0
    capital_disponible = 0
    solicitudes_pendientes = 0
    notificaciones = []
    mensajes_sin_leer = 0
    total_clientes = Cliente.query.count()

    # Variables Legacy para compatibilidad
    por_cobrar_hoy = 0 # Implementar lógica si se requiere
    proyeccion_manana = 0
    tasa_cobro_diaria = 0
    porcentaje_ganancia = 0
    
    # RETURN FINAL
    return render_template('dashboard_new.html',
        user=current_user,
        nombre=nombre,
        rol=rol,
        hoy_str=hoy_str,
        
        # Datos Fundamentales
        monedas_activas=monedas_activas,
        simbolos_moneda=simbolos_moneda,
        
        # Financieros
        total_cartera=total_cartera,
        capital_prestado=capital_prestado,
        ganancia_esperada=ganancia_esperada,
        total_cobrado_hoy=total_cobrado_hoy,
        total_gastos_hoy=total_gastos_hoy,
        num_pagos_hoy=num_pagos_hoy,
        
        # Estadísticas
        total_prestamos_activos=total_prestamos_activos,
        prestamos_al_dia=prestamos_al_dia,
        prestamos_atrasados=prestamos_atrasados,
        prestamos_mora=prestamos_mora,
        prestamos_pagados=prestamos_pagados,
        prestamos_cancelados=prestamos_cancelados,
        
        # Datos Segregados por Moneda
        cobrado_hoy_por_moneda=cobrado_hoy_por_moneda,
        gastos_hoy_por_moneda=gastos_hoy_por_moneda,
        balance_dia_por_moneda=balance_dia_por_moneda,
        flujo_cobro_por_moneda=flujo_cobro_por_moneda,
        tasa_cobro_por_moneda=tasa_cobro_por_moneda,
        mora_por_moneda=mora_por_moneda,
        monto_mora_por_moneda=monto_mora_por_moneda,
        ganancia_esperada_por_moneda=ganancia_esperada_por_moneda,
        porcentaje_ganancia_por_moneda=porcentaje_ganancia_por_moneda,
        
        # Gráficos
        cobros_ultimos_7_dias=cobros_ultimos_7_dias,
        labels_7_dias=labels_7_dias,
        cobros_7_dias_por_moneda=cobros_7_dias_por_moneda,
        riesgo_labels=riesgo_labels,
        riesgo_data=riesgo_data,
        
        # Listas / Feeds
        ultimos_pagos=ultimos_pagos,
        ultimos_gastos=ultimos_gastos,
        prestamos_recientes=prestamos_recientes,
        
        # Filtros
        todas_las_rutas=todas_las_rutas,
        todas_las_oficinas=todas_las_oficinas,
        ruta_seleccionada=ruta_seleccionada,
        oficina_seleccionada=oficina_seleccionada,
        
        # Variables Legacy/Extras (Para evitar NameError)
        clientes_vip=clientes_vip,
        capital_total_aportado=capital_total_aportado,
        capital_invertido_activos=capital_invertido_activos,
        capital_disponible=capital_disponible,
        solicitudes_pendientes=solicitudes_pendientes,
        notificaciones=notificaciones,
        mensajes_sin_leer=mensajes_sin_leer,
        total_clientes=total_clientes,
        por_cobrar_hoy=por_cobrar_hoy,
        proyeccion_manana=proyeccion_manana,
        tasa_cobro_diaria=tasa_cobro_diaria,
        porcentaje_ganancia=porcentaje_ganancia,
        
        # Compatibilidad variables BRL/COP viejas
        total_gastos_hoy_brl=gastos_hoy_por_moneda.get('BRL', 0),
        total_gastos_hoy_cop=gastos_hoy_por_moneda.get('COP', 0),
        balance_dia_brl=balance_dia_por_moneda.get('BRL', 0),
        balance_dia_cop=balance_dia_por_moneda.get('COP', 0)
    )

@main.route('/rutas/guardar', methods=['POST'])
@login_required
def rutas_guardar():
    nombre = request.form.get('nombre')
    cobrador_id = request.form.get('cobrador_id')
    sociedad_id = request.form.get('sociedad_id')
    moneda = request.form.get('moneda')
    descripcion = request.form.get('descripcion')
    if not nombre or not cobrador_id or not moneda:
        flash('Todos los campos obligatorios deben ser completados.', 'danger')
        return redirect(url_for('main.rutas_nueva'))
    nueva_ruta = Ruta(
        nombre=nombre,
        cobrador_id=cobrador_id,
        sociedad_id=sociedad_id if sociedad_id else None,
        moneda=moneda,
        descripcion=descripcion
    )
    db.session.add(nueva_ruta)
    db.session.commit()
    # Crear caja general de la ruta
    nueva_caja = CajaRuta(
        ruta_id=nueva_ruta.id,
        saldo=0,
        moneda=moneda
    )
    db.session.add(nueva_caja)
    db.session.commit()
    flash('Ruta creada correctamente.', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/seleccionar-ruta/<int:ruta_id>')
@login_required
def seleccionar_ruta(ruta_id):
    if session.get('rol') not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    session['ruta_seleccionada_id'] = ruta_id
    session.pop('oficina_seleccionada_id', None)
    return redirect(url_for('main.dashboard'))

@main.route('/seleccionar-oficina/<int:oficina_id>')
@login_required
def seleccionar_oficina(oficina_id):
    if session.get('rol') not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    session['oficina_seleccionada_id'] = oficina_id
    session.pop('ruta_seleccionada_id', None)
    return redirect(url_for('main.dashboard'))

@main.route('/ver-todas-rutas')
@login_required
def ver_todas_rutas():
    session.pop('ruta_seleccionada_id', None)
    session.pop('oficina_seleccionada_id', None)
    return redirect(url_for('main.dashboard'))

# --- GESTIÓN DE USUARIOS (requerido por base.html sidebar) ---

@main.route('/usuarios')
@login_required
def usuarios_lista():
    if current_user.rol not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    from werkzeug.security import generate_password_hash
    usuarios = Usuario.query.all()
    stats_usuarios = []
    for usuario in usuarios:
        num_cobros = Pago.query.filter_by(cobrador_id=usuario.id).count()
        total_cobrado = db.session.query(func.sum(Pago.monto)).filter_by(cobrador_id=usuario.id).scalar()
        total_cobrado = float(total_cobrado) if total_cobrado else 0
        stats_usuarios.append({
            'usuario': usuario,
            'num_cobros': num_cobros,
            'total_cobrado': total_cobrado
        })
    return render_template('usuarios_lista.html',
        stats_usuarios=stats_usuarios,
        nombre=current_user.nombre,
        rol=current_user.rol)

@main.route('/usuarios/nuevo')
@login_required
def usuarios_nuevo():
    if current_user.rol not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    return render_template('usuarios_nuevo.html',
        nombre=current_user.nombre,
        rol=current_user.rol)

# --- Ruta para editar usuario ---
@main.route('/usuarios/editar/<int:usuario_id>')
@login_required
def usuarios_editar(usuario_id):
    if current_user.rol not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template('usuarios_editar.html', usuario=usuario, nombre=current_user.nombre, rol=current_user.rol)

# --- Ruta para guardar nuevo usuario ---
@main.route('/usuarios/guardar', methods=['POST'])
@login_required
def usuarios_guardar():
    if current_user.rol not in ['dueno', 'gerente']:
        return redirect(url_for('main.dashboard'))
    nombre = request.form.get('nombre')
    usuario_login = request.form.get('usuario')
    password = request.form.get('password')
    rol = request.form.get('rol')
    # Validación básica
    if not nombre or not usuario_login or not password or not rol:
        error = 'Todos los campos son obligatorios.'
        return render_template('usuarios_nuevo.html', error=error, nombre=current_user.nombre, rol=current_user.rol)
    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(usuario=usuario_login).first():
        error = 'El usuario ya existe.'
        return render_template('usuarios_nuevo.html', error=error, nombre=current_user.nombre, rol=current_user.rol)
    # Crear usuario
    from werkzeug.security import generate_password_hash
    nuevo_usuario = Usuario(
        nombre=nombre,
        usuario=usuario_login,
        password=generate_password_hash(password),
        rol=rol
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    flash('Usuario creado exitosamente.', 'success')
    return redirect(url_for('main.usuarios_lista'))