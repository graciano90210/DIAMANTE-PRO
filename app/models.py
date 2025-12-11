from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 1. LA GENTE (Staff y Usuarios)
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False) # 'dueno', 'secretaria', 'supervisor', 'cobrador'
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

# 2. LOS CLIENTES (Comerciantes)
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), unique=True, nullable=False)
    documento_negocio = db.Column(db.String(30)) 
    telefono = db.Column(db.String(20), nullable=False)
    whatsapp_codigo_pais = db.Column(db.String(5), default='57')  # Código de país para WhatsApp
    whatsapp_numero = db.Column(db.String(20))  # Número WhatsApp sin código de país
    direccion_negocio = db.Column(db.String(200))
    gps_latitud = db.Column(db.Float)
    gps_longitud = db.Column(db.Float)
    es_vip = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def whatsapp_completo(self):
        """Retorna el número completo de WhatsApp con código de país"""
        if self.whatsapp_numero:
            return f"{self.whatsapp_codigo_pais}{self.whatsapp_numero}"
        return self.telefono  # Fallback al teléfono regular

# 3. LOS PRÉSTAMOS
class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    cobrador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
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
    
    # Relaciones
    cliente = db.relationship('Cliente', backref='prestamos')
    cobrador = db.relationship('Usuario', backref='prestamos_asignados')

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
    
    # Relaciones
    prestamo = db.relationship('Prestamo', backref='pagos')
    cobrador = db.relationship('Usuario', backref='pagos_realizados')

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