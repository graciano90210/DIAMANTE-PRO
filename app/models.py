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
    rol = db.Column(db.String(20), nullable=False) # 'admin', 'cobrador', 'inversionista'
    activo = db.Column(db.Boolean, default=True)

# 2. LOS CLIENTES (Comerciantes)
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), unique=True, nullable=False)
    documento_negocio = db.Column(db.String(30)) 
    telefono = db.Column(db.String(20), nullable=False)
    direccion_negocio = db.Column(db.String(200))
    gps_latitud = db.Column(db.Float)
    gps_longitud = db.Column(db.Float)
    es_vip = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

# 3. LOS PRÉSTAMOS
class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    cobrador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    monto_prestado = db.Column(db.Float, nullable=False)
    tasa_interes = db.Column(db.Float, default=0.20)
    monto_a_pagar = db.Column(db.Float, nullable=False)
    saldo_actual = db.Column(db.Float, nullable=False)
    
    frecuencia = db.Column(db.String(20), default='DIARIO')
    estado = db.Column(db.String(20), default='ACTIVO')
    
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin_estimada = db.Column(db.DateTime)

# 4. LA CAJA
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