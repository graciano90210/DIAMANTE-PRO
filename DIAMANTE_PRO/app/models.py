
# Imports correctos para usar el Patrón de Extensiones
from .extensions import db
from flask_login import UserMixin
from datetime import datetime

# 1. LA GENTE (Staff y Usuarios)
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Almacena el hash bcrypt

    def set_password(self, raw_password):
        import bcrypt
        self.password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, raw_password):
        import bcrypt
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))
    rol = db.Column(db.String(20), nullable=False) # 'dueno', 'secretaria', 'supervisor', 'cobrador'
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

# 1.1 SOCIEDADES (Asociaciones con socios)
class Sociedad(db.Model):
    __tablename__ = 'sociedades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Ej: "Sociedad Norte", "Inversiones Centro"
    descripcion = db.Column(db.String(500))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.String(500))
    
    # ============ CAMPOS LEGACY (mantener por compatibilidad) ============
    # TODO: Migrar datos y eliminar estos campos en versión futura
    nombre_socio = db.Column(db.String(100))  # DEPRECATED: usar relación 'socios'
    telefono_socio = db.Column(db.String(20))  # DEPRECATED
    porcentaje_socio = db.Column(db.Float, default=0.0)  # DEPRECATED
    nombre_socio_2 = db.Column(db.String(100))  # DEPRECATED
    telefono_socio_2 = db.Column(db.String(20))  # DEPRECATED
    porcentaje_socio_2 = db.Column(db.Float, default=0.0)  # DEPRECATED
    nombre_socio_3 = db.Column(db.String(100))  # DEPRECATED
    telefono_socio_3 = db.Column(db.String(20))  # DEPRECATED
    porcentaje_socio_3 = db.Column(db.Float, default=0.0)  # DEPRECATED
    # =====================================================================
    
    # Relación con la nueva tabla de socios (Many-to-Many)
    socios = db.relationship('Socio', back_populates='sociedad', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def porcentaje_dueno(self):
        """Calcula el porcentaje del dueño restando los porcentajes de todos los socios"""
        # Primero intentar con la nueva estructura
        total_socios = sum(s.porcentaje for s in self.socios.all()) if self.socios.count() > 0 else 0
        # Fallback a campos legacy si no hay socios en la nueva tabla
        if total_socios == 0:
            total_socios = (self.porcentaje_socio or 0) + (self.porcentaje_socio_2 or 0) + (self.porcentaje_socio_3 or 0)
        return 100.0 - total_socios
    
    @property
    def tiene_multiples_socios(self):
        """Verifica si tiene más de un socio"""
        if self.socios.count() > 0:
            return self.socios.count() > 1
        return bool(self.nombre_socio_2) or bool(self.nombre_socio_3)
    
    @property
    def numero_socios(self):
        """Cuenta cuántos socios tiene (sin contar al dueño)"""
        if self.socios.count() > 0:
            return self.socios.count()
        # Fallback legacy
        count = 1 if self.nombre_socio else 0
        if self.nombre_socio_2:
            count += 1
        if self.nombre_socio_3:
            count += 1
        return count
    
    @property
    def lista_socios(self):
        """Retorna lista de socios con sus datos (compatible con nueva y vieja estructura)"""
        if self.socios.count() > 0:
            return [{'nombre': s.nombre, 'telefono': s.telefono, 'porcentaje': s.porcentaje, 
                     'email': s.email, 'tipo': s.tipo_socio} for s in self.socios.all()]
        # Fallback legacy
        socios_legacy = []
        if self.nombre_socio:
            socios_legacy.append({'nombre': self.nombre_socio, 'telefono': self.telefono_socio, 
                                  'porcentaje': self.porcentaje_socio or 0, 'email': None, 'tipo': 'INVERSOR'})
        if self.nombre_socio_2:
            socios_legacy.append({'nombre': self.nombre_socio_2, 'telefono': self.telefono_socio_2,
                                  'porcentaje': self.porcentaje_socio_2 or 0, 'email': None, 'tipo': 'INVERSOR'})
        if self.nombre_socio_3:
            socios_legacy.append({'nombre': self.nombre_socio_3, 'telefono': self.telefono_socio_3,
                                  'porcentaje': self.porcentaje_socio_3 or 0, 'email': None, 'tipo': 'INVERSOR'})
        return socios_legacy


# 1.1.1 SOCIOS (Tabla intermedia Many-to-Many para inversionistas)
class Socio(db.Model):
    """
    Modelo para socios/inversionistas de una sociedad.
    Permite múltiples socios dinámicos por sociedad.
    """
    __tablename__ = 'socios'
    id = db.Column(db.Integer, primary_key=True)
    sociedad_id = db.Column(db.Integer, db.ForeignKey('sociedades.id'), nullable=False)
    
    # Datos del socio
    nombre = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(30))  # CPF, CNPJ, etc.
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    
    # Participación
    porcentaje = db.Column(db.Float, nullable=False, default=0.0)  # % de participación
    monto_aportado = db.Column(db.Float, default=0.0)  # Capital total aportado
    
    # Tipo de socio
    tipo_socio = db.Column(db.String(20), default='INVERSOR')  # INVERSOR, SOCIO_ACTIVO, SOCIO_CAPITALISTA
    
    # Estado
    activo = db.Column(db.Boolean, default=True)
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_salida = db.Column(db.DateTime)
    
    # Datos bancarios para distribución de ganancias
    banco = db.Column(db.String(50))
    cuenta_bancaria = db.Column(db.String(50))
    tipo_cuenta = db.Column(db.String(20))  # AHORRO, CORRIENTE
    
    notas = db.Column(db.String(500))
    
    # Relación inversa
    sociedad = db.relationship('Sociedad', back_populates='socios')
    
    def __repr__(self):
        return f'<Socio {self.nombre} - {self.porcentaje}%>'


