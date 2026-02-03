"""
Blueprint de Cobros - Diamante Pro
Maneja: Registro de pagos/cobros
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, send_file
from datetime import datetime
from ..models import Prestamo, Pago, db
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

cobros_bp = Blueprint('cobros', __name__, url_prefix='/cobro')


def login_required(f):
    """Decorador para requerir login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@cobros_bp.route('/lista')
@login_required
def lista():
    """Lista de cobros pendientes"""
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')
    
    # Obtener préstamos activos
    if rol == 'cobrador':
        prestamos = Prestamo.query.filter_by(estado='ACTIVO', cobrador_id=usuario_id).all()
    else:
        prestamos = Prestamo.query.filter_by(estado='ACTIVO').all()
    
    total_a_cobrar = sum(p.valor_cuota for p in prestamos)
    creditos_al_dia = sum(1 for p in prestamos if p.cuotas_atrasadas == 0)
    creditos_atrasados = sum(1 for p in prestamos if 0 < p.cuotas_atrasadas <= 3)
    creditos_mora = sum(1 for p in prestamos if p.cuotas_atrasadas > 3)
    
    return render_template(
        'cobro_lista.html',
        prestamos=prestamos,
        total_a_cobrar=total_a_cobrar,
        creditos_al_dia=creditos_al_dia,
        creditos_atrasados=creditos_atrasados,
        creditos_mora=creditos_mora,
        fecha_hoy=datetime.now().strftime('%A, %d de %B %Y'),
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@cobros_bp.route('/registrar/<int:prestamo_id>')
@login_required
def registrar(prestamo_id):
    """Formulario para registrar pago"""
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    return render_template('cobro_registrar.html',
        prestamo=prestamo,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@cobros_bp.route('/guardar', methods=['POST'])
@login_required
def guardar():
    """Guardar pago registrado"""
    prestamo_id = None
    try:
        prestamo_id = int(request.form.get('prestamo_id'))
        prestamo = Prestamo.query.get_or_404(prestamo_id)
        db.session.refresh(prestamo)
        
        monto = float(request.form.get('monto'))
        tipo_pago = request.form.get('tipo_pago')
        forzar_pago = request.form.get('forzar_pago', '0')
        saldo_anterior = prestamo.saldo_actual

        # Verificar pago duplicado
        if forzar_pago != '1':
            hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            hoy_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
            pago_duplicado = Pago.query.filter(
                Pago.prestamo_id == prestamo_id,
                Pago.monto == monto,
                Pago.fecha_pago >= hoy_inicio,
                Pago.fecha_pago <= hoy_fin
            ).first()
            if pago_duplicado:
                return render_template(
                    'cobro_registrar.html',
                    prestamo=prestamo,
                    error=f'⚠️ Ya se registró un pago de {prestamo.moneda} {monto:,.0f} para este cliente hoy a las {pago_duplicado.fecha_pago.strftime("%H:%M")}. ¿Está seguro de registrar otro pago con el mismo valor?',
                    nombre=session.get('nombre'),
                    rol=session.get('rol')
                )

        nuevo_saldo = max(0, saldo_anterior - monto)
        
        if tipo_pago == 'COMPLETO':
            cuotas_pagadas = prestamo.numero_cuotas - prestamo.cuotas_pagadas
        elif tipo_pago == 'MULTIPLE':
            cuotas_pagadas = int(request.form.get('numero_cuotas_pagadas', 1))
        else:
            cuotas_pagadas = int(monto / prestamo.valor_cuota)
            if cuotas_pagadas == 0 and monto > 0:
                cuotas_pagadas = 1

        nuevo_pago = Pago(
            prestamo_id=prestamo_id,
            cobrador_id=session.get('usuario_id'),
            monto=monto,
            numero_cuotas_pagadas=cuotas_pagadas,
            saldo_anterior=saldo_anterior,
            saldo_nuevo=nuevo_saldo,
            observaciones=request.form.get('observaciones'),
            tipo_pago=tipo_pago,
            fecha_pago=datetime.now()
        )

        prestamo.saldo_actual = nuevo_saldo
        prestamo.cuotas_pagadas += cuotas_pagadas
        prestamo.fecha_ultimo_pago = datetime.now()
        
        if prestamo.cuotas_atrasadas > 0:
            prestamo.cuotas_atrasadas = max(0, prestamo.cuotas_atrasadas - cuotas_pagadas)
        
        if nuevo_saldo <= 0:
            prestamo.estado = 'CANCELADO'

        db.session.add(nuevo_pago)
        db.session.commit()
        
        return redirect(url_for('cobros.exito', pago_id=nuevo_pago.id))

    except Exception as e:
        db.session.rollback()
        prestamo = Prestamo.query.get(prestamo_id) if prestamo_id else None
        return render_template(
            'cobro_registrar.html',
            prestamo=prestamo,
            error=f'Error al registrar pago: {str(e)}',
            nombre=session.get('nombre'),
            rol=session.get('rol')
        )


@cobros_bp.route('/exito/<int:pago_id>')
@login_required
def exito(pago_id):
    """Página de éxito después de registrar pago"""
    pago = Pago.query.get_or_404(pago_id)
    prestamo = pago.prestamo
    cliente = prestamo.cliente
    
    fecha_formato = pago.fecha_pago.strftime('%d/%m/%Y %H:%M')
    mensaje = f"""RECIBO DE PAGO - DIAMANTE PRO

Credito: #{prestamo.id}
Cliente: {cliente.nombre}
Fecha: {fecha_formato}

Monto Recibido: {prestamo.moneda} {pago.monto:,.0f}
Saldo Anterior: {prestamo.moneda} {pago.saldo_anterior:,.0f}
Saldo Nuevo: {prestamo.moneda} {pago.saldo_nuevo:,.0f}

Cuotas Pagadas: {prestamo.cuotas_pagadas}/{prestamo.numero_cuotas}

Gracias por su pago!"""
    
    mensaje_encoded = mensaje.replace(' ', '%20').replace('\n', '%0A')
    whatsapp_url = f"https://wa.me/{cliente.whatsapp_completo}?text={mensaje_encoded}"
    
    return render_template('cobro_exito.html',
        pago=pago,
        prestamo=prestamo,
        cliente=cliente,
        whatsapp_url=whatsapp_url,
        nombre=session.get('nombre'),
        rol=session.get('rol'))


@cobros_bp.route('/recibo-imagen/<int:pago_id>')
@login_required
def recibo_imagen(pago_id):
    """Genera imagen de recibo de pago"""
    pago = Pago.query.get_or_404(pago_id)
    prestamo = pago.prestamo
    cliente = prestamo.cliente
    
    # Crear imagen
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
        font_money_main = ImageFont.truetype("arialbd.ttf", 80)
        font_footer = ImageFont.truetype("arial.ttf", 28)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_section = ImageFont.load_default()
        font_label = ImageFont.load_default()
        font_value = ImageFont.load_default()
        font_money = ImageFont.load_default()
        font_money_main = ImageFont.load_default()
        font_footer = ImageFont.load_default()
    
    # Colores
    c_primary = '#0f172a'
    c_accent = '#0284c7'
    c_success = '#059669'
    c_success_bg = '#d1fae5'
    c_text = '#334155'
    c_muted = '#64748b'
    c_white = '#ffffff'
    
    # Encabezado verde
    header_h = 280
    draw.rectangle([0, 0, width, header_h], fill=c_success)
    draw.text((width // 2, 100), "💎 DIAMANTE PRO", fill=c_white, font=font_title, anchor='mm')
    draw.text((width // 2, 180), "RECIBO DE PAGO OFICIAL", fill='#ecfdf5', font=font_subtitle, anchor='mm')
    
    # Tag
    tag_w, tag_h = 600, 60
    tag_x = (width - tag_w) // 2
    tag_y = 220
    draw.rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], fill='#047857')
    draw.text((width // 2, tag_y + 30),
        f"RECIBO #{pago.id}  •  {pago.fecha_pago.strftime('%d/%m/%Y %H:%M')}",
        fill=c_white, font=font_section, anchor='mm')
    
    current_y = 330
    margin_x = 60
    
    def draw_card(y_pos, height):
        draw.rectangle([margin_x + 5, y_pos + 5, width - margin_x + 5, y_pos + height + 5], fill='#e2e8f0')
        draw.rectangle([margin_x, y_pos, width - margin_x, y_pos + height], fill=c_white, outline='#cbd5e1', width=1)
        return y_pos
    
    # Tarjeta Cliente
    card1_h = 250
    draw_card(current_y, card1_h)
    draw.text((margin_x + 40, current_y + 50), "👤 DATOS DEL CLIENTE", fill=c_success, font=font_section)
    draw.text((margin_x + 40, current_y + 110), cliente.nombre.upper(), fill=c_primary, font=font_money)
    draw.text((margin_x + 40, current_y + 170), f"Documento: {cliente.documento}  |  Crédito #{prestamo.id}", fill=c_muted, font=font_subtitle)
    
    current_y += card1_h + 40
    
    # Tarjeta Monto (destacada)
    card2_h = 250
    draw_card(current_y, card2_h)
    draw.rectangle([margin_x, current_y, width - margin_x, current_y + card2_h], fill=c_success_bg, outline='#10b981', width=2)
    draw.text((width // 2, current_y + 60), "MONTO RECIBIDO", fill='#047857', font=font_section, anchor='mm')
    draw.text((width // 2, current_y + 140), f"{prestamo.moneda} ${pago.monto:,.0f}", fill='#065f46', font=font_money_main, anchor='mm')
    
    current_y += card2_h + 40
    
    # Tarjeta Estado de Cuenta
    card3_h = 280
    draw_card(current_y, card3_h)
    draw.text((margin_x + 40, current_y + 50), "📉 ESTADO DE CUENTA", fill=c_primary, font=font_section)
    
    row_space = 100
    row_start = current_y + 110
    col1_x = margin_x + 40
    col2_x = width // 2 + 20
    
    draw.text((col1_x, row_start), "Saldo Anterior:", fill=c_muted, font=font_label)
    draw.text((col1_x, row_start + 40), f"${pago.saldo_anterior:,.0f}", fill=c_text, font=font_value)
    draw.text((col2_x, row_start), "Nuevo Saldo:", fill=c_muted, font=font_label)
    draw.text((col2_x, row_start + 40), f"${pago.saldo_nuevo:,.0f}", fill=c_accent, font=font_money)
    
    current_y += card3_h + 50
    
    # Pie
    draw.line([margin_x, current_y, width - margin_x, current_y], fill='#cbd5e1', width=2)
    current_y += 30
    draw.text((width // 2, current_y), f"Recibido por: {session.get('nombre')}", fill=c_muted, font=font_footer, anchor='mm')
    
    draw.rectangle([0, height - 80, width, height], fill='#f1f5f9')
    draw.text((width // 2, height - 40), "¡Gracias por su pago a tiempo!", fill=c_success, font=font_section, anchor='mm')
    
    # Guardar
    buffer = BytesIO()
    img.save(buffer, format='PNG', quality=95)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='image/png',
        as_attachment=True,
        download_name=f'Recibo_Pago_{pago.id}_{cliente.nombre.replace(" ", "_")}.png'
    )
