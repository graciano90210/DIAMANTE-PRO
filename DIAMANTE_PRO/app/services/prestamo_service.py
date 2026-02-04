"""
Préstamo Service - Lógica de negocio de préstamos

Contiene operaciones CRUD y cálculos financieros de préstamos.
"""
from datetime import datetime, timedelta
from sqlalchemy import func
from ..models import db, Prestamo, Pago, Cliente, Ruta


class PrestamoService:
    """Servicio para gestión de préstamos"""
    
    @staticmethod
    def calcular_prestamo(monto: float, tasa_interes: float, num_cuotas: int):
        """
        Calcula los valores de un nuevo préstamo.
        
        Args:
            monto: Monto a prestar
            tasa_interes: Tasa de interés (ej: 0.20 para 20%)
            num_cuotas: Número de cuotas
            
        Returns:
            dict con monto_a_pagar, valor_cuota, ganancia
        """
        monto_a_pagar = monto * (1 + tasa_interes)
        valor_cuota = monto_a_pagar / num_cuotas
        ganancia = monto_a_pagar - monto
        
        return {
            'monto_prestado': monto,
            'monto_a_pagar': round(monto_a_pagar, 2),
            'valor_cuota': round(valor_cuota, 2),
            'ganancia': round(ganancia, 2),
            'tasa_interes': tasa_interes
        }
    
    @staticmethod
    def crear_prestamo(cliente_id: int, ruta_id: int, cobrador_id: int,
                       monto: float, tasa_interes: float, num_cuotas: int,
                       frecuencia: str = 'DIARIO'):
        """
        Crea un nuevo préstamo.
        
        Returns:
            tuple (Prestamo, error_message)
        """
        try:
            cliente = Cliente.query.get(cliente_id)
            if not cliente:
                return None, "Cliente no encontrado"
            
            if cliente.credito_bloqueado:
                return None, "El cliente tiene el crédito bloqueado"
            
            ruta = Ruta.query.get(ruta_id)
            if not ruta:
                return None, "Ruta no encontrada"
            
            # Calcular valores
            calculos = PrestamoService.calcular_prestamo(monto, tasa_interes, num_cuotas)
            
            prestamo = Prestamo(
                cliente_id=cliente_id,
                ruta_id=ruta_id,
                cobrador_id=cobrador_id,
                monto_prestado=monto,
                tasa_interes=tasa_interes,
                monto_a_pagar=calculos['monto_a_pagar'],
                saldo_actual=calculos['monto_a_pagar'],
                valor_cuota=calculos['valor_cuota'],
                moneda=ruta.moneda,
                frecuencia=frecuencia,
                numero_cuotas=num_cuotas,
                estado='ACTIVO',
                fecha_inicio=datetime.now()
            )
            
            db.session.add(prestamo)
            db.session.commit()
            
            return prestamo, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def registrar_pago(prestamo_id: int, monto: float, cobrador_id: int,
                       observaciones: str = None):
        """
        Registra un pago en un préstamo.
        
        Returns:
            tuple (Pago, error_message)
        """
        try:
            prestamo = Prestamo.query.get(prestamo_id)
            if not prestamo:
                return None, "Préstamo no encontrado"
            
            if prestamo.estado != 'ACTIVO':
                return None, f"El préstamo está {prestamo.estado}"
            
            saldo_anterior = prestamo.saldo_actual
            saldo_nuevo = max(0, saldo_anterior - monto)
            
            # Calcular cuántas cuotas cubre este pago
            cuotas_pagadas = int(monto / prestamo.valor_cuota) if prestamo.valor_cuota > 0 else 1
            
            # Determinar tipo de pago
            if saldo_nuevo == 0:
                tipo_pago = 'COMPLETO'
                prestamo.estado = 'PAGADO'
            elif monto >= prestamo.valor_cuota:
                tipo_pago = 'NORMAL'
            else:
                tipo_pago = 'ABONO'
            
            pago = Pago(
                prestamo_id=prestamo_id,
                cobrador_id=cobrador_id,
                monto=monto,
                numero_cuotas_pagadas=cuotas_pagadas,
                saldo_anterior=saldo_anterior,
                saldo_nuevo=saldo_nuevo,
                tipo_pago=tipo_pago,
                observaciones=observaciones,
                fecha_pago=datetime.now()
            )
            
            # Actualizar préstamo
            prestamo.saldo_actual = saldo_nuevo
            prestamo.cuotas_pagadas += cuotas_pagadas
            prestamo.fecha_ultimo_pago = datetime.now()
            
            db.session.add(pago)
            db.session.commit()
            
            return pago, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_prestamos_por_cobrar_hoy(cobrador_id: int = None, ruta_id: int = None):
        """
        Obtiene préstamos que deben cobrarse hoy según su frecuencia.
        """
        hoy = datetime.now()
        dia_semana = hoy.weekday()
        
        query = Prestamo.query.filter(Prestamo.estado == 'ACTIVO')
        
        if cobrador_id:
            query = query.filter(Prestamo.cobrador_id == cobrador_id)
        if ruta_id:
            query = query.filter(Prestamo.ruta_id == ruta_id)
        
        # Filtrar por frecuencia
        if dia_semana == 6:  # Domingo
            query = query.filter(Prestamo.frecuencia == 'BISEMANAL')
        elif dia_semana < 5:  # Lunes a Viernes
            query = query.filter(
                Prestamo.frecuencia.in_(['DIARIO', 'DIARIO_LUNES_VIERNES', 'BISEMANAL'])
            )
        else:  # Sábado
            query = query.filter(
                Prestamo.frecuencia.in_(['DIARIO', 'BISEMANAL'])
            )
        
        return query.all()
    
    @staticmethod
    def get_prestamos_atrasados(dias_minimo: int = 1):
        """Obtiene préstamos con cuotas atrasadas"""
        return Prestamo.query.filter(
            Prestamo.estado == 'ACTIVO',
            Prestamo.cuotas_atrasadas >= dias_minimo
        ).all()
    
    @staticmethod
    def actualizar_atrasos():
        """
        Actualiza el conteo de cuotas atrasadas de todos los préstamos activos.
        Debería ejecutarse diariamente.
        """
        hoy = datetime.now().date()
        prestamos = Prestamo.query.filter_by(estado='ACTIVO').all()
        actualizados = 0
        
        for prestamo in prestamos:
            if prestamo.fecha_ultimo_pago:
                dias_sin_pago = (hoy - prestamo.fecha_ultimo_pago.date()).days
            else:
                dias_sin_pago = (hoy - prestamo.fecha_inicio.date()).days
            
            # Calcular atrasos según frecuencia
            if prestamo.frecuencia == 'DIARIO':
                cuotas_esperadas = dias_sin_pago
            elif prestamo.frecuencia == 'SEMANAL':
                cuotas_esperadas = dias_sin_pago // 7
            elif prestamo.frecuencia == 'QUINCENAL':
                cuotas_esperadas = dias_sin_pago // 15
            else:
                cuotas_esperadas = dias_sin_pago
            
            atraso = max(0, cuotas_esperadas - prestamo.cuotas_pagadas)
            
            if prestamo.cuotas_atrasadas != atraso:
                prestamo.cuotas_atrasadas = atraso
                actualizados += 1
        
        db.session.commit()
        return actualizados