# 1.1.2 OFICINAS (Agrupación de rutas por zona/región)
class Oficina(db.Model):
    """
    Modelo para agrupar rutas en oficinas/zonas.
    Útil cuando un inversionista tiene muchas rutas y necesita organizarlas.
    Jerarquía: Sociedad → Oficinas → Rutas
    """
    __tablename__ = 'oficinas'
    id = db.Column(db.Integer, primary_key=True)
    
    # Datos básicos
    nombre = db.Column(db.String(100), nullable=False)  # Ej: "Oficina Centro", "Oficina Norte"
    codigo = db.Column(db.String(20))  # Código corto: "OFC-01", "NORTE"
    descripcion = db.Column(db.String(300))
    
    # Ubicación
    direccion = db.Column(db.String(200))
    ciudad = db.Column(db.String(100))
    estado = db.Column(db.String(50))  # Departamento/Estado
    pais = db.Column(db.String(50), default='Colombia')
    
    # Responsable de la oficina
    responsable_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    telefono_oficina = db.Column(db.String(20))
    email_oficina = db.Column(db.String(100))
    
    # Pertenencia (puede ser de una sociedad o directamente del dueño)
    sociedad_id = db.Column(db.Integer, db.ForeignKey('sociedades.id'), nullable=True)
    
    # Estado
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Configuración de la oficina
    meta_cobro_diario = db.Column(db.Float, default=0)  # Meta de cobro diario
    meta_prestamos_mes = db.Column(db.Float, default=0)  # Meta de préstamos mensuales
    
    notas = db.Column(db.String(500))
    
    # Relaciones
    responsable = db.relationship('Usuario', backref=db.backref('oficinas_responsable', lazy='dynamic'))
    sociedad = db.relationship('Sociedad', backref=db.backref('oficinas', lazy='dynamic'))
    rutas = db.relationship('Ruta', backref='oficina', lazy='dynamic')
    
    @property
    def numero_rutas(self):
        """Retorna el número de rutas activas en esta oficina"""
        return self.rutas.filter_by(activo=True).count()
    
    @property
    def total_cartera(self):
        """Calcula el total de cartera activa de todas las rutas de la oficina"""
        from sqlalchemy import func
        total = db.session.query(func.sum(Prestamo.saldo_actual)).join(Ruta).filter(
            Ruta.oficina_id == self.id,
            Prestamo.estado == 'ACTIVO'
        ).scalar()
        return float(total or 0)
    
    def __repr__(self):
        return f'<Oficina {self.nombre}>'


