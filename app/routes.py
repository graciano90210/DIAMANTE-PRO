from flask import render_template, request, redirect, url_for, session, flash, make_response
from .models import Usuario, Cliente, Prestamo, Pago, db
from datetime import datetime, timedelta
from sqlalchemy import func
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO

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
        
        # Estadísticas generales
        total_clientes = Cliente.query.count()
        clientes_vip = Cliente.query.filter_by(es_vip=True).count()
        
        # Préstamos activos
        prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO').all()
        total_prestamos_activos = len(prestamos_activos)
        
        # Cartera total (suma de saldos pendientes)
        total_cartera = db.session.query(func.sum(Prestamo.saldo_actual)).filter_by(estado='ACTIVO').scalar()
        total_cartera = float(total_cartera) if total_cartera else 0
        
        # Capital prestado (suma de montos originales activos)
        capital_prestado = db.session.query(func.sum(Prestamo.monto_prestado)).filter_by(estado='ACTIVO').scalar()
        capital_prestado = float(capital_prestado) if capital_prestado else 0
        
        # Por cobrar hoy (suma de valores de cuota de préstamos activos con pago diario o bisemanal)
        por_cobrar_hoy = sum(float(p.valor_cuota) for p in prestamos_activos if p.frecuencia in ['DIARIO', 'BISEMANAL']) if prestamos_activos else 0
        
        # Préstamos al día vs atrasados
        prestamos_al_dia = sum(1 for p in prestamos_activos if p.cuotas_atrasadas == 0) if prestamos_activos else 0
        prestamos_atrasados = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 0) if prestamos_activos else 0
        prestamos_mora = sum(1 for p in prestamos_activos if p.cuotas_atrasadas > 3) if prestamos_activos else 0
        
        # Total pagos realizados hoy
        hoy = datetime.now().date()
        pagos_hoy = Pago.query.filter(func.date(Pago.fecha_pago) == hoy).all()
        total_cobrado_hoy = sum(float(p.monto) for p in pagos_hoy) if pagos_hoy else 0
        num_pagos_hoy = len(pagos_hoy)
        
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
                             num_pagos_hoy=num_pagos_hoy)
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('home'))

    # ==================== CLIENTES ====================
    @app.route('/clientes')
    def clientes_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
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

    # ==================== PRÉSTAMOS ====================
    @app.route('/prestamos')
    def prestamos_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        prestamos = Prestamo.query.order_by(Prestamo.fecha_inicio.desc()).all()
        
        # Estadísticas
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
        
        return render_template('prestamos_nuevo.html',
                             clientes=clientes,
                             cobradores=cobradores,
                             fecha_hoy=datetime.now().strftime('%Y-%m-%d'),
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))
    
    @app.route('/prestamos/guardar', methods=['POST'])
    def prestamos_guardar():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        try:
            cliente_id = int(request.form.get('cliente_id'))
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
            
            return redirect(url_for('prestamos_lista', mensaje='Préstamo otorgado exitosamente'))
        
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

    # ==================== COBRO ====================
    @app.route('/cobro/lista')
    def cobro_lista():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        # Lista de préstamos activos
        prestamos = Prestamo.query.filter_by(estado='ACTIVO').order_by(
            Prestamo.cuotas_atrasadas.desc()
        ).all()
        
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
        
        # Generar mensaje de WhatsApp
        mensaje = f"""✅ *RECIBO DE PAGO - DIAMANTE PRO*

📋 *Crédito #:* {prestamo.id}
👤 *Cliente:* {cliente.nombre}
📅 *Fecha:* {pago.fecha_pago.strftime('%d/%m/%Y %H:%M')}

💰 *Monto Recibido:* {prestamo.moneda} {pago.monto:,.0f}
📊 *Saldo Anterior:* {prestamo.moneda} {pago.saldo_anterior:,.0f}
✨ *Saldo Nuevo:* {prestamo.moneda} {pago.saldo_nuevo:,.0f}

🎯 *Cuotas Pagadas:* {prestamo.cuotas_pagadas}/{prestamo.numero_cuotas}

¡Gracias por su pago! 💎"""
        
        whatsapp_url = f"https://wa.me/57{cliente.telefono}?text={mensaje.replace(' ', '%20').replace('\n', '%0A')}"
        
        return render_template('cobro_exito.html',
                             pago=pago,
                             prestamo=prestamo,
                             cliente=cliente,
                             whatsapp_url=whatsapp_url,
                             nombre=session.get('nombre'),
                             rol=session.get('rol'))

    # ==================== REPORTES ====================
    @app.route('/reportes')
    def reportes():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
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
        total_prestamos = Prestamo.query.count()
        prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO').count()
        prestamos_cancelados = Prestamo.query.filter_by(estado='CANCELADO').count()
        
        # ===== DATOS FINANCIEROS =====
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
        # Pagos por día (últimos 30 días)
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

    # ==================== REPORTES PDF ====================
    @app.route('/reporte/cuadre-pdf')
    def reporte_cuadre_pdf():
        if 'usuario_id' not in session:
            return redirect(url_for('home'))
        
        # Solo secretaria, gerente y dueño pueden descargar
        if session.get('rol') not in ['secretaria', 'gerente', 'dueno']:
            return redirect(url_for('dashboard'))
        
        # Obtener fecha (hoy por defecto)
        fecha = datetime.now()
        if request.args.get('fecha'):
            fecha = datetime.strptime(request.args.get('fecha'), '%Y-%m-%d')
        
        fecha_inicio = fecha.replace(hour=0, minute=0, second=0)
        fecha_fin = fecha.replace(hour=23, minute=59, second=59)
        
        # Usuario actual
        usuario = Usuario.query.get(session.get('usuario_id'))
        
        # ABONOS (pagos recibidos hoy)
        pagos_hoy = Pago.query.filter(
            Pago.fecha_pago >= fecha_inicio,
            Pago.fecha_pago <= fecha_fin,
            Pago.cobrador_id == session.get('usuario_id')
        ).all()
        
        total_abonos = sum(p.monto for p in pagos_hoy)
        
        # DESEMBOLSOS (préstamos creados hoy)
        prestamos_hoy = Prestamo.query.filter(
            Prestamo.fecha_inicio >= fecha_inicio,
            Prestamo.fecha_inicio <= fecha_fin
        ).all()
        
        total_desembolsos = sum(p.monto_prestado for p in prestamos_hoy)
        
        # TOTAL CAJA
        total_caja = total_abonos - total_desembolsos
        
        # GASTOS Y MOVIMIENTOS (ejemplo - puedes agregar una tabla de gastos)
        gastos = []
        
        # CLIENTES SIN PAGO (préstamos activos que debían pagar hoy y no pagaron)
        prestamos_activos = Prestamo.query.filter_by(estado='ACTIVO').all()
        clientes_sin_pago = []
        
        for prestamo in prestamos_activos:
            # Si tiene cuotas atrasadas
            if prestamo.cuotas_atrasadas and prestamo.cuotas_atrasadas > 0:
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
            gastos_data = [['OBSERVACIÓN', 'VALOR ($)']]
            for gasto in gastos:
                gastos_data.append([gasto['observacion'], f"${gasto['valor']:,.2f}"])
            gastos_table = Table(gastos_data, colWidths=[4*inch, 2*inch])
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

    @app.route('/estado')
    def estado():
        return {"estado": "OK", "version": "1.0"}