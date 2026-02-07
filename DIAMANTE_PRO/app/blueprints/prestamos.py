"""
Blueprint de Préstamos - Diamante Pro
Maneja: CRUD de préstamos, cálculos, comprobantes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from datetime import datetime, timedelta
from ..models import Cliente, Prestamo, Pago, Ruta, Oficina, Usuario, db
from sqlalchemy import func
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

prestamos_bp = Blueprint('prestamos', __name__, url_prefix='/prestamos')


def login_required(f):
    """Decorador para requerir login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@prestamos_bp.route('/nuevo')
@login_required
def nuevo():
    """Formulario para nuevo préstamo"""
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    cobradores = Usuario.query.filter(Usuario.rol.in_(['admin', 'cobrador'])).all()
    return render_template(
        'prestamos_nuevo.html',
        clientes=clientes,
        cobradores=cobradores,
        fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
        nombre=session.get('nombre'),
        rol=session.get('rol')
    )


@prestamos_bp.route('/')
@login_required
def lista():
    """Lista de préstamos"""
    page = request.args.get('page', 1, type=int)
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')

    # Filtro base según el rol del usuario
    if rol in ['dueno', 'gerente']:
        # DUENO y GERENTE ven todos los préstamos
        filtro_usuario = True  # No filtrar por usuario
    else:
        # COBRADOR solo ve sus préstamos
        filtro_usuario = (Prestamo.cobrador_id == usuario_id)

    # Estadísticas agrupadas por moneda
    query_por_moneda = db.session.query(
        Prestamo.moneda,
        func.sum(Prestamo.monto_prestado).label('total_prestado'),
        func.sum(Prestamo.saldo_actual).label('total_cartera'),
        func.sum(Prestamo.monto_a_pagar - Prestamo.monto_prestado).label('ganancia_esperada')
    ).filter(
        Prestamo.estado == 'ACTIVO'
    )

    if filtro_usuario is not True:
        query_por_moneda = query_por_moneda.filter(filtro_usuario)

    query_por_moneda = query_por_moneda.group_by(Prestamo.moneda).all()

    # Crear diccionarios por moneda
    stats_por_moneda = {}
    for moneda, prestado, cartera, ganancia in query_por_moneda:
        stats_por_moneda[moneda] = {
            'total_prestado': prestado or 0,
            'total_cartera': cartera or 0,
            'ganancia_esperada': ganancia or 0
        }

    # Totales generales (para compatibilidad)
    total_prestado = sum(s['total_prestado'] for s in stats_por_moneda.values())
    total_cartera = sum(s['total_cartera'] for s in stats_por_moneda.values())
    ganancia_esperada = sum(s['ganancia_esperada'] for s in stats_por_moneda.values())

    clientes = Cliente.query.order_by(Cliente.nombre).all()
    cobradores = Usuario.query.filter(Usuario.rol.in_(['admin', 'cobrador'])).all()
    oficinas = Oficina.query.filter_by(activo=True).order_by(Oficina.nombre).all()
    rutas = Ruta.query.filter_by(activo=True).order_by(Ruta.nombre).all()

    # Obtener lista de préstamos según el rol
    query_prestamos = Prestamo.query.order_by(Prestamo.fecha_inicio.desc())
    if filtro_usuario is not True:
        query_prestamos = query_prestamos.filter(filtro_usuario)
    prestamos = query_prestamos.all()

    # Contar préstamos activos
    query_count_activos = Prestamo.query.filter_by(estado='ACTIVO')
    if filtro_usuario is not True:
        query_count_activos = query_count_activos.filter(filtro_usuario)
    prestamos_activos = query_count_activos.count()

    return render_template('prestamos_lista.html',
        clientes=clientes,
        cobradores=cobradores,
        prestamos=prestamos,
        prestamos_activos=prestamos_activos,
        fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
        nombre=session.get('nombre'),
        rol=rol,
        usuario_id=usuario_id,
        cliente_id_seleccionado=None,
        total_prestado=total_prestado,
        total_cartera=total_cartera,
        ganancia_esperada=ganancia_esperada,
        stats_por_moneda=stats_por_moneda,
        oficinas=oficinas,
        rutas=rutas)