# 1.2 RUTAS (Con nombre propio, independientes del cobrador)
class Ruta(db.Model):
    __tablename__ = 'rutas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Ej: "Ruta Centro", "Ruta Norte"
    cobrador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Puede cambiar
    sociedad_id = db.Column(db.Integer, db.ForeignKey('sociedades.id'), nullable=True)  # NULL = PROPIO
    oficina_id = db.Column(db.Integer, db.ForeignKey('oficinas.id'), nullable=True)  # Agrupación por oficina
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(200))
    
    # País y moneda
    pais = db.Column(db.String(50), default='Colombia')  # Colombia, Brasil, Perú, Argentina, USA
    moneda = db.Column(db.String(3), default='COP')  # COP, BRL, PEN, ARS, USD
    simbolo_moneda = db.Column(db.String(5), default='$')  # $, R$, S/, $, USD
    
    # Relaciones con cascade
    cobrador = db.relationship('Usuario', backref=db.backref('rutas_asignadas', lazy='dynamic'))
    sociedad = db.relationship('Sociedad', backref=db.backref('rutas', lazy='dynamic'))

# 2. LOS CLIENTES (Comerciantes)
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), unique=True, nullable=False) # CPF (Documento Personal)
    tipo_documento = db.Column(db.String(20), default='CPF') # Siempre CPF para el cliente
    fecha_nacimiento = db.Column(db.Date) # Nueva fecha de nacimiento
    # documento_negocio se mueve a la sección FORMALIZACIÓN FISCAL para evitar duplicidad
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100)) # Email de contacto
    whatsapp_codigo_pais = db.Column(db.String(5), default='57')  # Código de país para WhatsApp
    whatsapp_numero = db.Column(db.String(20))  # Número WhatsApp sin código de país
    
    # Direcciones detalladas
    direccion_negocio = db.Column(db.String(200))
    cep_negocio = db.Column(db.String(20)) # CEP del negocio
    direccion_casa = db.Column(db.String(200)) # Dirección de casa
    cep_casa = db.Column(db.String(20)) # CEP de casa
    
    gps_latitud = db.Column(db.Float)  # GPS del negocio
    gps_longitud = db.Column(db.Float)  # GPS del negocio
    gps_latitud_casa = db.Column(db.Float)  # GPS de residencia
    gps_longitud_casa = db.Column(db.Float)  # GPS de residencia
    es_vip = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # NUEVOS CAMPOS PARA SCORING (Capacidad de Pago y Estabilidad)
    gastos_mensuales_promedio = db.Column(db.Float) # Vital para calcular capacidad de pago real
    personas_a_cargo = db.Column(db.Integer, default=0) # Carga familiar afecta riesgo
    estado_civil = db.Column(db.String(20)) # SOLTERO, CASADO, UNION_LIBRE
    tiempo_residencia_meses = db.Column(db.Integer) # Estabilidad domiciliaria (meses viviendo ahí)
    
    # ==================== DATOS DEL COMERCIO (Scoring) ====================
    tipo_negocio = db.Column(db.String(50))  # tienda, restaurante, ferretería, peluquería, etc.
    nombre_negocio = db.Column(db.String(100))  # Nombre del comercio
    antiguedad_negocio_meses = db.Column(db.Integer)  # Meses que lleva el negocio
    local_propio = db.Column(db.Boolean, default=False)  # ¿Es dueño o alquila?
    dias_trabajo = db.Column(db.String(20))  # L-V, L-S, L-D
    hora_cobro_preferida = db.Column(db.String(10))  # 08:00, 10:00, etc.
    ingresos_diarios_estimados = db.Column(db.Float)  # Ventas diarias aproximadas
    referido_por_cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)  # Quién lo recomendó
    
    # ==================== FORMALIZACIÓN FISCAL (Scoring) ====================
    negocio_formalizado = db.Column(db.Boolean, default=False)  # ¿Tiene registro fiscal?
    tipo_documento_fiscal = db.Column(db.String(20), default='CNPJ')  # CNPJ (Documento del Negocio)
    documento_fiscal_negocio = db.Column(db.String(30))  # Número del CNPJ
    fecha_verificacion_fiscal = db.Column(db.DateTime)  # Cuándo se verificó
    
    # ==================== COMPROBANTE DE RESIDENCIA (Scoring) ====================
    tiene_comprobante_residencia = db.Column(db.Boolean, default=False)
    tipo_comprobante_residencia = db.Column(db.String(30))  # LUZ, AGUA, INTERNET, GAS, ALQUILER, ESCRITURA
    comprobante_a_nombre_propio = db.Column(db.Boolean, default=False)  # ¿A su nombre?
    nombre_titular_comprobante = db.Column(db.String(100))  # Si no está a su nombre
    parentesco_titular = db.Column(db.String(30))  # esposa, padre, hermano, etc.
    fecha_comprobante = db.Column(db.Date)  # Fecha del comprobante
    foto_comprobante_residencia = db.Column(db.String(300))  # Ruta del archivo
    
    # ==================== SCORING CREDITICIO (Calculado por IA) ====================
    score_crediticio = db.Column(db.Integer, default=500)  # 0-1000 puntos
    nivel_riesgo = db.Column(db.String(20), default='NUEVO')  # EXCELENTE, BUENO, REGULAR, ALTO, CRITICO, NUEVO
    limite_credito_sugerido = db.Column(db.Float)  # Máximo a prestar según IA
    credito_bloqueado = db.Column(db.Boolean, default=False)  # No prestarle más
    motivo_bloqueo = db.Column(db.String(200))  # Razón del bloqueo
    fecha_ultimo_calculo_score = db.Column(db.DateTime)  # Última actualización del score
    
    # Relación con el cliente que lo refirió
    referido_por = db.relationship('Cliente', remote_side=[id], backref='clientes_referidos')
    
    @property
    def whatsapp_completo(self):
        """Retorna el número completo de WhatsApp con código de país"""
        if self.whatsapp_numero:
            return f"{self.whatsapp_codigo_pais}{self.whatsapp_numero}"
        return self.telefono  # Fallback al teléfono regular
    
    @property
    def score_color(self):
        """Retorna el color CSS según el nivel de riesgo"""
        colores = {
            'EXCELENTE': 'success',
            'BUENO': 'info',
            'REGULAR': 'warning',
            'ALTO': 'danger',
            'CRITICO': 'dark',
            'NUEVO': 'secondary'
        }
        return colores.get(self.nivel_riesgo, 'secondary')
    
    @property
    def puede_recibir_prestamo(self):
        """Verifica si el cliente puede recibir un nuevo préstamo"""
        if self.credito_bloqueado:
            return False
        if self.nivel_riesgo == 'CRITICO':
            return False
        return True

