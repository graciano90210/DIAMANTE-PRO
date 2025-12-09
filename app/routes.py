from flask import render_template, request, redirect, url_for, session, flash
from .models import Usuario, Cliente, Prestamo, Pago, db
from datetime import datetime, timedelta
from sqlalchemy import func

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
        return render_template('dashboard.html', nombre=session.get('nombre'), rol=session.get('rol'))
    
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
        cobradores = Usuario.query.filter(Usuario.rol.in_(['admin', 'cobrador'])).all()
        
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
            
            monto = float(request.form.get('monto'))
            tipo_pago = request.form.get('tipo_pago')
            saldo_anterior = float(request.form.get('saldo_anterior'))
            
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

    @app.route('/estado')
    def estado():
        return {"estado": "OK", "version": "1.0"}