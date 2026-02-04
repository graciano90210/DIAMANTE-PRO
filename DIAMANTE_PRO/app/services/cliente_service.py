"""
Cliente Service - Lógica de negocio de clientes

Contiene operaciones CRUD y scoring crediticio.
"""
from datetime import datetime
from sqlalchemy import func
from ..models import db, Cliente, Prestamo, Pago


class ClienteService:
    """Servicio para gestión de clientes y scoring crediticio"""
    
    @staticmethod
    def crear_cliente(data: dict):
        """
        Crea un nuevo cliente.
        
        Args:
            data: Diccionario con datos del cliente
            
        Returns:
            tuple (Cliente, error_message)
        """
        try:
            # Verificar documento único
            if Cliente.query.filter_by(documento=data['documento']).first():
                return None, "Ya existe un cliente con este documento"
            
            cliente = Cliente(
                nombre=data['nombre'],
                documento=data['documento'],
                tipo_documento=data.get('tipo_documento', 'CPF'),
                telefono=data['telefono'],
                email=data.get('email'),
                whatsapp_numero=data.get('whatsapp', data['telefono']),
                direccion_negocio=data.get('direccion_negocio'),
                direccion_casa=data.get('direccion_casa'),
                gps_latitud=data.get('gps_latitud'),
                gps_longitud=data.get('gps_longitud'),
                tipo_negocio=data.get('tipo_negocio'),
                nombre_negocio=data.get('nombre_negocio'),
                antiguedad_negocio_meses=data.get('antiguedad_negocio_meses'),
                ingresos_diarios_estimados=data.get('ingresos_diarios_estimados'),
                score_crediticio=500,  # Score inicial
                nivel_riesgo='NUEVO'
            )
            
            db.session.add(cliente)
            db.session.commit()
            
            return cliente, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def calcular_score(cliente_id: int):
        """
        Calcula el score crediticio de un cliente basado en su historial.
        
        Factores:
        - Antigüedad del negocio (0-100 pts)
        - Historial de pagos (0-300 pts)
        - Tasa de pago a tiempo (0-250 pts)
        - Comprobante de residencia (0-100 pts)
        - Local propio (0-50 pts)
        - Referencias (0-100 pts)
        - Formalización fiscal (0-100 pts)
        
        Total máximo: 1000 puntos
        """
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return None, "Cliente no encontrado"
        
        score = 0
        factores = {}
        
        # 1. Antigüedad del negocio (máx 100 pts)
        if cliente.antiguedad_negocio_meses:
            if cliente.antiguedad_negocio_meses >= 24:
                pts = 100
            elif cliente.antiguedad_negocio_meses >= 12:
                pts = 70
            elif cliente.antiguedad_negocio_meses >= 6:
                pts = 40
            else:
                pts = 20
            score += pts
            factores['antiguedad_negocio'] = pts
        
        # 2. Historial de pagos - préstamos completados (máx 300 pts)
        prestamos_pagados = Prestamo.query.filter_by(
            cliente_id=cliente_id, 
            estado='PAGADO'
        ).count()
        pts_historial = min(300, prestamos_pagados * 50)
        score += pts_historial
        factores['prestamos_completados'] = pts_historial
        
        # 3. Tasa de pago a tiempo (máx 250 pts)
        total_pagos = Pago.query.join(Prestamo).filter(
            Prestamo.cliente_id == cliente_id
        ).count()
        
        if total_pagos > 0:
            # Simplificado: asumimos que pagos de tipo NORMAL son a tiempo
            pagos_tiempo = Pago.query.join(Prestamo).filter(
                Prestamo.cliente_id == cliente_id,
                Pago.tipo_pago == 'NORMAL'
            ).count()
            tasa = pagos_tiempo / total_pagos
            pts_tasa = int(tasa * 250)
            score += pts_tasa
            factores['tasa_pago'] = pts_tasa
        
        # 4. Comprobante de residencia (máx 100 pts)
        if cliente.tiene_comprobante_residencia:
            pts = 100 if cliente.comprobante_a_nombre_propio else 50
            score += pts
            factores['comprobante_residencia'] = pts
        
        # 5. Local propio (máx 50 pts)
        if cliente.local_propio:
            score += 50
            factores['local_propio'] = 50
        
        # 6. Formalización fiscal (máx 100 pts)
        if cliente.negocio_formalizado and cliente.documento_fiscal_negocio:
            score += 100
            factores['formalizacion'] = 100
        
        # Determinar nivel de riesgo
        if score >= 800:
            nivel_riesgo = 'EXCELENTE'
        elif score >= 600:
            nivel_riesgo = 'BUENO'
        elif score >= 400:
            nivel_riesgo = 'REGULAR'
        elif score >= 200:
            nivel_riesgo = 'ALTO'
        else:
            nivel_riesgo = 'CRITICO'
        
        # Calcular límite sugerido (basado en ingresos y score)
        if cliente.ingresos_diarios_estimados:
            # Límite = ingresos mensuales * factor según score
            ingresos_mensuales = cliente.ingresos_diarios_estimados * 26
            factor = score / 500  # 1.0 para score 500, 2.0 para 1000
            limite_sugerido = ingresos_mensuales * factor
        else:
            limite_sugerido = score * 5  # Default: score * 5
        
        # Actualizar cliente
        score_anterior = cliente.score_crediticio
        cliente.score_crediticio = score
        cliente.nivel_riesgo = nivel_riesgo
        cliente.limite_credito_sugerido = limite_sugerido
        cliente.fecha_ultimo_calculo_score = datetime.now()
        
        db.session.commit()
        
        return {
            'score_anterior': score_anterior,
            'score_nuevo': score,
            'nivel_riesgo': nivel_riesgo,
            'limite_sugerido': limite_sugerido,
            'factores': factores
        }, None
    
    @staticmethod
    def get_clientes_por_riesgo(nivel_riesgo: str = None):
        """Obtiene clientes filtrados por nivel de riesgo"""
        query = Cliente.query
        
        if nivel_riesgo:
            query = query.filter_by(nivel_riesgo=nivel_riesgo)
        
        return query.order_by(Cliente.score_crediticio.desc()).all()
    
    @staticmethod
    def buscar_clientes(termino: str, limit: int = 20):
        """Busca clientes por nombre o documento"""
        return Cliente.query.filter(
            (Cliente.nombre.ilike(f'%{termino}%')) |
            (Cliente.documento.ilike(f'%{termino}%'))
        ).limit(limit).all()
    
    @staticmethod
    def get_estadisticas_cliente(cliente_id: int):
        """Obtiene estadísticas detalladas de un cliente"""
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return None
        
        prestamos = Prestamo.query.filter_by(cliente_id=cliente_id).all()
        
        total_prestado = sum(p.monto_prestado for p in prestamos)
        total_pagado = sum(
            sum(pago.monto for pago in p.pagos.all()) 
            for p in prestamos
        )
        
        return {
            'cliente': cliente,
            'total_prestamos': len(prestamos),
            'prestamos_activos': sum(1 for p in prestamos if p.estado == 'ACTIVO'),
            'prestamos_pagados': sum(1 for p in prestamos if p.estado == 'PAGADO'),
            'total_prestado': total_prestado,
            'total_pagado': total_pagado,
            'saldo_actual': sum(p.saldo_actual for p in prestamos if p.estado == 'ACTIVO')
        }