# 3. LOS PRÉSTAMOS
class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    ruta_id = db.Column(db.Integer, db.ForeignKey('rutas.id'), nullable=False)  # Ahora se asocia a la ruta
    cobrador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Mantener por compatibilidad temporal
    
    # Montos
    monto_prestado = db.Column(db.Float, nullable=False)
    tasa_interes = db.Column(db.Float, default=0.20)  # 20% o 15% VIP
    monto_a_pagar = db.Column(db.Float, nullable=False)
    saldo_actual = db.Column(db.Float, nullable=False)
    valor_cuota = db.Column(db.Float, nullable=False)
    
    # Multidivisa
    moneda = db.Column(db.String(3), default='COP')  # COP, USD, PEN, BRL, ARS
    
    # Configuración
    frecuencia = db.Column(db.String(20), default='DIARIO')  # DIARIO, SEMANAL, QUINCENAL
    numero_cuotas = db.Column(db.Integer, nullable=False)
    cuotas_pagadas = db.Column(db.Integer, default=0)
    cuotas_atrasadas = db.Column(db.Integer, default=0)
    
    # Estado
    estado = db.Column(db.String(20), default='ACTIVO')  # ACTIVO, CANCELADO, MORA
    
    # Fechas
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin_estimada = db.Column(db.DateTime)
    fecha_ultimo_pago = db.Column(db.DateTime)
    
    # Relaciones con cascade
    cliente = db.relationship('Cliente', backref=db.backref('prestamos', lazy='dynamic', cascade='all, delete-orphan'))
    ruta = db.relationship('Ruta', backref=db.backref('prestamos', lazy='dynamic'))
    cobrador = db.relationship('Usuario', backref=db.backref('prestamos_asignados', lazy='dynamic'))

