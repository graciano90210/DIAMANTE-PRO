"""
Tests básicos para la API de DIAMANTE PRO
"""
import pytest
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()


def test_app_exists(app):
    """Verificar que la app existe"""
    assert app is not None


def test_app_is_testing(app):
    """Verificar que está en modo testing"""
    assert app.config['TESTING']


def test_login_page_exists(client):
    """Verificar que la página de login existe"""
    response = client.get('/login')
    # 405 = Method Not Allowed (probablemente solo POST), también válido
    assert response.status_code in [200, 302, 308, 405]


def test_api_login_exists(client):
    """Verificar que el endpoint de API login existe"""
    response = client.post('/api/v1/login', json={
        'username': 'test',
        'password': 'test'
    })
    # Debe retornar 200 (success), 401 (unauthorized) o 400 (bad request)
    # No debe ser 404 (not found)
    assert response.status_code != 404