@prestamos_bp.route('/guardar', methods=['POST'])
@login_required
def guardar():
    """Guardar nuevo préstamo"""
    try:
        # Validar campos requeridos
        cliente_id_str = request.form.get('cliente_id', '').strip()
        if not cliente_id_str:
            raise ValueError('Debe seleccionar un cliente')
        cliente_id = int(cliente_id_str)
        
        monto_prestado_str = request.form.get('monto_prestado', '').strip()
        if not monto_prestado_str:
            raise ValueError('Debe ingresar el monto a prestar')
        
        numero_cuotas_str = request.form.get('numero_cuotas', '').strip()
        if not numero_cuotas_str:
            raise ValueError('Debe ingresar el número de cuotas')
        
        cobrador_id_str = request.form.get('cobrador_id', '').strip()
        if not cobrador_id_str:
            # Si no hay cobrador seleccionado, usar el usuario actual
            cobrador_id_str = str(session.get('usuario_id', 1))
        
        # VALIDACIÓN: Verificar si el cliente ya tiene un préstamo activo
        prestamo_activo = Prestamo.query.filter_by(
            cliente_id=cliente_id,
            estado='ACTIVO'
        ).first()
        
        if prestamo_activo:
            clientes = Cliente.query.all()
            cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
            return render_template(
                'prestamos_nuevo.html',
                error=f'❌ Este cliente ya tiene un préstamo activo (#ID: {prestamo_activo.id}). No puede tener dos préstamos simultáneos.',
                clientes=clientes,
                cobradores=cobradores,
                nombre=session.get('nombre'),
                rol=session.get('rol')
            )

        monto_prestado = float(monto_prestado_str)
        tasa_interes = float(request.form.get('tasa_interes', '20'))
        numero_cuotas = int(numero_cuotas_str)
        monto_a_pagar = float(request.form.get('monto_a_pagar', str(monto_prestado * 1.2)))
        valor_cuota = float(request.form.get('valor_cuota', str(monto_a_pagar / numero_cuotas)))
        cobrador_id = int(cobrador_id_str)
        
        # Calcular fecha fin estimada
        fecha_inicio = datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d')
        frecuencia = request.form.get('frecuencia')
        
        if frecuencia == 'DIARIO':
            dias_totales = int(numero_cuotas * (7 / 6))
            fecha_fin = fecha_inicio + timedelta(days=dias_totales)
        elif frecuencia == 'DIARIO_LUNES_VIERNES':
            dias_totales = int(numero_cuotas * (7 / 5))
            fecha_fin = fecha_inicio + timedelta(days=dias_totales)
        elif frecuencia == 'BISEMANAL':
            dias_totales = (numero_cuotas * 7) // 2
            fecha_fin = fecha_inicio + timedelta(days=dias_totales)
        elif frecuencia == 'SEMANAL':
            fecha_fin = fecha_inicio + timedelta(weeks=numero_cuotas)
        elif frecuencia == 'QUINCENAL':
            fecha_fin = fecha_inicio + timedelta(days=numero_cuotas * 15)
        else:  # MENSUAL
            fecha_fin = fecha_inicio + timedelta(days=numero_cuotas * 30)
        
        # Obtener Ruta ID
        ruta_id = session.get('ruta_seleccionada_id')
        if not ruta_id:
            ruta = Ruta.query.filter_by(cobrador_id=cobrador_id).first()
            if ruta:
                ruta_id = ruta.id
            else:
                ruta = Ruta.query.first()
                ruta_id = ruta.id if ruta else 1
        
        # Crear préstamo
        nuevo_prestamo = Prestamo(
            cliente_id=cliente_id,
            ruta_id=ruta_id,
            cobrador_id=cobrador_id,
            monto_prestado=monto_prestado,
            tasa_interes=tasa_interes,
            monto_a_pagar=monto_a_pagar,
            saldo_actual=monto_a_pagar,
            valor_cuota=valor_cuota,
            moneda=request.form.get('moneda'),
            frecuencia=frecuencia,
            numero_cuotas=numero_cuotas,
            cuotas_pagadas=0,
            cuotas_atrasadas=0,
            estado='ACTIVO',
            fecha_inicio=fecha_inicio,
            fecha_fin_estimada=fecha_fin
        )
        
        db.session.add(nuevo_prestamo)
        db.session.commit()
        
        return redirect(url_for('prestamos.exito', prestamo_id=nuevo_prestamo.id))
        
    except Exception as e:
        db.session.rollback()
        clientes = Cliente.query.order_by(Cliente.nombre).all()
        cobradores = Usuario.query.filter(Usuario.rol.in_(['admin', 'cobrador'])).all()
        return render_template(
            'prestamos_nuevo.html',
            clientes=clientes,
            cobradores=cobradores,
            fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
            error=f'Error al crear préstamo: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol')
        )