# 4. LOS PAGOS
class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    prestamo_id = db.Column(db.Integer, db.ForeignKey('prestamos.id'), nullable=False)
    cobrador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    monto = db.Column(db.Float, nullable=False)
    numero_cuotas_pagadas = db.Column(db.Integer, default=1)
    saldo_anterior = db.Column(db.Float, nullable=False)
    saldo_nuevo = db.Column(db.Float, nullable=False)
    
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.String(500))
    tipo_pago = db.Column(db.String(20), default='NORMAL')  # NORMAL, ABONO, COMPLETO
    
    # Relaciones con cascade
    prestamo = db.relationship('Prestamo', backref=db.backref('pagos', lazy='dynamic', cascade='all, delete-orphan'))
    cobrador = db.relationship('Usuario', backref=db.backref('pagos_realizados', lazy='dynamic'))

# 5. LA CAJA
class Transaccion(db.Model):
    __tablename__ = 'transacciones'
    id = db.Column(db.Integer, primary_key=True)
    naturaleza = db.Column(db.String(20), nullable=False) 
    concepto = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200))
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario_origen_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario_destino_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    prestamo_id = db.Column(db.Integer, db.ForeignKey('prestamos.id'), nullable=True)
    foto_evidencia = db.Column(db.String(300))
    
    # Relaciones
    usuario_origen = db.relationship('Usuario', foreign_keys=[usuario_origen_id], backref='transacciones_origen')
    usuario_destino = db.relationship('Usuario', foreign_keys=[usuario_destino_id], backref='transacciones_destino')

# 6. APORTES DE CAPITAL
class AporteCapital(db.Model):
    __tablename__ = 'aportes_capital'
    id = db.Column(db.Integer, primary_key=True)
    sociedad_id = db.Column(db.Integer, db.ForeignKey('sociedades.id'), nullable=False)
    nombre_aportante = db.Column(db.String(100), nullable=False)  # Nombre del socio que aporta
    monto = db.Column(db.Float, nullable=False)
    moneda = db.Column(db.String(3), default='COP')  # COP, USD, BRL, PEN, ARS
    tipo_aporte = db.Column(db.String(20), default='EFECTIVO')  # EFECTIVO, TRANSFERENCIA, CHEQUE
    fecha_aporte = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.String(200))
    comprobante = db.Column(db.String(300))  # Ruta de imagen del comprobante
    registrado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relaciones con cascade
    sociedad = db.relationship('Sociedad', backref=db.backref('aportes', lazy='dynamic', cascade='all, delete-orphan'))
    registrado_por = db.relationship('Usuario', backref=db.backref('aportes_registrados', lazy='dynamic'))

