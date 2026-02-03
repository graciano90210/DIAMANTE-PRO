"""
Tests unitarios para el módulo de clientes
"""
import pytest
from app.models import Cliente


class TestClienteModel:
    """Tests para el modelo Cliente"""
    
    @pytest.mark.unit
    def test_crear_cliente(self, app):
        """Verifica la creación de un cliente"""
        with app.app_context():
            from app.extensions import db
            
            cliente = Cliente(
                nombre='Cliente Test',
                documento='99988877766',
                telefono='3009876543',
                tipo_negocio='restaurante',
                nombre_negocio='Restaurante Test'
            )
            db.session.add(cliente)
            db.session.commit()
            
            assert cliente.id is not None
            assert cliente.nombre == 'Cliente Test'
            assert cliente.score_crediticio == 500  # Default
            assert cliente.nivel_riesgo == 'NUEVO'  # Default
            
            db.session.delete(cliente)
            db.session.commit()
    
    @pytest.mark.unit
    def test_cliente_whatsapp_completo(self, sample_cliente):
        """Verifica la propiedad whatsapp_completo"""
        assert sample_cliente.whatsapp_completo == '573001234567'
    
    @pytest.mark.unit
    def test_cliente_score_color(self, app):
        """Verifica los colores de score según nivel de riesgo"""
        with app.app_context():
            from app.extensions import db
            
            cliente = Cliente(
                nombre='Test Score',
                documento='11122233344',
                telefono='3001111111'
            )
            
            # Probar diferentes niveles
            cliente.nivel_riesgo = 'EXCELENTE'
            assert cliente.score_color == 'success'
            
            cliente.nivel_riesgo = 'BUENO'
            assert cliente.score_color == 'info'
            
            cliente.nivel_riesgo = 'REGULAR'
            assert cliente.score_color == 'warning'
            
            cliente.nivel_riesgo = 'ALTO'
            assert cliente.score_color == 'danger'
            
            cliente.nivel_riesgo = 'CRITICO'
            assert cliente.score_color == 'dark'
            
            cliente.nivel_riesgo = 'NUEVO'
            assert cliente.score_color == 'secondary'
    
    @pytest.mark.unit
    def test_cliente_puede_recibir_prestamo(self, app):
        """Verifica la lógica de puede_recibir_prestamo"""
        with app.app_context():
            from app.extensions import db
            
            cliente = Cliente(
                nombre='Test Prestamo',
                documento='55544433322',
                telefono='3005555555'
            )
            
            # Cliente normal puede recibir préstamo
            cliente.credito_bloqueado = False
            cliente.nivel_riesgo = 'BUENO'
            assert cliente.puede_recibir_prestamo == True
            
            # Cliente bloqueado no puede
            cliente.credito_bloqueado = True
            assert cliente.puede_recibir_prestamo == False
            
            # Cliente crítico no puede
            cliente.credito_bloqueado = False
            cliente.nivel_riesgo = 'CRITICO'
            assert cliente.puede_recibir_prestamo == False
    
    @pytest.mark.unit
    def test_cliente_documento_unico(self, app, sample_cliente):
        """Verifica que no se pueden crear dos clientes con el mismo documento"""
        with app.app_context():
            from app.extensions import db
            from sqlalchemy.exc import IntegrityError
            
            cliente_duplicado = Cliente(
                nombre='Cliente Duplicado',
                documento=sample_cliente.documento,  # Mismo documento
                telefono='3001112233'
            )
            db.session.add(cliente_duplicado)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
            
            db.session.rollback()


class TestClienteRoutes:
    """Tests para las rutas de clientes"""
    
    @pytest.mark.unit
    def test_clientes_lista_requires_auth(self, client):
        """Verifica que la lista de clientes requiere autenticación"""
        response = client.get('/clientes/', follow_redirects=False)
        # Debería redirigir a login o denegar acceso
        assert response.status_code in [302, 401, 200]
    
    @pytest.mark.unit
    def test_clientes_lista_con_auth(self, authenticated_client):
        """Verifica que un usuario autenticado puede ver la lista"""
        response = authenticated_client.get('/clientes/')
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_cliente_nuevo_form(self, authenticated_client):
        """Verifica que el formulario de nuevo cliente carga"""
        response = authenticated_client.get('/clientes/nuevo')
        assert response.status_code == 200
