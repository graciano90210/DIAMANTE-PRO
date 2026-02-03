"""
Tests unitarios para los modelos de base de datos
"""
import pytest
from app.models import (
    Usuario, Cliente, Prestamo, Pago, 
    Ruta, Sociedad, AporteCapital, Activo,
    Transaccion, HistorialScoring, AlertaScoring
)


class TestModelsRelationships:
    """Tests para las relaciones entre modelos"""
    
    @pytest.mark.unit
    def test_ruta_tiene_cobrador(self, sample_ruta, sample_cobrador):
        """Verifica la relación Ruta -> Cobrador"""
        assert sample_ruta.cobrador_id == sample_cobrador.id
        assert sample_ruta.cobrador is not None
        assert sample_ruta.cobrador.nombre == 'Test Cobrador'
    
    @pytest.mark.unit
    def test_prestamo_tiene_cliente(self, sample_prestamo, sample_cliente):
        """Verifica la relación Prestamo -> Cliente"""
        assert sample_prestamo.cliente_id == sample_cliente.id
        assert sample_prestamo.cliente is not None
        assert sample_prestamo.cliente.nombre == sample_cliente.nombre
    
    @pytest.mark.unit
    def test_prestamo_tiene_ruta(self, sample_prestamo, sample_ruta):
        """Verifica la relación Prestamo -> Ruta"""
        assert sample_prestamo.ruta_id == sample_ruta.id
        assert sample_prestamo.ruta is not None
    
    @pytest.mark.unit
    def test_cascade_delete_cliente_elimina_prestamos(self, app):
        """Verifica que al eliminar cliente se eliminan sus préstamos (cascade)"""
        with app.app_context():
            from app.extensions import db
            from werkzeug.security import generate_password_hash
            
            # Crear cobrador
            cobrador = Usuario(
                nombre='Cobrador Cascade',
                usuario='cobrador_cascade',
                password=generate_password_hash('pass'),
                rol='cobrador'
            )
            db.session.add(cobrador)
            db.session.commit()
            
            # Crear ruta
            ruta = Ruta(
                nombre='Ruta Cascade',
                cobrador_id=cobrador.id
            )
            db.session.add(ruta)
            db.session.commit()
            
            # Crear cliente
            cliente = Cliente(
                nombre='Cliente Cascade',
                documento='99999999999',
                telefono='3009999999'
            )
            db.session.add(cliente)
            db.session.commit()
            cliente_id = cliente.id
            
            # Crear préstamo asociado al cliente
            prestamo = Prestamo(
                cliente_id=cliente.id,
                ruta_id=ruta.id,
                cobrador_id=cobrador.id,
                monto_prestado=10000,
                tasa_interes=0.20,
                monto_a_pagar=12000,
                saldo_actual=12000,
                valor_cuota=600,
                numero_cuotas=20
            )
            db.session.add(prestamo)
            db.session.commit()
            prestamo_id = prestamo.id
            
            # Eliminar cliente (debería eliminar préstamos en cascada)
            db.session.delete(cliente)
            db.session.commit()
            
            # Verificar que el préstamo fue eliminado
            prestamo_deleted = Prestamo.query.get(prestamo_id)
            assert prestamo_deleted is None
            
            # Limpiar
            db.session.delete(ruta)
            db.session.delete(cobrador)
            db.session.commit()


class TestSociedadModel:
    """Tests para el modelo Sociedad"""
    
    @pytest.mark.unit
    def test_crear_sociedad(self, app):
        """Verifica la creación de una sociedad"""
        with app.app_context():
            from app.extensions import db
            
            sociedad = Sociedad(
                nombre='Sociedad Test',
                nombre_socio='Juan Pérez',
                telefono_socio='3001234567',
                porcentaje_socio=50.0
            )
            db.session.add(sociedad)
            db.session.commit()
            
            assert sociedad.id is not None
            assert sociedad.porcentaje_dueno == 50.0
            
            db.session.delete(sociedad)
            db.session.commit()
    
    @pytest.mark.unit
    def test_sociedad_multiples_socios(self, app):
        """Verifica sociedad con múltiples socios"""
        with app.app_context():
            from app.extensions import db
            
            sociedad = Sociedad(
                nombre='Sociedad Multi',
                nombre_socio='Socio 1',
                porcentaje_socio=30.0,
                nombre_socio_2='Socio 2',
                porcentaje_socio_2=20.0,
                nombre_socio_3='Socio 3',
                porcentaje_socio_3=10.0
            )
            db.session.add(sociedad)
            db.session.commit()
            
            assert sociedad.tiene_multiples_socios == True
            assert sociedad.numero_socios == 3
            assert sociedad.porcentaje_dueno == 40.0  # 100 - 30 - 20 - 10
            
            db.session.delete(sociedad)
            db.session.commit()
    
    @pytest.mark.unit
    def test_sociedad_porcentaje_dueno(self, app):
        """Verifica el cálculo del porcentaje del dueño"""
        with app.app_context():
            from app.extensions import db
            
            # Sociedad con un socio al 50%
            sociedad = Sociedad(
                nombre='Sociedad 50-50',
                nombre_socio='Socio',
                porcentaje_socio=50.0
            )
            
            assert sociedad.porcentaje_dueno == 50.0
            
            # Sociedad con socio al 100% (dueño al 0%)
            sociedad.porcentaje_socio = 100.0
            assert sociedad.porcentaje_dueno == 0.0


class TestActivoModel:
    """Tests para el modelo Activo"""
    
    @pytest.mark.unit
    def test_crear_activo(self, app):
        """Verifica la creación de un activo"""
        with app.app_context():
            from app.extensions import db
            
            activo = Activo(
                nombre='Moto Honda Wave',
                categoria='VEHICULO',
                descripcion='Moto para cobrador',
                valor_compra=5000000,
                moneda='COP',
                marca='Honda',
                modelo='Wave',
                placa_serial='ABC123'
            )
            db.session.add(activo)
            db.session.commit()
            
            assert activo.id is not None
            assert activo.estado == 'ACTIVO'
            assert activo.categoria == 'VEHICULO'
            
            db.session.delete(activo)
            db.session.commit()
    
    @pytest.mark.unit
    def test_activo_categorias(self, app):
        """Verifica las diferentes categorías de activos"""
        categorias = ['VEHICULO', 'EQUIPO', 'INMUEBLE', 'OTRO']
        
        with app.app_context():
            from app.extensions import db
            
            for categoria in categorias:
                activo = Activo(
                    nombre=f'Activo {categoria}',
                    categoria=categoria,
                    valor_compra=100000
                )
                db.session.add(activo)
                db.session.commit()
                
                assert activo.categoria == categoria
                
                db.session.delete(activo)
                db.session.commit()


class TestTransaccionModel:
    """Tests para el modelo Transaccion"""
    
    @pytest.mark.unit
    def test_crear_transaccion(self, app, sample_user):
        """Verifica la creación de una transacción"""
        with app.app_context():
            from app.extensions import db
            
            transaccion = Transaccion(
                naturaleza='EGRESO',
                concepto='GASTO',
                descripcion='Gasolina',
                monto=50000,
                usuario_origen_id=sample_user.id
            )
            db.session.add(transaccion)
            db.session.commit()
            
            assert transaccion.id is not None
            assert transaccion.naturaleza == 'EGRESO'
            
            db.session.delete(transaccion)
            db.session.commit()
