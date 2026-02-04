"""
Sociedad Service - Lógica de negocio de sociedades e inversiones

Contiene operaciones para gestión de sociedades, socios y distribución de ganancias.
"""
from datetime import datetime
from sqlalchemy import func
from ..models import db, Sociedad, Socio, Ruta, AporteCapital, Prestamo


class SociedadService:
    """Servicio para gestión de sociedades y socios"""
    
    @staticmethod
    def crear_sociedad(nombre: str, descripcion: str = None, notas: str = None):
        """
        Crea una nueva sociedad.
        
        Returns:
            tuple (Sociedad, error_message)
        """
        try:
            sociedad = Sociedad(
                nombre=nombre,
                descripcion=descripcion,
                notas=notas,
                activo=True
            )
            
            db.session.add(sociedad)
            db.session.commit()
            
            return sociedad, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def agregar_socio(sociedad_id: int, nombre: str, porcentaje: float,
                      telefono: str = None, email: str = None, 
                      documento: str = None, tipo_socio: str = 'INVERSOR',
                      banco: str = None, cuenta_bancaria: str = None):
        """
        Agrega un nuevo socio a una sociedad.
        
        Returns:
            tuple (Socio, error_message)
        """
        try:
            sociedad = Sociedad.query.get(sociedad_id)
            if not sociedad:
                return None, "Sociedad no encontrada"
            
            # Verificar que el porcentaje total no exceda 100%
            porcentaje_actual = sum(s.porcentaje for s in sociedad.socios.all())
            if porcentaje_actual + porcentaje > 100:
                return None, f"El porcentaje total excedería 100%. Disponible: {100 - porcentaje_actual}%"
            
            socio = Socio(
                sociedad_id=sociedad_id,
                nombre=nombre,
                documento=documento,
                telefono=telefono,
                email=email,
                porcentaje=porcentaje,
                tipo_socio=tipo_socio,
                banco=banco,
                cuenta_bancaria=cuenta_bancaria,
                activo=True,
                fecha_ingreso=datetime.now()
            )
            
            db.session.add(socio)
            db.session.commit()
            
            return socio, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def modificar_participacion(socio_id: int, nuevo_porcentaje: float):
        """
        Modifica el porcentaje de participación de un socio.
        
        Returns:
            tuple (Socio, error_message)
        """
        try:
            socio = Socio.query.get(socio_id)
            if not socio:
                return None, "Socio no encontrado"
            
            sociedad = socio.sociedad
            porcentaje_otros = sum(
                s.porcentaje for s in sociedad.socios.all() 
                if s.id != socio_id
            )
            
            if porcentaje_otros + nuevo_porcentaje > 100:
                return None, f"Porcentaje total excedería 100%. Máximo posible: {100 - porcentaje_otros}%"
            
            socio.porcentaje = nuevo_porcentaje
            db.session.commit()
            
            return socio, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def retirar_socio(socio_id: int, fecha_salida: datetime = None):
        """
        Marca un socio como retirado (no lo elimina para mantener historial).
        
        Returns:
            tuple (Socio, error_message)
        """
        try:
            socio = Socio.query.get(socio_id)
            if not socio:
                return None, "Socio no encontrado"
            
            socio.activo = False
            socio.fecha_salida = fecha_salida or datetime.now()
            
            db.session.commit()
            
            return socio, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def registrar_aporte(sociedad_id: int, socio_nombre: str, monto: float,
                         usuario_id: int, tipo_aporte: str = 'EFECTIVO',
                         descripcion: str = None, moneda: str = 'COP'):
        """
        Registra un aporte de capital de un socio.
        
        Returns:
            tuple (AporteCapital, error_message)
        """
        try:
            sociedad = Sociedad.query.get(sociedad_id)
            if not sociedad:
                return None, "Sociedad no encontrada"
            
            aporte = AporteCapital(
                sociedad_id=sociedad_id,
                nombre_aportante=socio_nombre,
                monto=monto,
                moneda=moneda,
                tipo_aporte=tipo_aporte,
                descripcion=descripcion,
                registrado_por_id=usuario_id,
                fecha_aporte=datetime.now()
            )
            
            # Si hay un socio con ese nombre, actualizar su monto_aportado
            socio = Socio.query.filter_by(
                sociedad_id=sociedad_id,
                nombre=socio_nombre,
                activo=True
            ).first()
            
            if socio:
                socio.monto_aportado = (socio.monto_aportado or 0) + monto
            
            db.session.add(aporte)
            db.session.commit()
            
            return aporte, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def calcular_distribucion_ganancias(sociedad_id: int):
        """
        Calcula cómo se distribuirían las ganancias actuales entre los socios.
        
        Returns:
            dict con distribución por socio
        """
        sociedad = Sociedad.query.get(sociedad_id)
        if not sociedad:
            return None, "Sociedad no encontrada"
        
        # Obtener rutas de esta sociedad
        rutas = Ruta.query.filter_by(sociedad_id=sociedad_id, activo=True).all()
        ruta_ids = [r.id for r in rutas]
        
        if not ruta_ids:
            return {
                'ganancia_total': 0,
                'distribucion': [],
                'mensaje': 'No hay rutas asociadas a esta sociedad'
            }, None
        
        # Calcular ganancias (intereses cobrados)
        ganancias = db.session.query(
            func.sum(Prestamo.monto_a_pagar - Prestamo.monto_prestado)
        ).filter(
            Prestamo.ruta_id.in_(ruta_ids),
            Prestamo.estado == 'PAGADO'
        ).scalar() or 0
        
        # Distribuir entre socios
        distribucion = []
        
        # Primero los socios
        for socio in sociedad.socios.filter_by(activo=True).all():
            monto_socio = ganancias * (socio.porcentaje / 100)
            distribucion.append({
                'nombre': socio.nombre,
                'porcentaje': socio.porcentaje,
                'monto': round(monto_socio, 2),
                'tipo': socio.tipo_socio,
                'cuenta': socio.cuenta_bancaria
            })
        
        # El dueño se queda con el resto
        porcentaje_dueno = sociedad.porcentaje_dueno
        monto_dueno = ganancias * (porcentaje_dueno / 100)
        distribucion.append({
            'nombre': 'DUEÑO (Tú)',
            'porcentaje': porcentaje_dueno,
            'monto': round(monto_dueno, 2),
            'tipo': 'DUEÑO',
            'cuenta': None
        })
        
        return {
            'ganancia_total': round(ganancias, 2),
            'distribucion': distribucion
        }, None
    
    @staticmethod
    def get_resumen_sociedad(sociedad_id: int):
        """Obtiene resumen completo de una sociedad"""
        sociedad = Sociedad.query.get(sociedad_id)
        if not sociedad:
            return None
        
        rutas = Ruta.query.filter_by(sociedad_id=sociedad_id).all()
        ruta_ids = [r.id for r in rutas]
        
        # Capital total aportado
        capital = db.session.query(
            func.sum(AporteCapital.monto)
        ).filter_by(sociedad_id=sociedad_id).scalar() or 0
        
        # Cartera activa
        cartera = 0
        prestamos_activos = 0
        if ruta_ids:
            result = db.session.query(
                func.sum(Prestamo.saldo_actual),
                func.count(Prestamo.id)
            ).filter(
                Prestamo.ruta_id.in_(ruta_ids),
                Prestamo.estado == 'ACTIVO'
            ).first()
            cartera = result[0] or 0
            prestamos_activos = result[1] or 0
        
        return {
            'sociedad': sociedad,
            'socios': sociedad.lista_socios,
            'num_socios': sociedad.numero_socios,
            'porcentaje_dueno': sociedad.porcentaje_dueno,
            'num_rutas': len(rutas),
            'rutas': rutas,
            'capital_aportado': float(capital),
            'cartera_activa': float(cartera),
            'prestamos_activos': prestamos_activos
        }
