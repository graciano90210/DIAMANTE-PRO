"""
Configuración de fixtures para tests de Diamante Pro
"""
import pytest
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Usuario, Cliente, Prestamo, Pago, Ruta, Sociedad


@pytest.fixture(scope='session')
def app():
    """Crea una instancia de la aplicación para testing"""
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['SECRET_KEY'] = 'test-secret-key-for-testing'
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': False,
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Cliente de prueba para hacer requests HTTP"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Sesión de base de datos para cada test"""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        yield db.session
        
        transaction.rollback()
        connection.close()


@pytest.fixture
def sample_user(app):
    """Crea un usuario de prueba"""
    with app.app_context():
        from werkzeug.security import generate_password_hash
        user = Usuario(
            nombre='Test User',
            usuario='testuser',
            password=generate_password_hash('testpass123'),
            rol='dueno',
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def sample_cobrador(app):
    """Crea un cobrador de prueba"""
    with app.app_context():
        from werkzeug.security import generate_password_hash
        user = Usuario(
            nombre='Test Cobrador',
            usuario='cobrador1',
            password=generate_password_hash('cobrador123'),
            rol='cobrador',
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def sample_ruta(app, sample_cobrador):
    """Crea una ruta de prueba"""
    with app.app_context():
        ruta = Ruta(
            nombre='Ruta Test Centro',
            cobrador_id=sample_cobrador.id,
            activo=True,
            pais='Colombia',
            moneda='COP',
            simbolo_moneda='$'
        )
        db.session.add(ruta)
        db.session.commit()
        yield ruta
        db.session.delete(ruta)
        db.session.commit()


@pytest.fixture
def sample_cliente(app, sample_ruta):
    """Crea un cliente de prueba"""
    with app.app_context():
        cliente = Cliente(
            nombre='Juan Pérez Test',
            documento='12345678901',
            telefono='3001234567',
            whatsapp_codigo_pais='57',
            whatsapp_numero='3001234567',
            direccion_negocio='Calle Test 123',
            tipo_negocio='tienda',
            nombre_negocio='Tienda Test',
            score_crediticio=700,
            nivel_riesgo='BUENO'
        )
        db.session.add(cliente)
        db.session.commit()
        yield cliente
        db.session.delete(cliente)
        db.session.commit()


@pytest.fixture
def sample_prestamo(app, sample_cliente, sample_ruta, sample_cobrador):
    """Crea un préstamo de prueba"""
    with app.app_context():
        prestamo = Prestamo(
            cliente_id=sample_cliente.id,
            ruta_id=sample_ruta.id,
            cobrador_id=sample_cobrador.id,
            monto_prestado=100000,
            tasa_interes=0.20,
            monto_a_pagar=120000,
            saldo_actual=120000,
            valor_cuota=6000,
            frecuencia='DIARIO',
            numero_cuotas=20,
            cuotas_pagadas=0,
            estado='ACTIVO',
            moneda='COP'
        )
        db.session.add(prestamo)
        db.session.commit()
        yield prestamo
        db.session.delete(prestamo)
        db.session.commit()


@pytest.fixture
def authenticated_client(client, sample_user):
    """Cliente autenticado para tests que requieren login"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(sample_user.id)
        sess['_fresh'] = True
    return client


def login_user(client, username, password):
    """Helper para hacer login en tests"""
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def logout_user(client):
    """Helper para hacer logout en tests"""
    return client.get('/logout', follow_redirects=True)
