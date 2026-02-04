"""
Oficina Service - Lógica de negocio para gestión de oficinas

Permite agrupar rutas en oficinas/zonas para mejor organización.
"""
from datetime import datetime
from sqlalchemy import func
from ..models import db, Oficina, Ruta, Prestamo, Pago, Usuario


class OficinaService:
    """Servicio para gestión de oficinas"""
    
    @staticmethod
    def crear_oficina(datos: dict):
        """
        Crea una nueva oficina.
        
        Args:
            datos: dict con nombre, codigo, descripcion, direccion, ciudad, 
                   estado, pais, responsable_id, sociedad_id, etc.
        
        Returns:
            dict con oficina creada o error
        """
        try:
            oficina = Oficina(
                nombre=datos.get('nombre'),
                codigo=datos.get('codigo'),
                descripcion=datos.get('descripcion'),
                direccion=datos.get('direccion'),
                ciudad=datos.get('ciudad'),
                estado=datos.get('estado'),
                pais=datos.get('pais', 'Colombia'),
                responsable_id=datos.get('responsable_id'),
                telefono_oficina=datos.get('telefono_oficina'),
                email_oficina=datos.get('email_oficina'),
                sociedad_id=datos.get('sociedad_id'),
                meta_cobro_diario=datos.get('meta_cobro_diario', 0),
                meta_prestamos_mes=datos.get('meta_prestamos_mes', 0),
                notas=datos.get('notas'),
                activo=True
            )
            
            db.session.add(oficina)
            db.session.commit()
            
            return {'oficina': oficina, 'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    @staticmethod
    def get_oficina(oficina_id: int):
        """Obtiene una oficina por ID con estadísticas"""
        oficina = Oficina.query.get(oficina_id)
        if not oficina:
            return {'error': 'Oficina no encontrada'}
        
        return {
            'oficina': oficina,
            'estadisticas': OficinaService.get_estadisticas_oficina(oficina_id)
        }
    
    @staticmethod
    def listar_oficinas(sociedad_id: int = None, solo_activas: bool = True):
        """
        Lista oficinas con sus estadísticas.
        
        Args:
            sociedad_id: Filtrar por sociedad específica
            solo_activas: Solo oficinas activas
        """
        query = Oficina.query
        
        if sociedad_id:
            query = query.filter_by(sociedad_id=sociedad_id)
        
        if solo_activas:
            query = query.filter_by(activo=True)
        
        oficinas = query.order_by(Oficina.nombre).all()
        
        resultado = []
        for oficina in oficinas:
            stats = OficinaService.get_estadisticas_oficina(oficina.id)
            resultado.append({
                'oficina': oficina,
                'num_rutas': stats['num_rutas'],
                'cartera_total': stats['cartera_total'],
                'cobrado_hoy': stats['cobrado_hoy']
            })
        
        return resultado
    
    @staticmethod
    def get_estadisticas_oficina(oficina_id: int):
        """Calcula estadísticas completas de una oficina"""
        # Rutas de la oficina
        rutas = Ruta.query.filter_by(oficina_id=oficina_id, activo=True).all()
        ruta_ids = [r.id for r in rutas]
        
        if not ruta_ids:
            return {
                'num_rutas': 0,
                'num_cobradores': 0,
                'prestamos_activos': 0,
                'cartera_total': 0,
                'capital_prestado': 0,
                'cobrado_hoy': 0,
                'por_cobrar_hoy': 0
            }
        
        # Conteos
        num_cobradores = db.session.query(func.count(func.distinct(Ruta.cobrador_id))).filter(
            Ruta.id.in_(ruta_ids),
            Ruta.cobrador_id.isnot(None)
        ).scalar() or 0
        
        # Préstamos activos
        prestamos_stats = db.session.query(
            func.count(Prestamo.id).label('cantidad'),
            func.sum(Prestamo.saldo_actual).label('cartera'),
            func.sum(Prestamo.monto_prestado).label('capital'),
            func.sum(Prestamo.valor_cuota).label('por_cobrar')
        ).filter(
            Prestamo.ruta_id.in_(ruta_ids),
            Prestamo.estado == 'ACTIVO'
        ).first()
        
        # Cobrado hoy
        hoy = datetime.now().date()
        cobrado_hoy = db.session.query(func.sum(Pago.monto)).join(Prestamo).filter(
            Prestamo.ruta_id.in_(ruta_ids),
            func.date(Pago.fecha_pago) == hoy
        ).scalar() or 0
        
        return {
            'num_rutas': len(rutas),
            'num_cobradores': num_cobradores,
            'prestamos_activos': prestamos_stats.cantidad or 0,
            'cartera_total': float(prestamos_stats.cartera or 0),
            'capital_prestado': float(prestamos_stats.capital or 0),
            'por_cobrar_hoy': float(prestamos_stats.por_cobrar or 0),
            'cobrado_hoy': float(cobrado_hoy)
        }
    
    @staticmethod
    def asignar_rutas(oficina_id: int, ruta_ids: list):
        """
        Asigna múltiples rutas a una oficina.
        
        Args:
            oficina_id: ID de la oficina destino
            ruta_ids: Lista de IDs de rutas a asignar
        """
        oficina = Oficina.query.get(oficina_id)
        if not oficina:
            return {'error': 'Oficina no encontrada'}
        
        try:
            rutas_asignadas = 0
            for ruta_id in ruta_ids:
                ruta = Ruta.query.get(ruta_id)
                if ruta:
                    ruta.oficina_id = oficina_id
                    rutas_asignadas += 1
            
            db.session.commit()
            
            return {
                'success': True,
                'rutas_asignadas': rutas_asignadas,
                'mensaje': f'{rutas_asignadas} rutas asignadas a {oficina.nombre}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    @staticmethod
    def quitar_ruta(ruta_id: int):
        """Quita una ruta de su oficina (la deja sin oficina)"""
        ruta = Ruta.query.get(ruta_id)
        if not ruta:
            return {'error': 'Ruta no encontrada'}
        
        try:
            oficina_anterior = ruta.oficina_id
            ruta.oficina_id = None
            db.session.commit()
            
            return {
                'success': True,
                'mensaje': f'Ruta {ruta.nombre} removida de oficina'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    @staticmethod
    def mover_rutas_entre_oficinas(origen_id: int, destino_id: int, ruta_ids: list = None):
        """
        Mueve rutas de una oficina a otra.
        
        Args:
            origen_id: ID de oficina origen
            destino_id: ID de oficina destino
            ruta_ids: Lista específica de rutas (si None, mueve todas)
        """
        oficina_destino = Oficina.query.get(destino_id)
        if not oficina_destino:
            return {'error': 'Oficina destino no encontrada'}
        
        try:
            if ruta_ids:
                rutas = Ruta.query.filter(
                    Ruta.id.in_(ruta_ids),
                    Ruta.oficina_id == origen_id
                ).all()
            else:
                rutas = Ruta.query.filter_by(oficina_id=origen_id).all()
            
            movidas = 0
            for ruta in rutas:
                ruta.oficina_id = destino_id
                movidas += 1
            
            db.session.commit()
            
            return {
                'success': True,
                'rutas_movidas': movidas,
                'mensaje': f'{movidas} rutas movidas a {oficina_destino.nombre}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    @staticmethod
    def get_rutas_sin_oficina(sociedad_id: int = None):
        """Obtiene rutas que no están asignadas a ninguna oficina"""
        query = Ruta.query.filter(
            Ruta.oficina_id.is_(None),
            Ruta.activo == True
        )
        
        if sociedad_id:
            query = query.filter_by(sociedad_id=sociedad_id)
        
        return query.order_by(Ruta.nombre).all()
    
    @staticmethod
    def get_resumen_por_oficinas(sociedad_id: int = None):
        """
        Genera resumen de todas las oficinas con métricas.
        Útil para vista de dashboard de inversionista.
        """
        oficinas = OficinaService.listar_oficinas(sociedad_id=sociedad_id)
        rutas_sin_oficina = OficinaService.get_rutas_sin_oficina(sociedad_id)
        
        total_cartera = sum(o['cartera_total'] for o in oficinas)
        total_rutas = sum(o['num_rutas'] for o in oficinas) + len(rutas_sin_oficina)
        
        return {
            'oficinas': oficinas,
            'rutas_sin_oficina': rutas_sin_oficina,
            'totales': {
                'num_oficinas': len(oficinas),
                'total_rutas': total_rutas,
                'total_cartera': total_cartera,
                'rutas_sin_asignar': len(rutas_sin_oficina)
            }
        }
    
    @staticmethod
    def actualizar_oficina(oficina_id: int, datos: dict):
        """Actualiza datos de una oficina"""
        oficina = Oficina.query.get(oficina_id)
        if not oficina:
            return {'error': 'Oficina no encontrada'}
        
        try:
            if 'nombre' in datos:
                oficina.nombre = datos['nombre']
            if 'codigo' in datos:
                oficina.codigo = datos['codigo']
            if 'descripcion' in datos:
                oficina.descripcion = datos['descripcion']
            if 'direccion' in datos:
                oficina.direccion = datos['direccion']
            if 'ciudad' in datos:
                oficina.ciudad = datos['ciudad']
            if 'estado' in datos:
                oficina.estado = datos['estado']
            if 'responsable_id' in datos:
                oficina.responsable_id = datos['responsable_id']
            if 'telefono_oficina' in datos:
                oficina.telefono_oficina = datos['telefono_oficina']
            if 'email_oficina' in datos:
                oficina.email_oficina = datos['email_oficina']
            if 'meta_cobro_diario' in datos:
                oficina.meta_cobro_diario = datos['meta_cobro_diario']
            if 'meta_prestamos_mes' in datos:
                oficina.meta_prestamos_mes = datos['meta_prestamos_mes']
            if 'notas' in datos:
                oficina.notas = datos['notas']
            if 'activo' in datos:
                oficina.activo = datos['activo']
            
            db.session.commit()
            
            return {'oficina': oficina, 'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    @staticmethod
    def eliminar_oficina(oficina_id: int, reasignar_a: int = None):
        """
        Elimina (desactiva) una oficina.
        Las rutas pueden reasignarse a otra oficina o quedar sin oficina.
        
        Args:
            oficina_id: ID de la oficina a eliminar
            reasignar_a: ID de oficina destino para las rutas (opcional)
        """
        oficina = Oficina.query.get(oficina_id)
        if not oficina:
            return {'error': 'Oficina no encontrada'}
        
        try:
            # Reasignar rutas
            rutas = Ruta.query.filter_by(oficina_id=oficina_id).all()
            for ruta in rutas:
                ruta.oficina_id = reasignar_a  # None o ID de otra oficina
            
            # Desactivar oficina
            oficina.activo = False
            
            db.session.commit()
            
            return {
                'success': True,
                'mensaje': f'Oficina {oficina.nombre} eliminada. {len(rutas)} rutas reasignadas.'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