@prestamos_bp.route('/ver/<int:prestamo_id>')
@login_required
def detalle(prestamo_id):
    """Ver detalle de un préstamo"""
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    pagos = Pago.query.filter_by(prestamo_id=prestamo_id).order_by(Pago.fecha_pago.desc()).all()
    
    return render_template('prestamo_detalle.html',
        prestamo=prestamo,
        pagos=pagos,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@prestamos_bp.route('/exito/<int:prestamo_id>')
@login_required
def exito(prestamo_id):
    """Página de éxito después de crear préstamo"""
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    cliente = prestamo.cliente
    cobrador = prestamo.cobrador
    
    whatsapp_url = f"https://wa.me/{cliente.whatsapp_completo}"
    
    return render_template('prestamo_exito.html',
        prestamo=prestamo,
        cliente=cliente,
        cobrador=cobrador,
        whatsapp_url=whatsapp_url,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@prestamos_bp.route('/comprobante-imagen/<int:prestamo_id>')
@login_required
def comprobante_imagen(prestamo_id):
    """Genera imagen de comprobante de préstamo"""
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    cliente = prestamo.cliente
    cobrador = prestamo.cobrador
    
    # Crear imagen en memoria (1080x1350)
    width, height = 1080, 1350
    bg_color = '#f8fafc'
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Fuentes
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 70)
        font_subtitle = ImageFont.truetype("arial.ttf", 35)
        font_section = ImageFont.truetype("arialbd.ttf", 35)
        font_label = ImageFont.truetype("arial.ttf", 30)
        font_value = ImageFont.truetype("arialbd.ttf", 38)
        font_money = ImageFont.truetype("arialbd.ttf", 60)
        font_footer = ImageFont.truetype("arial.ttf", 28)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_section = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_value = ImageFont.load_default()
        font_money = ImageFont.load_default()
        font_footer = ImageFont.load_default()
    
    # Colores
    c_primary = '#0f172a'
    c_accent = '#0284c7'
    c_success = '#059669'
    c_text = '#334155'
    c_muted = '#64748b'
    c_white = '#ffffff'
    
    # Encabezado
    header_h = 280
    draw.rectangle([0, 0, width, header_h], fill=c_primary)
    draw.text((width // 2, 100), "💎 DIAMANTE PRO", fill=c_white, font=font_title, anchor='mm')
    draw.text((width // 2, 180), "COMPROBANTE OFICIAL DE CRÉDITO", fill='#e2e8f0', font=font_subtitle, anchor='mm')
    
    # Tag con ID y fecha
    tag_w, tag_h = 600, 60
    tag_x = (width - tag_w) // 2
    tag_y = 220
    draw.rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], fill=c_accent)
    draw.text((width // 2, tag_y + 30),
        f"CRÉDITO #{prestamo.id}  •  {prestamo.fecha_inicio.strftime('%d/%m/%Y')}",
        fill=c_white, font=font_section, anchor='mm')
    
    current_y = 330
    margin_x = 60
    
    def draw_card(y_pos, height):
        draw.rectangle([margin_x + 5, y_pos + 5, width - margin_x + 5, y_pos + height + 5], fill='#e2e8f0')
        draw.rectangle([margin_x, y_pos, width - margin_x, y_pos + height], fill=c_white, outline='#cbd5e1', width=1)
        return y_pos
    
    # Tarjeta 1: Cliente
    card1_h = 350
    draw_card(current_y, card1_h)
    draw.text((margin_x + 40, current_y + 50), "👤 DATOS DEL CLIENTE", fill=c_accent, font=font_section)
    draw.text((margin_x + 40, current_y + 110), cliente.nombre.upper(), fill=c_primary, font=font_money)
    draw.text((margin_x + 40, current_y + 170), f"Documento: {cliente.documento}", fill=c_muted, font=font_subtitle)
    draw.line([margin_x + 40, current_y + 200, width - margin_x - 40, current_y + 200], fill='#e2e8f0', width=2)
    draw.text((margin_x + 40, current_y + 230), "MONTO TOTAL A PAGAR", fill=c_muted, font=font_label)
    monto_total_txt = f"{prestamo.moneda} ${prestamo.monto_a_pagar:,.0f}"
    draw.text((width - margin_x - 40, current_y + 280), monto_total_txt, fill=c_primary, font=font_money, anchor='ra')
    
    current_y += card1_h + 40
    
    # Tarjeta 2: Detalles
    card2_h = 420
    draw_card(current_y, card2_h)
    draw.text((margin_x + 40, current_y + 50), "📊 DETALLES DEL PRÉSTAMO", fill=c_accent, font=font_section)
    
    col1_x = margin_x + 40
    col2_x = width // 2 + 20
    row_start = current_y + 120
    row_space = 100
    
    draw.text((col1_x, row_start), "Monto Prestado:", fill=c_muted, font=font_label)
    draw.text((col1_x, row_start + 40), f"${prestamo.monto_prestado:,.0f}", fill=c_text, font=font_value)
    draw.text((col1_x, row_start + row_space), "Tasa Interés:", fill=c_muted, font=font_label)
    draw.text((col1_x, row_start + row_space + 40), f"{prestamo.tasa_interes:.0f}%", fill=c_text, font=font_value)
    draw.text((col1_x, row_start + row_space * 2), "Estado:", fill=c_muted, font=font_label)
    estado_color = c_success if prestamo.estado == 'ACTIVO' else c_muted
    draw.text((col1_x, row_start + row_space * 2 + 40), f"✅ {prestamo.estado}", fill=estado_color, font=font_value)
    
    draw.text((col2_x, row_start), "Cuota:", fill=c_muted, font=font_label)
    draw.text((col2_x, row_start + 40), f"${prestamo.valor_cuota:,.0f} ({prestamo.frecuencia})", fill=c_text, font=font_value)
    draw.text((col2_x, row_start + row_space), "Nº Cuotas:", fill=c_muted, font=font_label)
    draw.text((col2_x, row_start + row_space + 40), f"{prestamo.numero_cuotas}", fill=c_text, font=font_value)
    draw.text((col2_x, row_start + row_space * 2), "Vence:", fill=c_muted, font=font_label)
    draw.text((col2_x, row_start + row_space * 2 + 40), f"{prestamo.fecha_fin_estimada.strftime('%d/%m/%Y')}", fill=c_text, font=font_value)
    
    current_y += card2_h + 50
    
    # Pie
    draw.line([margin_x, current_y, width - margin_x, current_y], fill='#cbd5e1', width=2)
    current_y += 30
    draw.text((width // 2, current_y), f"Atendido por: {cobrador.nombre}", fill=c_muted, font=font_footer, anchor='mm')
    draw.text((width // 2, current_y + 40), f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fill=c_muted, font=font_footer, anchor='mm')
    
    draw.rectangle([0, height - 100, width, height], fill='#f1f5f9')
    draw.text((width // 2, height - 50), "¡Gracias por su confianza!", fill=c_accent, font=font_section, anchor='mm')
    
    # Guardar en buffer
    buffer = BytesIO()
    img.save(buffer, format='PNG', quality=95)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='image/png',
        as_attachment=True,
        download_name=f'Comprobante_Credito_{prestamo.id}_{cliente.nombre.replace(" ", "_")}.png'
    )


@prestamos_bp.route('/eliminar/<int:prestamo_id>', methods=['POST'])
@login_required
def eliminar(prestamo_id):
    """Eliminar un préstamo y sus pagos asociados (solo dueño/gerente/admin)"""
    rol = session.get('rol')
    if rol not in ['dueno', 'gerente', 'admin']:
        flash('No tienes permisos para eliminar créditos.', 'danger')
        return redirect(url_for('prestamos.lista'))

    prestamo = Prestamo.query.get_or_404(prestamo_id)

    try:
        # Eliminar pagos asociados primero
        Pago.query.filter_by(prestamo_id=prestamo.id).delete()
        db.session.delete(prestamo)
        db.session.commit()
        flash('Crédito eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar crédito: {str(e)}', 'danger')

    return redirect(url_for('prestamos.lista'))
