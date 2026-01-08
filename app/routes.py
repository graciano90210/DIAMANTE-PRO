from flask import render_template, request, redirect, url_for, session, flash, make_response, send_file
from .models import Usuario, Cliente, Prestamo, Pago, Transaccion, Sociedad, Ruta, AporteCapital, Activo, db
from datetime import datetime, timedelta
from sqlalchemy import func
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from io import BytesIO
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("⚠️ Warning: PIL (Pillow) not available. Image features will be disabled.")
    Image = None
    ImageDraw = None
    ImageFont = None
import os
import base64

def init_routes(app):
    # ==================== AUTENTICACIÓN ====================
    @app.route('/')
    def home():
        if 'usuario_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('login.html')
    
    @app.route('/login', methods=['POST'])
    def login():
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(usuario=usuario).first()
        
        if user and user.password == password and user.activo:
            session['usuario_id'] = user.id
            session['nombre'] = user.nombre
            session['rol'] = user.rol
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos')
    
    @app.route('/dashboard')
    def dashboard():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        usuario_id = session.get('usuario_id')
        rol = session.get('rol')
        
        # Obtener ruta seleccionada (para dueño y gerente)
        ruta_seleccionada_id = session.get('ruta_seleccionada_id')
        ruta_seleccionada = None
        todas_las_rutas = []
        
        if rol in ['dueno', 'gerente']:
            todas_las_rutas = Ruta.query.filter_by(activo=True).order_by(Ruta.nombre).all()
            if ruta_seleccionada_id:
                ruta_seleccionada = Ruta.query.get(ruta_seleccionada_id)
        
        # Estadísticas generales (todos ven total de clientes)
        total_clientes = Cliente.query.count()
        clientes_vip = Cliente.query.filter_by(es_vip=True).count()
        
        # Si es cobrador, filtrar solo sus préstamos
        if rol == 'cobrador':
            # Préstamos activos del cobrador
            prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO', cobrador_id=usuario_id).all()
            total_prestamos_activos = len(prestamos_activos)
            
            # Cartera total del cobrador
            total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter_by(estado='ACTIVO', cobrador_id=usuario_id).scalar()
            total_cartera = float(total_cartera) if total_cartera else 0
            
            # Capital prestado del cobrador
            capital_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter_by(estado='ACTIVO', cobrador_id=usuario_id).scalar()
            capital_prestado = float(capital_prestado) if capital_prestado else 0
            
            # Por cobrar hoy del cobrador
            por_cobrar_hoy = sum(float(p.valor_cuota) for p in prestamos_activos if p.frecuencia in ['DIARIO', 'BISEMANAL']) if prestamos_activos else 0
            
            # Préstamos al día vs atrasados del cobrador
            prestamos_al_dia = sum(1 for p in prestamos_activos if p.cuotas_atrasadas == 0) if prestamos_activos else 0
            prestamos_atrasados = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 0) if prestamos_activos else 0
            prestamos_mora = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 3) if prestamos_activos else 0
            
            # Pagos realizados hoy por el cobrador
            hoy = datetime.now().date()
            pagos_hoy = Pago.query.join(Prestamo).filter(
                func.date(Pago.fecha_pago) == hoy,
                Prestamo.cobrador_id == usuario_id
            ).all()
            total_cobrado_hoy = sum(float(p.monto) for p in pagos_hoy) if pagos_hoy else 0
            num_pagos_hoy = len(pagos_hoy)
            
            # Últimos pagos del cobrador
            ultimos_pagos = Pago.query.join(Prestamo).filter(
                Prestamo.cobrador_id == usuario_id
            ).order_by(Pago.fecha_pago.desc()).limit(10).all()
            
            # Préstamos recientes del cobrador
            prestamos_recientes = Prestamo.query.filter_by(
                cobrador_id=usuario_id
            ).order_by(Prestamo.fecha_inicio.desc()).limit(5).all()
        else:
            # Dueño, gerente, secretaria ven todas las estadísticas (o filtradas por ruta)
            if ruta_seleccionada_id:
                # Filtrar por ruta seleccionada
                prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO', ruta_id=ruta_seleccionada_id).all()
                total_prestamos_activos = len(prestamos_activos)
                
                # Cartera total de la ruta
                total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter_by(estado='ACTIVO', ruta_id=ruta_seleccionada_id).scalar()
                total_cartera = float(total_cartera) if total_cartera else 0
                
                # Capital prestado de la ruta
                capital_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter_by(estado='ACTIVO', ruta_id=ruta_seleccionada_id).scalar()
                capital_prestado = float(capital_prestado) if capital_prestado else 0
                
                # Pagos de la ruta hoy
                hoy = datetime.now().date()
                pagos_hoy = Pago.query.join(Prestamo).filter(
                    func.date(Pago.fecha_pago) == hoy,
                    Prestamo.ruta_id == ruta_seleccionada_id
                ).all()
                
                # Últimos pagos de la ruta
                ultimos_pagos = Pago.query.join(Prestamo).filter(
                    Prestamo.ruta_id == ruta_seleccionada_id
                ).order_by(Pago.fecha_pago.desc()).limit(10).all()
                
                # Préstamos recientes de la ruta
                prestamos_recientes = Prestamo.query.filter_by(
                    ruta_id=ruta_seleccionada_id
                ).order_by(Prestamo.fecha_inicio.desc()).limit(5).all()
            else:
                # Ver todas las rutas
                prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO').all()
                total_prestamos_activos = len(prestamos_activos)
                
                # Cartera total
                total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter_by(estado='ACTIVO').scalar()
                total_cartera = float(total_cartera) if total_cartera else 0
                
                # Capital prestado
                capital_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter_by(estado='ACTIVO').scalar()
                capital_prestado = float(capital_prestado) if capital_prestado else 0
                
                # Total pagos realizados hoy
                hoy = datetime.now().date()
                pagos_hoy = Pago.query.filter(func.date(Pago.fecha_pago) == hoy).all()
                
                # Últimos pagos generales
                ultimos_pagos = Pago.query.order_by(Pago.fecha_pago.desc()).limit(10).all()
                
                # Préstamos recientes generales
                prestamos_recientes = Prestamo.query.order_by(Prestamo.fecha_inicio.desc()).limit(5).all()
            
            # Por cobrar hoy
            por_cobrar_hoy = sum(float(p.valor_cuota) for p in prestamos_activos if p.frecuencia in ['DIARIO', 'BISEMANAL']) if prestamos_activos else 0
            
            # Préstamos al día vs atrasados
            prestamos_al_dia = sum(1 for p in prestamos_activos if p.cuotas_atrasadas == 0) if prestamos_activos else 0
            prestamos_atrasados = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 0) if prestamos_activos else 0
            prestamos_mora = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 3) if prestamos_activos else 0
            
            total_cobrado_hoy = sum(float(p.monto) for p in pagos_hoy) if pagos_hoy else 0
            num_pagos_hoy = len(pagos_hoy)
        
        # Calcular estadísticas avanzadas
        ganancia_esperada = total_cartera - capital_prestado if capital_prestado > 0 else 0
        porcentaje_ganancia = ((ganancia_esperada / capital_prestado) * 100) if capital_prestado > 0 else 0
        tasa_cobro_diaria = (total_cobrado_hoy / por_cobrar_hoy * 100) if por_cobrar_hoy > 0 else 0
        
        # NUEVO: Calcular Capital Disponible (solo para dueño y gerente)
        capital_total_aportado = 0
        capital_invertido_activos = 0
        capital_disponible = 0
        
        if rol in ['dueno', 'gerente']:
            # Total de aportes de capital
            capital_total_aportado = db.session.query(func.sum(AporteCapital.monto)).scalar() or 0
            capital_total_aportado = float(capital_total_aportado)
            
            # Total invertido en activos
            capital_invertido_activos = db.session.query(func.sum(Activo.valor_compra)).scalar() or 0
            capital_invertido_activos = float(capital_invertido_activos)
            
            # Capital disponible = Aportes - Activos
            capital_disponible = capital_total_aportado - capital_invertido_activos
        
        # Estadísticas de los últimos 7 días para gráficos
        fecha_inicio = datetime.now().date() - timedelta(days=6)
        cobros_ultimos_7_dias = []
        labels_7_dias = []
        
        for i in range(7):
            fecha = fecha_inicio + timedelta(days=i)
            if rol == 'cobrador':
                pagos_dia = Pago.query.join(Prestamo).filter(
                    func.date(Pago.fecha_pago) == fecha,
                    Prestamo.cobrador_id == usuario_id
                ).all()
            elif ruta_seleccionada_id:
                pagos_dia = Pago.query.join(Prestamo).filter(
                    func.date(Pago.fecha_pago) == fecha,
                    Prestamo.ruta_id == ruta_seleccionada_id
                ).all()
            else:
                pagos_dia = Pago.query.filter(func.date(Pago.fecha_pago) == fecha).all()
            
            total_dia = sum(float(p.monto) for p in pagos_dia) if pagos_dia else 0
            cobros_ultimos_7_dias.append(total_dia)
            labels_7_dias.append(fecha.strftime('%d/%m'))
        
        # Distribución de préstamos por estado
        if rol == 'cobrador':
            prestamos_pagados = Prestamo.query.filter_by(estado='PAGADO', cobrador_id=usuario_id).count()
            prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO', cobrador_id=usuario_id).count()
        elif ruta_seleccionada_id:
            prestamos_pagados = Prestamo.query.filter_by(estado='PAGADO', ruta_id=ruta_seleccionada_id).count()
            prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO', ruta_id=ruta_seleccionada_id).count()
        else:
            prestamos_pagados = Prestamo.query.filter_by(estado='PAGADO').count()
            prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO').count()
        
        return render_template('dashboard.html', 
                             nombre=session.get('nombre'), 
                             rol=session.get('rol'),
                             total_clientes=total_clientes,
                             clientes_vip=clientes_vip,
                             total_prestamos_activos=total_prestamos_activos,
                             total_cartera=total_cartera,
                             capital_prestado=capital_prestado,
                             por_cobrar_hoy=por_cobrar_hoy,
                             prestamos_al_dia=prestamos_al_dia,
                             prestamos_atrasados=prestamos_atrasados,
                             prestamos_mora=prestamos_mora,
                             total_cobrado_hoy=total_cobrado_hoy,
                             num_pagos_hoy=num_pagos_hoy,
                             todas_las_rutas=todas_las_rutas,
                             ruta_seleccionada=ruta_seleccionada,
                             ganancia_esperada=ganancia_esperada,
                             porcentaje_ganancia=porcentaje_ganancia,
                             tasa_cobro_diaria=tasa_cobro_diaria,
                             ultimos_pagos=ultimos_pagos,
                             prestamos_recientes=prestamos_recientes,
                             cobros_ultimos_7_dias=cobros_ultimos_7_dias,
                             labels_7_dias=labels_7_dias,
                             prestamos_pagados=prestamos_pagados,
                             prestamos_cancelados=prestamos_cancelados,
                             capital_total_aportado=capital_total_aportado,
                             capital_invertido_activos=capital_invertido_activos,
                             capital_disponible=capital_disponible)
    
    @app.route('/seleccionar-ruta/<int:ruta_id>')
    def seleccionar_ruta(ruta_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        # Guardar la ruta seleccionada en la sesión
        session['ruta_seleccionada_id'] = ruta_id
        return redirect(url_for('dashboard'))
    
    @app.route('/ver-todas-rutas')
    def ver_todas_rutas():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        # Limpiar la ruta seleccionada para ver todas
        session.pop('ruta_seleccionada_id', None)
        return redirect(url_for('dashboard'))
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('home'))

    # ==================== CLIENTES ====================
    @app.route('/clientes')
    def clientes_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        rol = session.get('rol')
        usuario_id = session.get('usuario_id')
        
        # Si es cobrador, solo ver sus clientes (que tienen préstamos asignados a él)
        if rol == 'cobrador':
            # Obtener IDs de clientes que tienen préstamos del cobrador
            clientes_ids = db.session.query(Prestamo.cliente_id).filter_by(cobrador_id=usuario_id).distinct().all()
            clientes_ids = [c[0] for c in clientes_ids]
            clientes = Cliente.query.filter(Cliente.id.in_(clientes_ids)).order_by(Cliente.fecha_registro.desc()).all()
        else:
            # Dueño, gerente y secretaria ven todos los clientes (o filtrados por ruta)
            ruta_seleccionada_id = session.get('ruta_seleccionada_id')
            
            if ruta_seleccionada_id:
                # Obtener clientes de la ruta seleccionada
                clientes_ids = db.session.query(Prestamo.cliente_id).filter_by(ruta_id=ruta_seleccionada_id).distinct().all()
                clientes_ids = [c[0] for c in clientes_ids]
                clientes = Cliente.query.filter(Cliente.id.in_(clientes_ids)).order_by(Cliente.fecha_registro.desc()).all()
            else:
                # Ver todos los clientes
                clientes = Cliente.query.order_by(Cliente.fecha_registro.desc()).all()
        
        return render_template('clientes_lista.html', 
                             clientes=clientes,
                             nombre=session.get('nombre'), 
                             rol=session.get('rol'),
                             mensaje=request.args.get('mensaje'))
    
    @app.route('/clientes/nuevo')
    def clientes_nuevo():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        return render_template('clientes_nuevo.html', 
                             nombre=session.get('nombre'), 
                             rol=session.get('rol'))
    
    @app.route('/clientes/guardar', methods=['POST'])
    def clientes_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        try:
            # Verificar si el documento ya existe
            documento = request.form.get('documento')
            if Cliente.query.filter_by(documento=documento).first():
                return render_template('clientes_nuevo.html', 
                                     error='Ya existe un cliente con ese documento',
                                     nombre=session.get('nombre'), 
                                     rol=session.get('rol'))
            
            # Crear nuevo cliente
            nuevo_cliente = Cliente(
                nombre=request.form.get('nombre'),
                documento=documento,
                documento_negocio=request.form.get('documento_negocio'),
                telefono=request.form.get('telefono'),
                whatsapp_codigo_pais=request.form.get('whatsapp_codigo_pais', '57'),
                whatsapp_numero=request.form.get('whatsapp_numero'),
                direccion_negocio=request.form.get('direccion_negocio'),
                gps_latitud=request.form.get('gps_latitud') or None,
                gps_longitud=request.form.get('gps_longitud') or None,
                es_vip=bool(request.form.get('es_vip'))
            )
            
            db.session.add(nuevo_cliente)
            db.session.commit()
            
            return redirect(url_for('clientes_lista', mensaje='Cliente registrado exitosamente'))
        
        except Exception as e:
            db.session.rollback()
            return render_template('clientes_nuevo.html', 
                                 error=f'Error al guardar: {str(e)}',
                                 nombre=session.get('nombre'), 
                                 rol=session.get('rol'))
    
    @app.route('/clientes/editar/<int:cliente_id>')
    def clientes_editar(cliente_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        cliente = Cliente.query.get_or_404(cliente_id)
        
        return render_template('clientes_editar.html',
                             cliente=cliente,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/clientes/actualizar/<int:cliente_id>', methods=['POST'])
    def clientes_actualizar(cliente_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        try:
            cliente = Cliente.query.get_or_404(cliente_id)
            
            # Verificar si el documento cambió y ya existe en otro cliente
            nuevo_documento = request.form.get('documento')
            if nuevo_documento != cliente.documento:
                if Cliente.query.filter_by(documento=nuevo_documento).first():
                    return render_template('clientes_editar.html',
                                         cliente=cliente,
                                         error='Ya existe otro cliente con ese documento',
                                         nombre=session.get('nombre'),
                                         rol=session.get('rol'))
            
            # Actualizar datos
            cliente.nombre = request.form.get('nombre')
            cliente.documento = nuevo_documento
            cliente.documento_negocio = request.form.get('documento_negocio')
            cliente.telefono = request.form.get('telefono')
            cliente.whatsapp_codigo_pais = request.form.get('whatsapp_codigo_pais', '57')
            cliente.whatsapp_numero = request.form.get('whatsapp_numero')
            cliente.direccion_negocio = request.form.get('direccion_negocio')
            cliente.gps_latitud = request.form.get('gps_latitud') or None
            cliente.gps_longitud = request.form.get('gps_longitud') or None
            cliente.es_vip = bool(request.form.get('es_vip'))
            
            db.session.commit()
            
            return redirect(url_for('clientes_lista', mensaje='Cliente actualizado exitosamente'))
        
        except Exception as e:
            db.session.rollback()
            return render_template('clientes_editar.html',
                                 cliente=cliente,
                                 error=f'Error al actualizar: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))

    # ==================== PRÉSTAMOS ====================
    @app.route('/prestamos')
    def prestamos_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        usuario_id = session.get('usuario_id')
        rol = session.get('rol')
        
        # Si es cobrador, solo ver sus préstamos asignados
        if rol == 'cobrador':
            prestamos = Prestamo.query.filter_by(cobrador_id=usuario_id).order_by(Prestamo.fecha_inicio.desc()).all()
            
            # Estadísticas solo de sus préstamos
            total_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter(
                Prestamo.estado == 'ACTIVO',
                Prestamo.cobrador_id == usuario_id
            ).scalar() or 0
            
            total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter(
                Prestamo.estado == 'ACTIVO',
                Prestamo.cobrador_id == usuario_id
            ).scalar() or 0
            
            prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO', cobrador_id=usuario_id).count()
            
            ganancia_esperada = db.session.query(
                func.sum(Prestamo.monto_a_pagar - Prestamo.monto_prestado)
            ).filter(Prestamo.estado == 'ACTIVO', Prestamo.cobrador_id == usuario_id).scalar() or 0
        else:
            # Dueño, gerente y secretaria ven todos los préstamos (o filtrados por ruta)
            ruta_seleccionada_id = session.get('ruta_seleccionada_id')
            
            if ruta_seleccionada_id:
                # Filtrar por ruta seleccionada
                prestamos = Prestamo.query.filter_by(ruta_id=ruta_seleccionada_id).order_by(Prestamo.fecha_inicio.desc()).all()
                
                total_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter(
                    Prestamo.estado == 'ACTIVO',
                    Prestamo.ruta_id == ruta_seleccionada_id
                ).scalar() or 0
                
                total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter(
                    Prestamo.estado == 'ACTIVO',
                    Prestamo.ruta_id == ruta_seleccionada_id
                ).scalar() or 0
                
                prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO', ruta_id=ruta_seleccionada_id).count()
                
                ganancia_esperada = db.session.query(
                    func.sum(Prestamo.monto_a_pagar - Prestamo.monto_prestado)
                ).filter(Prestamo.estado == 'ACTIVO', Prestamo.ruta_id == ruta_seleccionada_id).scalar() or 0
            else:
                # Ver todos los préstamos
                prestamos = Prestamo.query.order_by(Prestamo.fecha_inicio.desc()).all()
                
                # Estadísticas generales
                total_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter(
                    Prestamo.estado == 'ACTIVO'
                ).scalar() or 0
                
                total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter(
                    Prestamo.estado == 'ACTIVO'
                ).scalar() or 0
                
                prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO').count()
                
                ganancia_esperada = db.session.query(
                func.sum(Prestamo.monto_a_pagar - Prestamo.monto_prestado)
            ).filter(Prestamo.estado == 'ACTIVO').scalar() or 0
        
        return render_template('prestamos_lista.html',
                             prestamos=prestamos,
                             total_prestado=total_prestado,
                             total_cartera=total_cartera,
                             prestamos_activos=prestamos_activos,
                             ganancia_esperada=ganancia_esperada,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'),
                             mensaje=request.args.get('mensaje'))
    
    @app.route('/prestamos/nuevo')
    def prestamos_nuevo():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        clientes = Cliente.query.order_by(Cliente.nombre).all()
        # Cobradores pueden ser: supervisor, cobrador, o admin (por compatibilidad)
        cobradores = Usuario.query.filter(Usuario.rol.in_(['admin', 'dueno', 'supervisor', 'cobrador'])).all()
        
        # Obtener cliente_id de los parámetros de URL si existe
        cliente_id_seleccionado = request.args.get('cliente_id', type=int)
        
        return render_template('prestamos_nuevo.html',
                             clientes=clientes,
                             cobradores=cobradores,
                             fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
                             nombre=session.get('nombre'),
                             rol=session.get('rol'),
                             usuario_id=session.get('usuario_id'),
                             cliente_id_seleccionado=cliente_id_seleccionado)
    
    @app.route('/prestamos/guardar', methods=['POST'])
    def prestamos_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        try:
            cliente_id = int(request.form.get('cliente_id'))
            
            # VALIDACIÓN: Verificar si el cliente ya tiene un préstamo activo
            prestamo_activo = Prestamo.query.filter_by(
                cliente_id=cliente_id,
                estado='ACTIVO'
            ).first()
            
            if prestamo_activo:
                clientes = Cliente.query.all()
                cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
                return render_template('prestamos_nuevo.html',
                                     error=f'❌ Este cliente ya tiene un préstamo activo (#ID: {prestamo_activo.id}). No puede tener dos préstamos simultáneos.',
                                     clientes=clientes,
                                     cobradores=cobradores,
                                     nombre=session.get('nombre'),
                                     rol=session.get('rol'))
            
            monto_prestado = float(request.form.get('monto_prestado'))
            tasa_interes = float(request.form.get('tasa_interes'))
            numero_cuotas = int(request.form.get('numero_cuotas'))
            monto_a_pagar = float(request.form.get('monto_a_pagar'))
            valor_cuota = float(request.form.get('valor_cuota'))
            
            # Calcular fecha fin estimada
            fecha_inicio = datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d')
            frecuencia = request.form.get('frecuencia')
            
            if frecuencia == 'DIARIO':
                # Considerar solo días laborables (lun-sáb)
                dias_totales = numero_cuotas + (numero_cuotas // 6)  # +1 domingo por cada 6 días
                fecha_fin = fecha_inicio + timedelta(days=dias_totales)
            elif frecuencia == 'BISEMANAL':
                # 2 pagos por semana = cada 3-4 días
                dias_totales = (numero_cuotas * 7) // 2  # Aprox 3.5 días por cuota
                fecha_fin = fecha_inicio + timedelta(days=dias_totales)
            elif frecuencia == 'SEMANAL':
                fecha_fin = fecha_inicio + timedelta(weeks=numero_cuotas)
            elif frecuencia == 'QUINCENAL':
                fecha_fin = fecha_inicio + timedelta(days=numero_cuotas * 15)
            else:  # MENSUAL
                fecha_fin = fecha_inicio + timedelta(days=numero_cuotas * 30)
            
            # Crear préstamo
            nuevo_prestamo = Prestamo(
                cliente_id=cliente_id,
                cobrador_id=int(request.form.get('cobrador_id')),
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
            
            # Redirigir a página de éxito con comprobante
            return redirect(url_for('prestamo_exito', prestamo_id=nuevo_prestamo.id))
        
        except Exception as e:
            db.session.rollback()
            clientes = Cliente.query.order_by(Cliente.nombre).all()
            cobradores = Usuario.query.filter(Usuario.rol.in_(['admin', 'cobrador'])).all()
            return render_template('prestamos_nuevo.html',
                                 clientes=clientes,
                                 cobradores=cobradores,
                                 fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
                                 error=f'Error al crear préstamo: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))
    
    @app.route('/prestamos/ver/<int:prestamo_id>')
    def prestamo_detalle(prestamo_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        prestamo = Prestamo.query.get_or_404(prestamo_id)
        
        # Obtener todos los pagos del préstamo ordenados por fecha
        pagos = Pago.query.filter_by(prestamo_id=prestamo_id).order_by(Pago.fecha_pago.desc()).all()
        
        return render_template('prestamo_detalle.html',
                             prestamo=prestamo,
                             pagos=pagos,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/prestamos/exito/<int:prestamo_id>')
    def prestamo_exito(prestamo_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        prestamo = Prestamo.query.get_or_404(prestamo_id)
        cliente = prestamo.cliente
        cobrador = prestamo.cobrador
        
        # Generar URL de WhatsApp con imagen del comprobante
        whatsapp_url = f"https://wa.me/{cliente.whatsapp_completo}"
        
        return render_template('prestamo_exito.html',
                             prestamo=prestamo,
                             cliente=cliente,
                             cobrador=cobrador,
                             whatsapp_url=whatsapp_url,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/prestamos/comprobante-imagen/<int:prestamo_id>')
    def prestamo_comprobante_imagen(prestamo_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        prestamo = Prestamo.query.get_or_404(prestamo_id)
        cliente = prestamo.cliente
        cobrador = prestamo.cobrador
        
        # Crear imagen en memoria (1080x1920 - Tamaño para móviles)
        width, height = 1080, 1920
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Usar fuentes del sistema (fallback a fuentes predeterminadas)
        try:
            font_title = ImageFont.truetype("arial.ttf", 80)
            font_subtitle = ImageFont.truetype("arial.ttf", 40)
            font_header = ImageFont.truetype("arialbd.ttf", 50)
            font_label = ImageFont.truetype("arial.ttf", 38)
            font_value = ImageFont.truetype("arialbd.ttf", 42)
            font_big = ImageFont.truetype("arialbd.ttf", 65)
            font_small = ImageFont.truetype("arial.ttf", 32)
        except:
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
            font_header = ImageFont.load_default()
            font_label = ImageFont.load_default()
            font_value = ImageFont.load_default()
            font_big = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Encabezado con degradado azul
        draw.rectangle([0, 0, width, 250], fill='#1e3c72')
        draw.text((width//2, 80), "💎 DIAMANTE PRO", fill='white', font=font_title, anchor='mm')
        draw.text((width//2, 160), "COMPROBANTE DE CRÉDITO", fill='white', font=font_subtitle, anchor='mm')
        draw.text((width//2, 210), f"Crédito #{prestamo.id} - {prestamo.fecha_inicio.strftime('%d/%m/%Y')}", fill='#60a5fa', font=font_subtitle, anchor='mm')
        
        y = 300
        
        # Información del cliente
        draw.text((80, y), "INFORMACIÓN DEL CLIENTE", fill='#1e3c72', font=font_header)
        y += 80
        draw.rectangle([50, y, width-50, y+220], outline='#60a5fa', width=3)
        y += 30
        draw.text((80, y), "Nombre:", fill='#4b5563', font=font_label)
        draw.text((80, y+50), cliente.nombre.upper(), fill='#111827', font=font_value)
        y += 120
        draw.text((80, y), f"Documento: {cliente.documento}", fill='#4b5563', font=font_label)
        y += 180
        
        # Detalles del crédito
        draw.rectangle([0, y, width, y+550], fill='#e0e7ff')
        y += 50
        draw.text((width//2, y), "DETALLES DEL CRÉDITO", fill='#1e3c72', font=font_header, anchor='mm')
        y += 100
        
        draw.text((80, y), "Monto Prestado:", fill='#4b5563', font=font_label)
        draw.text((80, y+55), f"{prestamo.moneda} ${prestamo.monto_prestado:,.0f}", fill='#059669', font=font_big)
        y += 150
        
        draw.text((80, y), f"Tasa de Interés: {prestamo.tasa_interes:.0f}%", fill='#4b5563', font=font_label)
        y += 80
        
        draw.text((80, y), "TOTAL A PAGAR:", fill='#dc2626', font=font_value)
        draw.text((80, y+55), f"{prestamo.moneda} ${prestamo.monto_a_pagar:,.0f}", fill='#dc2626', font=font_big)
        y += 200
        
        # Plan de pago
        draw.text((80, y), "PLAN DE PAGO", fill='#1e3c72', font=font_header)
        y += 80
        draw.rectangle([50, y, width-50, y+350], outline='#60a5fa', width=3)
        y += 30
        
        draw.text((80, y), f"Frecuencia: {prestamo.frecuencia}", fill='#4b5563', font=font_label)
        y += 70
        draw.text((80, y), f"Número de Cuotas: {prestamo.numero_cuotas}", fill='#4b5563', font=font_label)
        y += 70
        draw.text((80, y), "Valor por Cuota:", fill='#4b5563', font=font_label)
        draw.text((80, y+55), f"{prestamo.moneda} ${prestamo.valor_cuota:,.0f}", fill='#059669', font=font_big)
        y += 140
        draw.text((80, y), f"Fecha de Fin: {prestamo.fecha_fin_estimada.strftime('%d/%m/%Y')}", fill='#4b5563', font=font_label)
        y += 120
        
        # Información adicional
        draw.text((80, y), f"Cobrador: {cobrador.nombre}", fill='#6b7280', font=font_small)
        y += 60
        draw.text((80, y), f"Estado: ACTIVO", fill='#059669', font=font_value)
        y += 100
        
        # Pie de página
        draw.line([50, y, width-50, y], fill='#d1d5db', width=2)
        y += 30
        draw.text((width//2, y), f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fill='#9ca3af', font=font_small, anchor='mm')
        y += 50
        draw.text((width//2, y), "¡Gracias por confiar en DIAMANTE PRO!", fill='#1e3c72', font=font_label, anchor='mm')
        
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

    # ==================== COBRO ====================
    @app.route('/cobro/lista')
    def cobro_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        usuario_id = session.get('usuario_id')
        rol = session.get('rol')
        
        # Obtener fecha de hoy
        hoy = datetime.now().date()
        
        # Si es cobrador, solo ver sus préstamos asignados
        if rol == 'cobrador':
            prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO', cobrador_id=usuario_id).order_by(
                Prestamo.cuotas_atrasadas.desc()
            ).all()
        else:
            # Lista de préstamos activos (todos)
            prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO').order_by(
                Prestamo.cuotas_atrasadas.desc()
            ).all()
        
        # Filtrar préstamos que NO han pagado hoy
        prestamos = []
        for prestamo in prestamos_activos:
            # Verificar si hay un pago registrado hoy para este préstamo
            pago_hoy = Pago.query.filter(
                Pago.prestamo_id == prestamo.id,
                func.date(Pago.fecha_pago) == hoy
            ).first()
            
            # Si NO pagó hoy, agregarlo a la lista
            if not pago_hoy:
                prestamos.append(prestamo)
        
        # Estadísticas
        total_a_cobrar = sum(p.valor_cuota for p in prestamos)
        creditos_al_dia = sum(1 for p in prestamos if p.cuotas_atrasadas == 0)
        creditos_atrasados = sum(1 for p in prestamos if 0 < p.cuotas_atrasadas <= 3)
        creditos_mora = sum(1 for p in prestamos if p.cuotas_atrasadas > 3)
        
        return render_template('cobro_lista.html',
                             prestamos=prestamos,
                             total_a_cobrar=total_a_cobrar,
                             creditos_al_dia=creditos_al_dia,
                             creditos_atrasados=creditos_atrasados,
                             creditos_mora=creditos_mora,
                             fecha_hoy=datetime.now().strftime('%A, %d de %B %Y'),
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/cobro/registrar/<int:prestamo_id>')
    def cobro_registrar(prestamo_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        prestamo = Prestamo.query.get_or_404(prestamo_id)
        
        return render_template('cobro_registrar.html',
                             prestamo=prestamo,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/cobro/guardar', methods=['POST'])
    def cobro_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        try:
            prestamo_id = int(request.form.get('prestamo_id'))
            prestamo = Prestamo.query.get_or_404(prestamo_id)
            
            # Refrescar el objeto desde la base de datos para obtener el saldo más actual
            db.session.refresh(prestamo)
            
            monto = float(request.form.get('monto'))
            tipo_pago = request.form.get('tipo_pago')
            forzar_pago = request.form.get('forzar_pago', '0')
            # Usar el saldo actual del préstamo, no el del formulario
            saldo_anterior = prestamo.saldo_actual
            
            # Verificar si ya existe un pago con el mismo monto hoy (solo si no está forzando)
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
                    return render_template('cobro_registrar.html',
                                         prestamo=prestamo,
                                         error=f'⚠️ Ya se registró un pago de {prestamo.moneda} {monto:,.0f} para este cliente hoy a las {pago_duplicado.fecha_pago.strftime("%H:%M")}. ¿Está seguro de registrar otro pago con el mismo valor?',
                                         nombre=session.get('nombre'),
                                         rol=session.get('rol'))
            
            # Calcular nuevo saldo
            nuevo_saldo = max(0, saldo_anterior - monto)
            
            # Determinar cuántas cuotas se pagaron
            if tipo_pago == 'COMPLETO':
                cuotas_pagadas = prestamo.numero_cuotas - prestamo.cuotas_pagadas
            elif tipo_pago == 'MULTIPLE':
                cuotas_pagadas = int(request.form.get('numero_cuotas_pagadas', 1))
            else:
                # Calcular automáticamente basado en el monto
                cuotas_pagadas = int(monto / prestamo.valor_cuota)
                if cuotas_pagadas == 0 and monto > 0:
                    cuotas_pagadas = 1  # Al menos 1 si pagó algo
            
            # Crear registro de pago
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
            
            # Actualizar préstamo
            prestamo.saldo_actual = nuevo_saldo
            prestamo.cuotas_pagadas += cuotas_pagadas
            prestamo.fecha_ultimo_pago = datetime.now()
            
            # Recalcular cuotas atrasadas (lógica simple)
            if prestamo.cuotas_atrasadas > 0:
                prestamo.cuotas_atrasadas = max(0, prestamo.cuotas_atrasadas - cuotas_pagadas)
            
            # Si se pagó todo, cambiar estado
            if nuevo_saldo <= 0:
                prestamo.estado = 'CANCELADO'
            
            db.session.add(nuevo_pago)
            db.session.commit()
            
            return redirect(url_for('cobro_exito', pago_id=nuevo_pago.id))
        
        except Exception as e:
            db.session.rollback()
            prestamo = Prestamo.query.get(prestamo_id)
            return render_template('cobro_registrar.html',
                                 prestamo=prestamo,
                                 error=f'Error al registrar pago: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))
    
    @app.route('/cobro/exito/<int:pago_id>')
    def cobro_exito(pago_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        pago = Pago.query.get_or_404(pago_id)
        prestamo = pago.prestamo
        cliente = prestamo.cliente
        
        # Generar mensaje de WhatsApp simplificado
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
        
        # Usar el número de WhatsApp completo (con código de país)
        mensaje_encoded = mensaje.replace(' ', '%20').replace('\n', '%0A')
        whatsapp_url = f"https://wa.me/{cliente.whatsapp_completo}?text={mensaje_encoded}"
        
        return render_template('cobro_exito.html',
                             pago=pago,
                             prestamo=prestamo,
                             cliente=cliente,
                             whatsapp_url=whatsapp_url,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/cobro/recibo-imagen/<int:pago_id>')
    def cobro_recibo_imagen(pago_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        pago = Pago.query.get_or_404(pago_id)
        prestamo = pago.prestamo
        cliente = prestamo.cliente
        
        # Crear imagen en memoria (1080x1680 - Formato para recibo)
        width, height = 1080, 1680
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Usar fuentes del sistema
        try:
            font_title = ImageFont.truetype("arial.ttf", 70)
            font_subtitle = ImageFont.truetype("arial.ttf", 38)
            font_header = ImageFont.truetype("arialbd.ttf", 48)
            font_label = ImageFont.truetype("arial.ttf", 36)
            font_value = ImageFont.truetype("arialbd.ttf", 40)
            font_big = ImageFont.truetype("arialbd.ttf", 60)
            font_small = ImageFont.truetype("arial.ttf", 30)
        except:
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
            font_header = ImageFont.load_default()
            font_label = ImageFont.load_default()
            font_value = ImageFont.load_default()
            font_big = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Encabezado verde (pago exitoso)
        draw.rectangle([0, 0, width, 220], fill='#059669')
        draw.text((width//2, 70), "💎 DIAMANTE PRO", fill='white', font=font_title, anchor='mm')
        draw.text((width//2, 140), "RECIBO DE PAGO", fill='white', font=font_subtitle, anchor='mm')
        draw.text((width//2, 190), f"Recibo #{pago.id} - {pago.fecha_pago.strftime('%d/%m/%Y %H:%M')}", fill='#d1fae5', font=font_subtitle, anchor='mm')
        
        y = 280
        
        # Información del cliente
        draw.text((80, y), "CLIENTE", fill='#059669', font=font_header)
        y += 70
        draw.rectangle([50, y, width-50, y+180], outline='#10b981', width=3)
        y += 25
        draw.text((80, y), cliente.nombre.upper(), fill='#111827', font=font_value)
        y += 60
        draw.text((80, y), f"Doc: {cliente.documento}  |  Tel: {cliente.telefono}", fill='#6b7280', font=font_label)
        y += 120
        
        # Información del crédito
        draw.text((80, y), f"Crédito #{prestamo.id}", fill='#6b7280', font=font_label)
        y += 100
        
        # Monto recibido (destacado)
        draw.rectangle([0, y, width, y+200], fill='#d1fae5')
        y += 50
        draw.text((width//2, y), "MONTO RECIBIDO", fill='#059669', font=font_header, anchor='mm')
        y += 80
        draw.text((width//2, y), f"{prestamo.moneda} ${pago.monto:,.0f}", fill='#047857', font=font_big, anchor='mm')
        y += 150
        
        # Saldos
        draw.text((80, y), "Saldo Anterior:", fill='#6b7280', font=font_label)
        draw.text((width-80, y), f"{prestamo.moneda} ${pago.saldo_anterior:,.0f}", fill='#6b7280', font=font_value, anchor='rm')
        y += 70
        
        draw.text((80, y), "Saldo Nuevo:", fill='#1e40af', font=font_value)
        draw.text((width-80, y), f"{prestamo.moneda} ${pago.saldo_nuevo:,.0f}", fill='#1e40af', font=font_big, anchor='rm')
        y += 100
        
        # Cuotas
        draw.line([50, y, width-50, y], fill='#d1d5db', width=2)
        y += 40
        draw.text((80, y), f"Cuotas Pagadas: {prestamo.cuotas_pagadas} / {prestamo.numero_cuotas}", fill='#4b5563', font=font_label)
        y += 80
        
        # Observaciones si existen
        if pago.observaciones:
            draw.text((80, y), "Observaciones:", fill='#6b7280', font=font_label)
            y += 50
            # Limitar texto de observaciones
            obs_text = pago.observaciones[:100] + "..." if len(pago.observaciones) > 100 else pago.observaciones
            draw.text((80, y), obs_text, fill='#6b7280', font=font_small)
            y += 80
        
        # Pie de página
        y = height - 150
        draw.line([50, y, width-50, y], fill='#d1d5db', width=2)
        y += 40
        draw.text((width//2, y), f"Cobrador: {session.get('nombre')}", fill='#9ca3af', font=font_small, anchor='mm')
        y += 50
        draw.text((width//2, y), "¡Gracias por su pago!", fill='#059669', font=font_value, anchor='mm')
        
        # Guardar en buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'Recibo_Pago_{pago.id}_{cliente.nombre.replace(" ", "_")}.png'
        )

    # ==================== REPORTES ====================
    @app.route('/reportes')
    def reportes():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        usuario_id = session.get('usuario_id')
        rol = session.get('rol')
        
        # Obtener fecha de inicio y fin (por defecto últimos 30 días)
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Si hay filtros en la query
        if request.args.get('fecha_inicio'):
            fecha_inicio = datetime.strptime(request.args.get('fecha_inicio'), '%Y-%m-%d')
        if request.args.get('fecha_fin'):
            fecha_fin = datetime.strptime(request.args.get('fecha_fin'), '%Y-%m-%d')
            fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
        
        # ===== ESTADÍSTICAS GENERALES =====
        total_clientes = Cliente.query.count()
        
        if rol == 'cobrador':
            # Cobradores ven solo sus préstamos
            total_prestamos = Prestamo.query.filter_by(cobrador_id=usuario_id).count()
            prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO', cobrador_id=usuario_id).count()
            prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO', cobrador_id=usuario_id).count()
        else:
            # Otros roles ven todos los préstamos
            total_prestamos = Prestamo.query.count()
            prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO').count()
            prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO').count()
        
        # ===== DATOS FINANCIEROS =====
        if rol == 'cobrador':
            # Total prestado en el período (solo del cobrador)
            prestamos_periodo = Prestamo.query.filter(
                Prestamo.fecha_inicio >= fecha_inicio,
                Prestamo.fecha_inicio <= fecha_fin,
                Prestamo.cobrador_id == usuario_id
            ).all()
            
            total_prestado_periodo = sum(p.monto_prestado for p in prestamos_periodo)
            
            # Total cobrado en el período (solo sus pagos)
            pagos_periodo = Pago.query.join(Prestamo).filter(
                Pago.fecha_pago >= fecha_inicio,
                Pago.fecha_pago <= fecha_fin,
                Prestamo.cobrador_id == usuario_id
            ).all()
            
            total_cobrado_periodo = sum(p.monto for p in pagos_periodo)
            num_pagos_periodo = len(pagos_periodo)
            
            # Cartera actual (solo sus préstamos)
            cartera_actual = db.session.query(func.sum(Prestamo.saldo_actual)).filter_by(estado='ACTIVO', cobrador_id=usuario_id).scalar()
            cartera_actual = float(cartera_actual) if cartera_actual else 0
            
            # Capital en circulación (solo sus préstamos)
            capital_circulacion = db.session.query(func.sum(Prestamo.monto_prestado)).filter_by(estado='ACTIVO', cobrador_id=usuario_id).scalar()
            capital_circulacion = float(capital_circulacion) if capital_circulacion else 0
        else:
            # Total prestado en el período
            prestamos_periodo = Prestamo.query.filter(
                Prestamo.fecha_inicio >= fecha_inicio,
                Prestamo.fecha_inicio <= fecha_fin
            ).all()
            
            total_prestado_periodo = sum(p.monto_prestado for p in prestamos_periodo)
            
            # Total cobrado en el período
            pagos_periodo = Pago.query.filter(
                Pago.fecha_pago >= fecha_inicio,
                Pago.fecha_pago <= fecha_fin
            ).all()
            
            total_cobrado_periodo = sum(p.monto for p in pagos_periodo)
            num_pagos_periodo = len(pagos_periodo)
            
            # Cartera actual
            cartera_actual = db.session.query(func.sum(Prestamo.saldo_actual)).filter_by(estado='ACTIVO').scalar()
            cartera_actual = float(cartera_actual) if cartera_actual else 0
            
            # Capital en circulación
            capital_circulacion = db.session.query(func.sum(Prestamo.monto_prestado)).filter_by(estado='ACTIVO').scalar()
            capital_circulacion = float(capital_circulacion) if capital_circulacion else 0
        
        # ===== DATOS PARA GRÁFICOS =====
        if rol == 'cobrador':
            # Pagos por día (solo sus pagos)
            pagos_por_dia = db.session.query(
                func.date(Pago.fecha_pago).label('fecha'),
                func.sum(Pago.monto).label('total')
            ).join(Prestamo).filter(
                Pago.fecha_pago >= fecha_inicio,
                Pago.fecha_pago <= fecha_fin,
                Prestamo.cobrador_id == usuario_id
            ).group_by(func.date(Pago.fecha_pago)).order_by('fecha').all()
            
            # Préstamos por estado (solo suyos)
            estados_prestamos = db.session.query(
                Prestamo.estado,
                func.count(Prestamo.id).label('cantidad')
            ).filter_by(cobrador_id=usuario_id).group_by(Prestamo.estado).all()
            
            # Top 5 clientes que más deben (solo sus préstamos)
            top_deudores = db.session.query(
                Cliente.nombre,
                Prestamo.saldo_actual
            ).join(Prestamo).filter(
                Prestamo.estado == 'ACTIVO',
                Prestamo.cobrador_id == usuario_id
            ).order_by(Prestamo.saldo_actual.desc()).limit(5).all()
            
            # Préstamos por frecuencia de pago (solo suyos)
            prestamos_por_frecuencia = db.session.query(
                Prestamo.frecuencia,
                func.count(Prestamo.id).label('cantidad')
            ).filter_by(estado='ACTIVO', cobrador_id=usuario_id).group_by(Prestamo.frecuencia).all()
            
            # Cobros por cobrador (solo él mismo)
            cobros_por_cobrador = db.session.query(
                Usuario.nombre,
                func.count(Pago.id).label('num_pagos'),
                func.sum(Pago.monto).label('total_cobrado')
            ).join(Pago, Usuario.id == Pago.cobrador_id).filter(
                Pago.fecha_pago >= fecha_inicio,
                Pago.fecha_pago <= fecha_fin,
                Usuario.id == usuario_id
            ).group_by(Usuario.nombre).all()
        else:
            # Pagos por día (todos)
            pagos_por_dia = db.session.query(
                func.date(Pago.fecha_pago).label('fecha'),
                func.sum(Pago.monto).label('total')
            ).filter(
                Pago.fecha_pago >= fecha_inicio,
                Pago.fecha_pago <= fecha_fin
            ).group_by(func.date(Pago.fecha_pago)).order_by('fecha').all()
            
            # Préstamos por estado
            estados_prestamos = db.session.query(
                Prestamo.estado,
                func.count(Prestamo.id).label('cantidad')
            ).group_by(Prestamo.estado).all()
            
            # Top 5 clientes que más deben
            top_deudores = db.session.query(
                Cliente.nombre,
                Prestamo.saldo_actual
            ).join(Prestamo).filter(
                Prestamo.estado == 'ACTIVO'
            ).order_by(Prestamo.saldo_actual.desc()).limit(5).all()
            
            # Préstamos por frecuencia de pago
            prestamos_por_frecuencia = db.session.query(
                Prestamo.frecuencia,
                func.count(Prestamo.id).label('cantidad')
            ).filter_by(estado='ACTIVO').group_by(Prestamo.frecuencia).all()
            
            # Cobros por cobrador
            cobros_por_cobrador = db.session.query(
                Usuario.nombre,
                func.count(Pago.id).label('num_pagos'),
                func.sum(Pago.monto).label('total_cobrado')
            ).join(Pago, Usuario.id == Pago.cobrador_id).filter(
                Pago.fecha_pago >= fecha_inicio,
                Pago.fecha_pago <= fecha_fin
            ).group_by(Usuario.nombre).all()
        
        # ===== LISTAS DETALLADAS PARA COBRADORES =====
        if rol == 'cobrador':
            # 1. Lista de pagos recibidos (clientes que pagaron)
            lista_pagos = Pago.query.join(Prestamo).join(Cliente).filter(
                Pago.fecha_pago >= fecha_inicio,
                Pago.fecha_pago <= fecha_fin,
                Prestamo.cobrador_id == usuario_id
            ).order_by(Pago.fecha_pago.desc()).all()
            
            # 2. Lista de créditos creados
            lista_creditos = Prestamo.query.join(Cliente).filter(
                Prestamo.fecha_inicio >= fecha_inicio,
                Prestamo.fecha_inicio <= fecha_fin,
                Prestamo.cobrador_id == usuario_id
            ).order_by(Prestamo.fecha_inicio.desc()).all()
            
            # 3. Lista de gastos/transacciones
            lista_gastos = Transaccion.query.filter(
                Transaccion.fecha >= fecha_inicio,
                Transaccion.fecha <= fecha_fin,
                Transaccion.usuario_origen_id == usuario_id
            ).order_by(Transaccion.fecha.desc()).all()
            
            # 4. Resumen de movimientos (todos los registros de actividad)
            lista_movimientos = []
            
            # Agregar pagos a movimientos
            for pago in lista_pagos:
                lista_movimientos.append({
                    'tipo': 'PAGO',
                    'fecha': pago.fecha_pago,
                    'descripcion': f'Pago de {pago.prestamo.cliente.nombre} - Crédito #{pago.prestamo_id}',
                    'monto': pago.monto,
                    'icono': 'bi-cash-coin',
                    'color': 'success'
                })
            
            # Agregar créditos a movimientos
            for credito in lista_creditos:
                lista_movimientos.append({
                    'tipo': 'CRÉDITO',
                    'fecha': credito.fecha_inicio,
                    'descripcion': f'Crédito creado para {credito.cliente.nombre} - #{credito.id}',
                    'monto': credito.monto_prestado,
                    'icono': 'bi-plus-circle',
                    'color': 'primary'
                })
            
            # Agregar gastos a movimientos
            for gasto in lista_gastos:
                lista_movimientos.append({
                    'tipo': 'GASTO',
                    'fecha': gasto.fecha,
                    'descripcion': f'{gasto.concepto}: {gasto.descripcion}',
                    'monto': gasto.monto,
                    'icono': 'bi-arrow-down-circle',
                    'color': 'danger'
                })
            
            # Ordenar movimientos por fecha descendente
            lista_movimientos.sort(key=lambda x: x['fecha'], reverse=True)
        else:
            lista_pagos = []
            lista_creditos = []
            lista_gastos = []
            lista_movimientos = []
        
        return render_template('reportes.html',
                             fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'),
                             fecha_fin=fecha_fin.strftime('%Y-%m-%d'),
                             total_clientes=total_clientes,
                             total_prestamos=total_prestamos,
                             prestamos_activos=prestamos_activos,
                             prestamos_cancelados=prestamos_cancelados,
                             total_prestado_periodo=total_prestado_periodo,
                             total_cobrado_periodo=total_cobrado_periodo,
                             num_pagos_periodo=num_pagos_periodo,
                             cartera_actual=cartera_actual,
                             capital_circulacion=capital_circulacion,
                             pagos_por_dia=pagos_por_dia,
                             estados_prestamos=estados_prestamos,
                             top_deudores=top_deudores,
                             prestamos_por_frecuencia=prestamos_por_frecuencia,
                             cobros_por_cobrador=cobros_por_cobrador,
                             lista_pagos=lista_pagos,
                             lista_creditos=lista_creditos,
                             lista_gastos=lista_gastos,
                             lista_movimientos=lista_movimientos,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    # ==================== GESTIÓN DE USUARIOS ====================
    @app.route('/usuarios')
    def usuarios_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        # Solo dueños y gerentes pueden ver usuarios
        if session.get('rol') not in ['dueno', 'gerente']:
            flash('No tienes permisos para acceder a esta sección')
            return redirect(url_for('dashboard'))
        
        usuarios = Usuario.query.all()
        
        # Contar cobros por usuario
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
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/usuarios/nuevo')
    def usuarios_nuevo():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        return render_template('usuarios_nuevo.html',
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/usuarios/guardar', methods=['POST'])
    def usuarios_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        try:
            nombre = request.form.get('nombre')
            usuario = request.form.get('usuario')
            password = request.form.get('password')
            rol = request.form.get('rol')
            
            # Validar que no exista el usuario
            usuario_existente = Usuario.query.filter_by(usuario=usuario).first()
            if usuario_existente:
                return render_template('usuarios_nuevo.html',
                                     error='El nombre de usuario ya existe',
                                     nombre=session.get('nombre'),
                                     rol=session.get('rol'))
            
            nuevo_usuario = Usuario(
                nombre=nombre,
                usuario=usuario,
                password=password,
                rol=rol,
                activo=True
            )
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            return redirect(url_for('usuarios_lista'))
        
        except Exception as e:
            db.session.rollback()
            return render_template('usuarios_nuevo.html',
                                 error=f'Error al crear usuario: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))
    
    @app.route('/usuarios/editar/<int:usuario_id>')
    def usuarios_editar(usuario_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        usuario = Usuario.query.get_or_404(usuario_id)
        
        return render_template('usuarios_editar.html',
                             usuario=usuario,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/usuarios/actualizar/<int:usuario_id>', methods=['POST'])
    def usuarios_actualizar(usuario_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        try:
            usuario = Usuario.query.get_or_404(usuario_id)
            
            usuario.nombre = request.form.get('nombre')
            usuario.rol = request.form.get('rol')
            
            # Solo actualizar contraseña si se proporciona una nueva
            nueva_password = request.form.get('password')
            if nueva_password:
                usuario.password = nueva_password
            
            activo = request.form.get('activo')
            usuario.activo = (activo == 'on')
            
            db.session.commit()
            
            return redirect(url_for('usuarios_lista'))
        
        except Exception as e:
            db.session.rollback()
            return render_template('usuarios_editar.html',
                                 usuario=usuario,
                                 error=f'Error al actualizar usuario: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))
    
    @app.route('/usuarios/eliminar/<int:usuario_id>')
    def usuarios_eliminar(usuario_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        # Solo el dueño puede eliminar usuarios
        if session.get('rol') != 'dueno':
            return redirect(url_for('dashboard'))
        
        # No permitir eliminar el propio usuario
        if usuario_id == session.get('usuario_id'):
            return redirect(url_for('usuarios_lista'))
        
        try:
            usuario = Usuario.query.get_or_404(usuario_id)
            
            # En lugar de eliminar, desactivar
            usuario.activo = False
            db.session.commit()
            
            return redirect(url_for('usuarios_lista'))
        
        except Exception as e:
            db.session.rollback()
            return redirect(url_for('usuarios_lista'))

    # ==================== SOCIEDADES ====================
    @app.route('/sociedades')
    def sociedades_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        sociedades = Sociedad.query.order_by(Sociedad.fecha_creacion.desc()).all()
        
        # Calcular estadísticas por sociedad
        stats_sociedades = []
        for sociedad in sociedades:
            num_rutas = Ruta.query.filter_by(sociedad_id=sociedad.id, activo=True).count()
            stats_sociedades.append({
                'sociedad': sociedad,
                'num_rutas': num_rutas
            })
        
        return render_template('sociedades_lista.html',
                             stats_sociedades=stats_sociedades,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/sociedades/nueva')
    def sociedades_nueva():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        return render_template('sociedades_nueva.html',
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/sociedades/guardar', methods=['POST'])
    def sociedades_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        try:
            # Validar que la suma de porcentajes no supere 100%
            p1 = float(request.form.get('porcentaje_socio', 50))
            p2 = float(request.form.get('porcentaje_socio_2', 0))
            p3 = float(request.form.get('porcentaje_socio_3', 0))
            
            if (p1 + p2 + p3) > 100:
                return render_template('sociedades_nueva.html',
                                     error='La suma de los porcentajes no puede superar el 100%',
                                     nombre=session.get('nombre'),
                                     rol=session.get('rol'))
            
            nueva_sociedad = Sociedad(
                nombre=request.form.get('nombre'),
                nombre_socio=request.form.get('nombre_socio'),
                telefono_socio=request.form.get('telefono_socio'),
                porcentaje_socio=p1,
                # Socio 2 (opcional)
                nombre_socio_2=request.form.get('nombre_socio_2') or None,
                telefono_socio_2=request.form.get('telefono_socio_2') or None,
                porcentaje_socio_2=p2,
                # Socio 3 (opcional)
                nombre_socio_3=request.form.get('nombre_socio_3') or None,
                telefono_socio_3=request.form.get('telefono_socio_3') or None,
                porcentaje_socio_3=p3,
                notas=request.form.get('notas'),
                activo=True
            )
            
            db.session.add(nueva_sociedad)
            db.session.commit()
            
            return redirect(url_for('sociedades_lista'))
        
        except Exception as e:
            db.session.rollback()
            return render_template('sociedades_nueva.html',
                                 error=f'Error al crear sociedad: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))

    @app.route('/sociedades/editar/<int:sociedad_id>')
    def sociedades_editar(sociedad_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        sociedad = Sociedad.query.get_or_404(sociedad_id)
        
        return render_template('sociedades_editar.html',
                             sociedad=sociedad,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/sociedades/actualizar/<int:sociedad_id>', methods=['POST'])
    def sociedades_actualizar(sociedad_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        try:
            sociedad = Sociedad.query.get_or_404(sociedad_id)
            
            # Validar porcentajes
            p1 = float(request.form.get('porcentaje_socio', 50))
            p2 = float(request.form.get('porcentaje_socio_2', 0))
            p3 = float(request.form.get('porcentaje_socio_3', 0))
            
            if (p1 + p2 + p3) > 100:
                return render_template('sociedades_editar.html',
                                     sociedad=sociedad,
                                     error='La suma de los porcentajes no puede superar el 100%',
                                     nombre=session.get('nombre'),
                                     rol=session.get('rol'))
            
            sociedad.nombre = request.form.get('nombre')
            sociedad.nombre_socio = request.form.get('nombre_socio')
            sociedad.telefono_socio = request.form.get('telefono_socio')
            sociedad.porcentaje_socio = p1
            
            # Socio 2
            sociedad.nombre_socio_2 = request.form.get('nombre_socio_2') or None
            sociedad.telefono_socio_2 = request.form.get('telefono_socio_2') or None
            sociedad.porcentaje_socio_2 = p2
            
            # Socio 3
            sociedad.nombre_socio_3 = request.form.get('nombre_socio_3') or None
            sociedad.telefono_socio_3 = request.form.get('telefono_socio_3') or None
            sociedad.porcentaje_socio_3 = p3
            
            sociedad.notas = request.form.get('notas')
            
            activo = request.form.get('activo')
            sociedad.activo = (activo == 'on')
            
            db.session.commit()
            
            return redirect(url_for('sociedades_lista'))
        
        except Exception as e:
            db.session.rollback()
            return render_template('sociedades_editar.html',
                                 sociedad=sociedad,
                                 error=f'Error al actualizar sociedad: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))

    # ==================== APORTES DE CAPITAL ====================
    @app.route('/capital/aportes')
    def capital_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        aportes = AporteCapital.query.order_by(AporteCapital.fecha_aporte.desc()).all()
        
        # Calcular totales por moneda
        total_pesos = db.session.query(func.sum(AporteCapital.monto)).filter(AporteCapital.moneda == 'PESOS').scalar() or 0
        total_reales = db.session.query(func.sum(AporteCapital.monto)).filter(AporteCapital.moneda == 'REALES').scalar() or 0
        
        return render_template('capital_lista.html',
                             aportes=aportes,
                             total_pesos=total_pesos,
                             total_reales=total_reales,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/capital/nuevo')
    def capital_nuevo():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        sociedades = Sociedad.query.order_by(Sociedad.nombre).all()
        
        return render_template('capital_nuevo.html',
                             sociedades=sociedades,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/capital/guardar', methods=['POST'])
    def capital_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        try:
            sociedad_id = request.form['sociedad_id']
            nombre_aportante = request.form['nombre_aportante']
            monto = float(request.form['monto'])
            moneda = request.form['moneda']
            fecha_aporte_str = request.form['fecha_aporte']
            descripcion = request.form.get('observaciones', '')
            
            # Convertir fecha
            fecha_aporte = datetime.strptime(fecha_aporte_str, '%Y-%m-%d')
            
            # Crear nuevo aporte
            nuevo_aporte = AporteCapital(
                sociedad_id=sociedad_id,
                nombre_aportante=nombre_aportante,
                monto=monto,
                moneda=moneda,
                fecha_aporte=fecha_aporte,
                descripcion=descripcion,
                registrado_por_id=session.get('usuario_id')
            )
            
            db.session.add(nuevo_aporte)
            db.session.commit()
            
            return redirect(url_for('capital_lista'))
            
        except Exception as e:
            db.session.rollback()
            sociedades = Sociedad.query.order_by(Sociedad.nombre).all()
            return render_template('capital_nuevo.html',
                                 sociedades=sociedades,
                                 error=f'Error al guardar aporte: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))

    # ==================== ACTIVOS FIJOS ====================
    @app.route('/activos')
    def activos_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        activos = Activo.query.order_by(Activo.fecha_compra.desc()).all()
        
        # Calcular total por categoría
        total_valor = db.session.query(func.sum(Activo.valor_compra)).scalar() or 0
        
        return render_template('activos_lista.html',
                             activos=activos,
                             total_valor=total_valor,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/activos/nuevo')
    def activos_nuevo():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        sociedades = Sociedad.query.order_by(Sociedad.nombre).all()
        rutas = Ruta.query.order_by(Ruta.nombre).all()
        usuarios = Usuario.query.order_by(Usuario.nombre).all()
        
        return render_template('activos_nuevo.html',
                             sociedades=sociedades,
                             rutas=rutas,
                             usuarios=usuarios,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/activos/guardar', methods=['POST'])
    def activos_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        try:
            nombre = request.form['nombre']
            categoria = request.form['categoria']
            valor_compra = float(request.form['valor_compra'])
            fecha_compra_str = request.form['fecha_compra']
            sociedad_id = request.form.get('sociedad_id')
            ruta_id = request.form.get('ruta_id')
            usuario_responsable_id = request.form.get('usuario_responsable_id')
            marca = request.form.get('marca', '')
            modelo = request.form.get('modelo', '')
            placa_serial = request.form.get('placa_serial', '')
            estado = request.form['estado']
            notas = request.form.get('observaciones', '')
            
            # Convertir fecha
            fecha_compra = datetime.strptime(fecha_compra_str, '%Y-%m-%d')
            
            # Crear nuevo activo
            nuevo_activo = Activo(
                nombre=nombre,
                categoria=categoria,
                valor_compra=valor_compra,
                fecha_compra=fecha_compra,
                sociedad_id=sociedad_id if sociedad_id else None,
                ruta_id=ruta_id if ruta_id else None,
                usuario_responsable_id=usuario_responsable_id if usuario_responsable_id else None,
                marca=marca,
                modelo=modelo,
                placa_serial=placa_serial,
                estado=estado,
                notas=notas,
                registrado_por_id=session.get('usuario_id')
            )
            
            db.session.add(nuevo_activo)
            db.session.commit()
            
            return redirect(url_for('activos_lista'))
            
        except Exception as e:
            db.session.rollback()
            sociedades = Sociedad.query.order_by(Sociedad.nombre).all()
            rutas = Ruta.query.order_by(Ruta.nombre).all()
            usuarios = Usuario.query.order_by(Usuario.nombre).all()
            return render_template('activos_nuevo.html',
                                 sociedades=sociedades,
                                 rutas=rutas,
                                 usuarios=usuarios,
                                 error=f'Error al guardar activo: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))

    # ==================== RUTAS ====================
    @app.route('/rutas')
    def rutas_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        rutas = Ruta.query.order_by(Ruta.nombre).all()
        
        # Calcular estadísticas por ruta
        stats_rutas = []
        for ruta in rutas:
            num_prestamos = Prestamo.query.filter_by(ruta_id=ruta.id, estado='ACTIVO').count()
            total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter(
                Prestamo.ruta_id == ruta.id,
                Prestamo.estado == 'ACTIVO'
            ).scalar() or 0
            
            stats_rutas.append({
                'ruta': ruta,
                'num_prestamos': num_prestamos,
                'total_cartera': total_cartera
            })
        
        return render_template('rutas_lista.html',
                             stats_rutas=stats_rutas,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/rutas/nueva')
    def rutas_nueva():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
        sociedades = Sociedad.query.filter_by(activo=True).all()
        
        return render_template('rutas_nueva.html',
                             cobradores=cobradores,
                             sociedades=sociedades,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/rutas/guardar', methods=['POST'])
    def rutas_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        try:
            cobrador_id = request.form.get('cobrador_id')
            sociedad_id = request.form.get('sociedad_id')
            pais_data = request.form.get('pais', 'Colombia|COP|$')
            
            # Parsear país, moneda y símbolo
            pais_parts = pais_data.split('|')
            pais = pais_parts[0] if len(pais_parts) > 0 else 'Colombia'
            moneda = pais_parts[1] if len(pais_parts) > 1 else 'COP'
            simbolo = pais_parts[2] if len(pais_parts) > 2 else '$'
            
            nueva_ruta = Ruta(
                nombre=request.form.get('nombre'),
                cobrador_id=int(cobrador_id) if cobrador_id else None,
                sociedad_id=int(sociedad_id) if sociedad_id and sociedad_id != '' else None,
                descripcion=request.form.get('descripcion'),
                pais=pais,
                moneda=moneda,
                simbolo_moneda=simbolo,
                activo=True
            )
            
            db.session.add(nueva_ruta)
            db.session.commit()
            
            return redirect(url_for('rutas_lista'))
        
        except Exception as e:
            db.session.rollback()
            cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
            sociedades = Sociedad.query.filter_by(activo=True).all()
            return render_template('rutas_nueva.html',
                                 cobradores=cobradores,
                                 sociedades=sociedades,
                                 error=f'Error al crear ruta: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))

    @app.route('/rutas/editar/<int:ruta_id>')
    def rutas_editar(ruta_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        ruta = Ruta.query.get_or_404(ruta_id)
        cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
        sociedades = Sociedad.query.filter_by(activo=True).all()
        
        return render_template('rutas_editar.html',
                             ruta=ruta,
                             cobradores=cobradores,
                             sociedades=sociedades,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/rutas/actualizar/<int:ruta_id>', methods=['POST'])
    def rutas_actualizar(ruta_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente']:
            return redirect(url_for('dashboard'))
        
        try:
            ruta = Ruta.query.get_or_404(ruta_id)
            
            ruta.nombre = request.form.get('nombre')
            cobrador_id = request.form.get('cobrador_id')
            ruta.cobrador_id = int(cobrador_id) if cobrador_id else None
            
            sociedad_id = request.form.get('sociedad_id')
            ruta.sociedad_id = int(sociedad_id) if sociedad_id and sociedad_id != '' else None
            
            ruta.descripcion = request.form.get('descripcion')
            
            activo = request.form.get('activo')
            ruta.activo = (activo == 'on')
            
            db.session.commit()
            
            return redirect(url_for('rutas_lista'))
        
        except Exception as e:
            db.session.rollback()
            cobradores = Usuario.query.filter_by(rol='cobrador', activo=True).all()
            sociedades = Sociedad.query.filter_by(activo=True).all()
            return render_template('rutas_editar.html',
                                 ruta=ruta,
                                 cobradores=cobradores,
                                 sociedades=sociedades,
                                 error=f'Error al actualizar ruta: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))

    # ==================== REPORTES PDF ====================
    @app.route('/reporte/seleccionar-cobrador')
    def reporte_seleccionar_cobrador():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        # Solo secretaria, gerente, supervisor y dueño pueden acceder
        if session.get('rol') not in ['secretaria', 'gerente', 'supervisor', 'dueno']:
            return redirect(url_for('dashboard'))
        
        # Obtener lista de cobradores
        cobradores = Usuario.query.filter(Usuario.rol.in_(['cobrador', 'supervisor'])).all()
        
        return render_template('reporte_seleccionar_cobrador.html',
                             cobradores=cobradores,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/reporte/cuadre-pdf')
    def reporte_cuadre_pdf():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        # Solo secretaria, gerente, supervisor y dueño pueden descargar
        if session.get('rol') not in ['secretaria', 'gerente', 'supervisor', 'dueno']:
            return redirect(url_for('dashboard'))
        
        # Obtener fecha (hoy por defecto)
        fecha = datetime.now()
        if request.args.get('fecha'):
            fecha = datetime.strptime(request.args.get('fecha'), '%Y-%m-%d')
        
        fecha_inicio = fecha.replace(hour=0, minute=0, second=0)
        fecha_fin = fecha.replace(hour=23, minute=59, second=59)
        
        # Determinar el cobrador a consultar
        # Si se especifica cobrador_id en la URL, usar ese; sino usar el usuario actual
        cobrador_id = request.args.get('cobrador_id', type=int)
        if cobrador_id:
            usuario = Usuario.query.get(cobrador_id)
            if not usuario:
                return "Cobrador no encontrado", 404
        else:
            usuario = Usuario.query.get(session.get('usuario_id'))
        
        # ABONOS (pagos recibidos hoy del cobrador seleccionado)
        pagos_hoy = Pago.query.filter(
            Pago.fecha_pago >= fecha_inicio,
            Pago.fecha_pago <= fecha_fin,
            Pago.cobrador_id == usuario.id
        ).all()
        
        total_abonos = sum(p.monto for p in pagos_hoy)
        
        # DESEMBOLSOS (préstamos creados hoy por el cobrador seleccionado)
        prestamos_hoy = Prestamo.query.filter(
            Prestamo.fecha_inicio >= fecha_inicio,
            Prestamo.fecha_inicio <= fecha_fin,
            Prestamo.cobrador_id == usuario.id
        ).all()
        
        total_desembolsos = sum(p.monto_prestado for p in prestamos_hoy)
        
        # TOTAL CAJA
        total_caja = total_abonos - total_desembolsos
        
        # GASTOS del día del cobrador
        gastos = Transaccion.query.filter(
            Transaccion.fecha >= fecha_inicio,
            Transaccion.fecha <= fecha_fin,
            Transaccion.naturaleza == 'EGRESO',
            Transaccion.usuario_origen_id == usuario.id
        ).all()
        
        # CLIENTES SIN PAGO (préstamos activos del cobrador que no pagaron hoy)
        # Obtener los IDs de préstamos que SÍ pagaron hoy
        prestamos_que_pagaron_hoy = [p.prestamo_id for p in pagos_hoy]
        
        # Préstamos activos del cobrador que NO pagaron hoy y tienen frecuencia DIARIO o BISEMANAL
        prestamos_activos = Prestamo.query.filter(
            Prestamo.estado == 'ACTIVO',
            Prestamo.cobrador_id == usuario.id,
            Prestamo.frecuencia.in_(['DIARIO', 'BISEMANAL'])
        ).all()
        
        clientes_sin_pago = []
        for prestamo in prestamos_activos:
            # Si NO pagó hoy
            if prestamo.id not in prestamos_que_pagaron_hoy:
                clientes_sin_pago.append({
                    'numero': prestamo.id,
                    'cliente': prestamo.cliente.nombre,
                    'celular': prestamo.cliente.telefono,
                    'valor': prestamo.valor_cuota
                })
        
        # CREAR PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title = Paragraph(f"<b>{usuario.nombre.upper()} - INFORME</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Fecha
        fecha_text = Paragraph(f"Fecha {fecha.strftime('%d/%m/%Y')}", styles['Normal'])
        elements.append(fecha_text)
        elements.append(Spacer(1, 0.3*inch))
        
        # CUADRE RUTA
        elements.append(Paragraph("<b>CUADRE RUTA</b>", styles['Heading2']))
        cuadre_data = [
            ['ABONOS', 'DESEMBOLSOS', 'TOTAL CAJA'],
            [f'${total_abonos:,.2f}', f'${total_desembolsos:,.2f}', f'${total_caja:,.2f}']
        ]
        cuadre_table = Table(cuadre_data, colWidths=[2*inch, 2*inch, 2*inch])
        cuadre_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(cuadre_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # GASTOS Y MOVIMIENTOS
        elements.append(Paragraph("<b>GASTOS Y MOVIMIENTOS</b>", styles['Heading2']))
        if gastos:
            gastos_data = [['CONCEPTO', 'DESCRIPCIÓN', 'VALOR ($)']]
            for gasto in gastos:
                gastos_data.append([
                    gasto.concepto or 'Sin concepto',
                    gasto.descripcion[:40] + '...' if gasto.descripcion and len(gasto.descripcion) > 40 else (gasto.descripcion or ''),
                    f"${gasto.monto:,.2f}"
                ])
            gastos_table = Table(gastos_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch])
            gastos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(gastos_table)
        else:
            elements.append(Paragraph("No hay gastos registrados", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # CRÉDITOS (PRÉSTAMOS OTORGADOS HOY)
        if prestamos_hoy:
            elements.append(Paragraph("<b>CRÉDITOS</b>", styles['Heading2']))
            creditos_data = [['CLIENTE', 'CELULAR', 'VALOR CRÉDITO ($)']]
            for prestamo in prestamos_hoy:
                creditos_data.append([
                    prestamo.cliente.nombre,
                    prestamo.cliente.telefono,
                    f"${prestamo.monto_prestado:,.2f}"
                ])
            creditos_table = Table(creditos_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            creditos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(creditos_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # CLIENTES SIN PAGO
        if clientes_sin_pago:
            elements.append(Paragraph("<b>CLIENTES SIN PAGO</b>", styles['Heading2']))
            sin_pago_data = [['N°', 'CLIENTE', 'CELULAR', 'VALOR']]
            for idx, cliente in enumerate(clientes_sin_pago[:10], 1):  # Máximo 10
                sin_pago_data.append([
                    str(idx),
                    cliente['cliente'],
                    cliente['celular'],
                    f"${cliente['valor']:,.2f}"
                ])
            sin_pago_table = Table(sin_pago_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
            sin_pago_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(sin_pago_table)
        
        # Construir PDF
        doc.build(elements)
        
        # Preparar respuesta
        pdf = buffer.getvalue()
        buffer.close()
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=cuadre_ruta_{fecha.strftime("%Y%m%d")}.pdf'
        
        return response

    # ==================== MÓDULO DE CAJA/FINANZAS ====================
    @app.route('/caja')
    def caja_inicio():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        usuario_id = session.get('usuario_id')
        rol = session.get('rol')
        
        # Obtener fecha actual
        hoy = datetime.now().date()
        
        # Calcular ingresos del día (pagos recibidos)
        if rol == 'cobrador':
            pagos_hoy = Pago.query.join(Prestamo).filter(
                func.date(Pago.fecha_pago) == hoy,
                Prestamo.cobrador_id == usuario_id
            ).all()
            # Traslados recibidos (ingresos)
            traslados_recibidos_hoy = Transaccion.query.filter(
                func.date(Transaccion.fecha) == hoy,
                Transaccion.usuario_destino_id == usuario_id,
                Transaccion.naturaleza == 'TRASLADO'
            ).all()
        else:
            pagos_hoy = Pago.query.filter(func.date(Pago.fecha_pago) == hoy).all()
            traslados_recibidos_hoy = []
        
        total_cobrado_hoy = sum(p.monto for p in pagos_hoy)
        total_traslados_recibidos = sum(t.monto for t in traslados_recibidos_hoy)
        
        # Calcular gastos del día (incluyendo traslados enviados)
        if rol == 'cobrador':
            gastos_hoy = Transaccion.query.filter(
                func.date(Transaccion.fecha) == hoy,
                Transaccion.usuario_origen_id == usuario_id
            ).all()
        else:
            gastos_hoy = Transaccion.query.filter(func.date(Transaccion.fecha) == hoy).all()
        
        total_gastos_hoy = sum(g.monto for g in gastos_hoy)
        
        # Balance del día (cobros + traslados recibidos - gastos - traslados enviados)
        balance_dia = total_cobrado_hoy + total_traslados_recibidos - total_gastos_hoy
        
        # Estadísticas del mes
        inicio_mes = datetime(hoy.year, hoy.month, 1)
        
        if rol == 'cobrador':
            pagos_mes = Pago.query.join(Prestamo).filter(
                Pago.fecha_pago >= inicio_mes,
                Prestamo.cobrador_id == usuario_id
            ).all()
            # Traslados recibidos del mes
            traslados_recibidos_mes = Transaccion.query.filter(
                Transaccion.fecha >= inicio_mes,
                Transaccion.usuario_destino_id == usuario_id,
                Transaccion.naturaleza == 'TRASLADO'
            ).all()
            gastos_mes = Transaccion.query.filter(
                Transaccion.fecha >= inicio_mes,
                Transaccion.usuario_origen_id == usuario_id
            ).all()
        else:
            pagos_mes = Pago.query.filter(Pago.fecha_pago >= inicio_mes).all()
            traslados_recibidos_mes = []
            gastos_mes = Transaccion.query.filter(Transaccion.fecha >= inicio_mes).all()
        
        total_cobrado_mes = sum(p.monto for p in pagos_mes)
        total_traslados_mes = sum(t.monto for t in traslados_recibidos_mes)
        total_gastos_mes = sum(g.monto for g in gastos_mes)
        balance_mes = total_cobrado_mes + total_traslados_mes - total_gastos_mes
        
        return render_template('caja_inicio.html',
                             total_cobrado_hoy=total_cobrado_hoy,
                             total_gastos_hoy=total_gastos_hoy,
                             balance_dia=balance_dia,
                             num_pagos_hoy=len(pagos_hoy),
                             num_gastos_hoy=len(gastos_hoy),
                             total_cobrado_mes=total_cobrado_mes,
                             total_gastos_mes=total_gastos_mes,
                             balance_mes=balance_mes,
                             fecha_hoy=hoy.strftime('%d/%m/%Y'),
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/caja/gastos')
    def caja_gastos():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        usuario_id = session.get('usuario_id')
        rol = session.get('rol')
        
        # Filtrar gastos según el rol
        if rol == 'cobrador':
            gastos = Transaccion.query.filter_by(usuario_origen_id=usuario_id).order_by(Transaccion.fecha.desc()).all()
        else:
            gastos = Transaccion.query.order_by(Transaccion.fecha.desc()).all()
        
        return render_template('caja_gastos.html',
                             gastos=gastos,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/caja/gastos/nuevo')
    def caja_gastos_nuevo():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        return render_template('caja_gastos_nuevo.html',
                             fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/caja/gastos/guardar', methods=['POST'])
    def caja_gastos_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        try:
            nueva_transaccion = Transaccion(
                naturaleza='EGRESO',
                concepto=request.form.get('concepto'),
                descripcion=request.form.get('descripcion'),
                monto=float(request.form.get('monto')),
                fecha=datetime.strptime(request.form.get('fecha'), '%Y-%m-%d'),
                usuario_origen_id=session.get('usuario_id')
            )
            
            db.session.add(nueva_transaccion)
            db.session.commit()
            
            return redirect(url_for('caja_gastos', mensaje='Gasto registrado exitosamente'))
        
        except Exception as e:
            db.session.rollback()
            return render_template('caja_gastos_nuevo.html',
                                 fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
                                 error=f'Error al guardar: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))
    
    @app.route('/caja/cuadre')
    def caja_cuadre():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        usuario_id = session.get('usuario_id')
        rol = session.get('rol')
        
        # Obtener fecha del filtro o usar hoy
        fecha_str = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        # Obtener pagos del día
        if rol == 'cobrador':
            pagos = Pago.query.join(Prestamo).join(Cliente).filter(
                func.date(Pago.fecha_pago) == fecha,
                Prestamo.cobrador_id == usuario_id
            ).all()
        else:
            pagos = Pago.query.join(Prestamo).join(Cliente).filter(
                func.date(Pago.fecha_pago) == fecha
            ).all()
        
        # Obtener gastos del día
        if rol == 'cobrador':
            gastos = Transaccion.query.filter(
                func.date(Transaccion.fecha) == fecha,
                Transaccion.usuario_origen_id == usuario_id
            ).all()
        else:
            gastos = Transaccion.query.filter(func.date(Transaccion.fecha) == fecha).all()
        
        # Calcular totales
        total_ingresos = sum(p.monto for p in pagos)
        total_gastos = sum(g.monto for g in gastos)
        efectivo_esperado = total_ingresos - total_gastos
        
        return render_template('caja_cuadre.html',
                             pagos=pagos,
                             gastos=gastos,
                             total_ingresos=total_ingresos,
                             total_gastos=total_gastos,
                             efectivo_esperado=efectivo_esperado,
                             fecha=fecha.strftime('%Y-%m-%d'),
                             fecha_display=fecha.strftime('%d/%m/%Y'),
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    # ==================== TRASLADOS ENTRE RUTAS ====================
    @app.route('/traslados')
    def traslados_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        # Solo dueño, gerente, supervisor y secretaria pueden ver traslados
        if session.get('rol') not in ['dueno', 'gerente', 'supervisor', 'secretaria']:
            return redirect(url_for('dashboard'))
        
        # Obtener traslados (transacciones de tipo TRASLADO)
        traslados = Transaccion.query.filter(
            Transaccion.concepto.like('TRASLADO%')
        ).order_by(Transaccion.fecha.desc()).limit(50).all()
        
        return render_template('traslados_lista.html',
                             traslados=traslados,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/traslados/nuevo')
    def traslados_nuevo():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        # Solo dueño, gerente y supervisor pueden hacer traslados
        if session.get('rol') not in ['dueno', 'gerente', 'supervisor']:
            return redirect(url_for('dashboard'))
        
        # Obtener lista de cobradores
        cobradores = Usuario.query.filter(Usuario.rol.in_(['cobrador', 'supervisor'])).all()
        
        return render_template('traslados_nuevo.html',
                             cobradores=cobradores,
                             fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/traslados/guardar', methods=['POST'])
    def traslados_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        if session.get('rol') not in ['dueno', 'gerente', 'supervisor']:
            return redirect(url_for('dashboard'))
        
        try:
            tipo_traslado = request.form.get('tipo_traslado')
            monto = float(request.form.get('monto'))
            descripcion = request.form.get('descripcion', '')
            fecha = datetime.strptime(request.form.get('fecha'), '%Y-%m-%d')
            
            usuario_id = session.get('usuario_id')
            
            # Crear transacción según el tipo
            if tipo_traslado == 'general_a_ruta':
                cobrador_id = int(request.form.get('cobrador_id'))
                # Salida de caja general (naturaleza EGRESO para caja general)
                transaccion = Transaccion(
                    naturaleza='TRASLADO',
                    concepto='TRASLADO A RUTA',
                    descripcion=f'Traslado a ruta de cobrador. {descripcion}',
                    monto=monto,
                    fecha=fecha,
                    usuario_origen_id=usuario_id,  # Quien hace el traslado (admin/supervisor)
                    usuario_destino_id=cobrador_id  # Cobrador que recibe
                )
            elif tipo_traslado == 'ruta_a_general':
                cobrador_id = int(request.form.get('cobrador_id'))
                # Entrada a caja general (naturaleza INGRESO para caja general)
                transaccion = Transaccion(
                    naturaleza='TRASLADO',
                    concepto='TRASLADO DE RUTA',
                    descripcion=f'Devolución de ruta de cobrador. {descripcion}',
                    monto=monto,
                    fecha=fecha,
                    usuario_origen_id=cobrador_id,  # Cobrador que entrega
                    usuario_destino_id=usuario_id  # Quien recibe (admin/supervisor)
                )
            else:  # ruta_a_ruta
                cobrador_origen_id = int(request.form.get('cobrador_origen_id'))
                cobrador_destino_id = int(request.form.get('cobrador_destino_id'))
                
                # Validar que no sean el mismo cobrador
                if cobrador_origen_id == cobrador_destino_id:
                    raise ValueError('El cobrador origen y destino no pueden ser el mismo')
                
                # Traslado entre rutas
                transaccion = Transaccion(
                    naturaleza='TRASLADO',
                    concepto='TRASLADO ENTRE RUTAS',
                    descripcion=f'Traslado entre cobradores. {descripcion}',
                    monto=monto,
                    fecha=fecha,
                    usuario_origen_id=cobrador_origen_id,  # Cobrador que entrega
                    usuario_destino_id=cobrador_destino_id  # Cobrador que recibe
                )
            
            db.session.add(transaccion)
            db.session.commit()
            
            return redirect(url_for('traslados_exito', traslado_id=transaccion.id))
        
        except Exception as e:
            db.session.rollback()
            cobradores = Usuario.query.filter(Usuario.rol.in_(['cobrador', 'supervisor'])).all()
            return render_template('traslados_nuevo.html',
                                 cobradores=cobradores,
                                 fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
                                 error=f'Error al registrar traslado: {str(e)}',
                                 nombre=session.get('nombre'),
                                 rol=session.get('rol'))
    
    @app.route('/traslados/exito/<int:traslado_id>')
    def traslados_exito(traslado_id):
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        traslado = Transaccion.query.get_or_404(traslado_id)
        
        return render_template('traslados_exito.html',
                             traslado=traslado,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    @app.route('/estado')
    def estado():
        return {"estado": "OK", "version": "1.0"}