# 7. ACTIVOS FIJOS
class Activo(db.Model):
    __tablename__ = 'activos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Ej: "Moto Honda Wave"
    categoria = db.Column(db.String(50), nullable=False)  # VEHICULO, EQUIPO, INMUEBLE, OTRO
    descripcion = db.Column(db.String(200))
    valor_compra = db.Column(db.Float, nullable=False)
    moneda = db.Column(db.String(3), default='COP')
    fecha_compra = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Asociación (puede ser propio o de una sociedad)
    sociedad_id = db.Column(db.Integer, db.ForeignKey('sociedades.id'), nullable=True)  # NULL = PROPIO
    ruta_id = db.Column(db.Integer, db.ForeignKey('rutas.id'), nullable=True)  # Asignado a qué ruta
    usuario_responsable_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Usuario que lo usa
    
    # Información adicional
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    placa_serial = db.Column(db.String(50))  # Placa de vehículo o serial de equipo
    estado = db.Column(db.String(20), default='ACTIVO')  # ACTIVO, EN_MANTENIMIENTO, VENDIDO, INACTIVO
    foto = db.Column(db.String(300))
    notas = db.Column(db.String(500))
    
    registrado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # Relaciones
    sociedad = db.relationship('Sociedad', backref='activos')
    ruta = db.relationship('Ruta', backref='activos_asignados')
    usuario_responsable = db.relationship('Usuario', foreign_keys=[usuario_responsable_id], backref='activos_a_cargo')
    registrado_por = db.relationship('Usuario', foreign_keys=[registrado_por_id], backref='activos_registrados')


# 8. HISTORIAL DE SCORING (Para IA y auditoría)
class HistorialScoring(db.Model):
    __tablename__ = 'historial_scoring'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    # Scores
    score_anterior = db.Column(db.Integer)
    score_nuevo = db.Column(db.Integer, nullable=False)
    nivel_riesgo_anterior = db.Column(db.String(20))
    nivel_riesgo_nuevo = db.Column(db.String(20), nullable=False)
    
    # Límites de crédito
    limite_anterior = db.Column(db.Float)
    limite_nuevo = db.Column(db.Float)
    
    # Detalles del cálculo (JSON con los factores)
    factores_calculo = db.Column(db.Text)  # JSON con puntaje por cada factor
    # Ejemplo: {"antiguedad_negocio": 80, "tasa_pago": 250, "comprobante_residencia": 150, ...}
    
    # Metadatos
    fecha_calculo = db.Column(db.DateTime, default=datetime.utcnow)
    calculado_por = db.Column(db.String(50), default='SISTEMA')  # SISTEMA, MANUAL, RECALCULO_MASIVO
    observaciones = db.Column(db.String(500))
    
    # Relaciones con cascade
    cliente = db.relationship('Cliente', backref=db.backref('historial_scores', lazy='dynamic', cascade='all, delete-orphan'))


# 9. ALERTAS DE SCORING (Recomendaciones de la IA)
class AlertaScoring(db.Model):
    __tablename__ = 'alertas_scoring'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    tipo_alerta = db.Column(db.String(30), nullable=False)  
    # SUBIR_CREDITO, BAJAR_CREDITO, BLOQUEAR, REVISAR_MANUAL, CLIENTE_ESTRELLA
    
    mensaje = db.Column(db.String(500), nullable=False)  # Descripción de la alerta
    accion_sugerida = db.Column(db.String(200))  # Qué debería hacer el dueño
    
    prioridad = db.Column(db.String(10), default='MEDIA')  # ALTA, MEDIA, BAJA
    
    # Estado de la alerta
    estado = db.Column(db.String(20), default='PENDIENTE')  # PENDIENTE, VISTA, ATENDIDA, IGNORADA
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_atencion = db.Column(db.DateTime)
    atendida_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    notas_atencion = db.Column(db.String(500))
    
    # Relaciones con cascade
    cliente = db.relationship('Cliente', backref=db.backref('alertas_scoring', lazy='dynamic', cascade='all, delete-orphan'))
    atendida_por = db.relationship('Usuario', backref=db.backref('alertas_atendidas', lazy='dynamic'))