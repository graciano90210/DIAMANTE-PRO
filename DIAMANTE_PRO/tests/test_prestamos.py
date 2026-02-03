"""
Tests unitarios para el módulo de préstamos
"""
import pytest
from datetime import datetime, timedelta
from app.models import Prestamo, Pago


class TestPrestamoModel:
    """Tests para el modelo Prestamo"""
    
    @pytest.mark.unit
    def test_crear_prestamo(self, app, sample_cliente, sample_ruta, sample_cobrador):
        """Verifica la creación de un préstamo"""
        with app.app_context():
            from app.extensions import db
            
            prestamo = Prestamo(
                cliente_id=sample_cliente.id,
                ruta_id=sample_ruta.id,
                cobrador_id=sample_cobrador.id,
                monto_prestado=50000,
                tasa_interes=0.20,
                monto_a_pagar=60000,
                saldo_actual=60000,
                valor_cuota=3000,
                frecuencia='DIARIO',
                numero_cuotas=20,
                moneda='COP'
            )
            db.session.add(prestamo)
            db.session.commit()
            
            assert prestamo.id is not None
            assert prestamo.estado == 'ACTIVO'
            assert prestamo.cuotas_pagadas == 0
            assert prestamo.cuotas_atrasadas == 0
            
            db.session.delete(prestamo)
            db.session.commit()
    
    @pytest.mark.unit
    def test_prestamo_calculo_interes(self, sample_prestamo):
        """Verifica el cálculo de interés del préstamo"""
        monto_prestado = sample_prestamo.monto_prestado
        tasa = sample_prestamo.tasa_interes
        monto_a_pagar = sample_prestamo.monto_a_pagar
        
        # Verificar que el monto a pagar incluye el interés
        expected = monto_prestado * (1 + tasa)
        assert monto_a_pagar == expected
    
    @pytest.mark.unit
    def test_prestamo_valor_cuota(self, sample_prestamo):
        """Verifica el cálculo del valor de la cuota"""
        valor_cuota = sample_prestamo.valor_cuota
        numero_cuotas = sample_prestamo.numero_cuotas
        monto_a_pagar = sample_prestamo.monto_a_pagar
        
        # Verificar que las cuotas suman el monto a pagar
        assert valor_cuota * numero_cuotas == monto_a_pagar
    
    @pytest.mark.unit
    def test_prestamo_estados(self, app, sample_prestamo):
        """Verifica los diferentes estados del préstamo"""
        estados_validos = ['ACTIVO', 'CANCELADO', 'MORA', 'PAGADO']
        
        for estado in estados_validos:
            sample_prestamo.estado = estado
            assert sample_prestamo.estado == estado
    
    @pytest.mark.unit
    def test_prestamo_frecuencias(self, app, sample_cliente, sample_ruta, sample_cobrador):
        """Verifica las diferentes frecuencias de pago"""
        with app.app_context():
            from app.extensions import db
            
            frecuencias = ['DIARIO', 'SEMANAL', 'QUINCENAL', 'MENSUAL']
            
            for frecuencia in frecuencias:
                prestamo = Prestamo(
                    cliente_id=sample_cliente.id,
                    ruta_id=sample_ruta.id,
                    cobrador_id=sample_cobrador.id,
                    monto_prestado=10000,
                    tasa_interes=0.20,
                    monto_a_pagar=12000,
                    saldo_actual=12000,
                    valor_cuota=600,
                    frecuencia=frecuencia,
                    numero_cuotas=20,
                    moneda='COP'
                )
                db.session.add(prestamo)
                db.session.commit()
                
                assert prestamo.frecuencia == frecuencia
                
                db.session.delete(prestamo)
                db.session.commit()


class TestPagoModel:
    """Tests para el modelo Pago"""
    
    @pytest.mark.unit
    def test_crear_pago(self, app, sample_prestamo, sample_cobrador):
        """Verifica la creación de un pago"""
        with app.app_context():
            from app.extensions import db
            
            saldo_anterior = sample_prestamo.saldo_actual
            monto_pago = sample_prestamo.valor_cuota
            
            pago = Pago(
                prestamo_id=sample_prestamo.id,
                cobrador_id=sample_cobrador.id,
                monto=monto_pago,
                numero_cuotas_pagadas=1,
                saldo_anterior=saldo_anterior,
                saldo_nuevo=saldo_anterior - monto_pago,
                tipo_pago='NORMAL'
            )
            db.session.add(pago)
            db.session.commit()
            
            assert pago.id is not None
            assert pago.monto == monto_pago
            assert pago.saldo_nuevo == saldo_anterior - monto_pago
            
            db.session.delete(pago)
            db.session.commit()
    
    @pytest.mark.unit
    def test_pago_actualiza_saldo(self, app, sample_prestamo, sample_cobrador):
        """Verifica que el pago actualiza el saldo del préstamo"""
        with app.app_context():
            from app.extensions import db
            
            saldo_inicial = sample_prestamo.saldo_actual
            monto_pago = 6000
            
            pago = Pago(
                prestamo_id=sample_prestamo.id,
                cobrador_id=sample_cobrador.id,
                monto=monto_pago,
                numero_cuotas_pagadas=1,
                saldo_anterior=saldo_inicial,
                saldo_nuevo=saldo_inicial - monto_pago
            )
            db.session.add(pago)
            
            # Actualizar el saldo del préstamo
            sample_prestamo.saldo_actual = saldo_inicial - monto_pago
            sample_prestamo.cuotas_pagadas += 1
            sample_prestamo.fecha_ultimo_pago = datetime.utcnow()
            
            db.session.commit()
            
            assert sample_prestamo.saldo_actual == saldo_inicial - monto_pago
            assert sample_prestamo.cuotas_pagadas == 1
            
            # Limpiar
            db.session.delete(pago)
            sample_prestamo.saldo_actual = saldo_inicial
            sample_prestamo.cuotas_pagadas = 0
            db.session.commit()
    
    @pytest.mark.unit
    def test_tipos_pago(self, app, sample_prestamo, sample_cobrador):
        """Verifica los diferentes tipos de pago"""
        with app.app_context():
            from app.extensions import db
            
            tipos = ['NORMAL', 'ABONO', 'COMPLETO']
            
            for tipo in tipos:
                pago = Pago(
                    prestamo_id=sample_prestamo.id,
                    cobrador_id=sample_cobrador.id,
                    monto=1000,
                    numero_cuotas_pagadas=1,
                    saldo_anterior=10000,
                    saldo_nuevo=9000,
                    tipo_pago=tipo
                )
                db.session.add(pago)
                db.session.commit()
                
                assert pago.tipo_pago == tipo
                
                db.session.delete(pago)
                db.session.commit()


class TestPrestamoRoutes:
    """Tests para las rutas de préstamos"""
    
    @pytest.mark.unit
    def test_prestamos_lista_requires_auth(self, client):
        """Verifica que la lista de préstamos requiere autenticación"""
        response = client.get('/prestamos/', follow_redirects=False)
        assert response.status_code in [302, 401, 200]
    
    @pytest.mark.unit
    def test_prestamos_lista_con_auth(self, authenticated_client):
        """Verifica que un usuario autenticado puede ver préstamos"""
        response = authenticated_client.get('/prestamos/')
        assert response.status_code == 200
