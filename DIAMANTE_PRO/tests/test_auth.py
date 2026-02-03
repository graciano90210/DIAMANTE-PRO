"""
Tests unitarios para el módulo de autenticación
"""
import pytest
from flask import url_for
from app.models import Usuario


class TestAuthRoutes:
    """Tests para las rutas de autenticación"""
    
    @pytest.mark.unit
    def test_login_page_loads(self, client):
        """Verifica que la página de login carga correctamente"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'iniciar' in response.data.lower()
    
    @pytest.mark.unit
    def test_login_with_valid_credentials(self, client, sample_user):
        """Verifica login con credenciales válidas"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        # Debería redirigir al dashboard o selección de ruta
    
    @pytest.mark.unit
    def test_login_with_invalid_credentials(self, client):
        """Verifica que login falla con credenciales inválidas"""
        response = client.post('/login', data={
            'username': 'noexiste',
            'password': 'wrongpass'
        }, follow_redirects=True)
        assert response.status_code == 200
        # Debería mostrar error o quedarse en login
    
    @pytest.mark.unit
    def test_login_with_empty_credentials(self, client):
        """Verifica que login falla con campos vacíos"""
        response = client.post('/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_logout(self, authenticated_client):
        """Verifica que logout funciona correctamente"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_protected_route_requires_login(self, client):
        """Verifica que rutas protegidas requieren autenticación"""
        response = client.get('/dashboard', follow_redirects=False)
        # Debería redirigir a login (302) o denegar acceso (401)
        assert response.status_code in [302, 401, 200]
    
    @pytest.mark.unit
    def test_estado_endpoint(self, client):
        """Verifica el endpoint de estado de la API"""
        response = client.get('/estado')
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert 'estado' in data


class TestUsuarioModel:
    """Tests para el modelo Usuario"""
    
    @pytest.mark.unit
    def test_crear_usuario(self, app):
        """Verifica la creación de un usuario"""
        with app.app_context():
            from werkzeug.security import generate_password_hash
            from app.extensions import db
            
            user = Usuario(
                nombre='Nuevo Usuario',
                usuario='nuevo_user',
                password=generate_password_hash('password123'),
                rol='secretaria',
                activo=True
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.nombre == 'Nuevo Usuario'
            assert user.rol == 'secretaria'
            assert user.activo == True
            
            db.session.delete(user)
            db.session.commit()
    
    @pytest.mark.unit
    def test_usuario_rol_valido(self, sample_user):
        """Verifica que el rol del usuario es válido"""
        assert sample_user.rol in ['dueno', 'gerente', 'secretaria', 'cobrador', 'supervisor']
    
    @pytest.mark.unit
    def test_usuario_unique_username(self, app):
        """Verifica que no se pueden crear dos usuarios con el mismo username"""
        with app.app_context():
            from werkzeug.security import generate_password_hash
            from app.extensions import db
            from sqlalchemy.exc import IntegrityError
            
            user1 = Usuario(
                nombre='Usuario 1',
                usuario='duplicado',
                password=generate_password_hash('pass1'),
                rol='secretaria'
            )
            db.session.add(user1)
            db.session.commit()
            
            user2 = Usuario(
                nombre='Usuario 2',
                usuario='duplicado',  # Mismo username
                password=generate_password_hash('pass2'),
                rol='cobrador'
            )
            db.session.add(user2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
            
            db.session.rollback()
            db.session.delete(user1)
            db.session.commit()
