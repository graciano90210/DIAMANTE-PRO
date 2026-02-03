"""
Configuración de Logging Estructurado para Diamante Pro
"""
import logging
import json
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Formateador que produce logs en formato JSON estructurado"""
    
    def format(self, record):
        log_record = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        # Agregar campos extra si existen
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_record['ip_address'] = record.ip_address
        if hasattr(record, 'action'):
            log_record['action'] = record.action
        if hasattr(record, 'entity'):
            log_record['entity'] = record.entity
        if hasattr(record, 'entity_id'):
            log_record['entity_id'] = record.entity_id
        if hasattr(record, 'extra_data'):
            log_record['data'] = record.extra_data
            
        return json.dumps(log_record, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Formateador con colores para la consola (desarrollo)"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Verde
        'WARNING': '\033[33m',   # Amarillo
        'ERROR': '\033[31m',     # Rojo
        'CRITICAL': '\033[41m',  # Fondo rojo
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        # Formato legible para desarrollo
        log_format = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        formatter = logging.Formatter(log_format, datefmt='%H:%M:%S')
        return formatter.format(record)


def setup_logging(app):
    """
    Configura el sistema de logging para la aplicación Flask.
    
    En desarrollo: Logs coloridos en consola
    En producción: Logs JSON a archivo + consola
    """
    # Determinar entorno
    is_production = os.environ.get('FLASK_ENV') == 'production'
    log_level = logging.INFO if is_production else logging.DEBUG
    
    # Logger principal de la aplicación
    app_logger = logging.getLogger('diamante')
    app_logger.setLevel(log_level)
    app_logger.handlers = []  # Limpiar handlers existentes
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if is_production:
        # Producción: JSON estructurado
        console_handler.setFormatter(JSONFormatter())
    else:
        # Desarrollo: Colores y formato legible
        console_handler.setFormatter(ColoredConsoleFormatter())
    
    app_logger.addHandler(console_handler)
    
    # En producción, también escribir a archivo
    if is_production:
        logs_dir = Path(app.instance_path) / 'logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            logs_dir / 'diamante.log',
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        app_logger.addHandler(file_handler)
        
        # Archivo separado para errores
        error_handler = RotatingFileHandler(
            logs_dir / 'errors.log',
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        app_logger.addHandler(error_handler)
    
    # Configurar loggers de librerías externas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(
        logging.WARNING if is_production else logging.INFO
    )
    
    return app_logger


def get_logger(name='diamante'):
    """Obtiene un logger con el nombre especificado"""
    return logging.getLogger(name)


# Logger para auditoría de acciones
class AuditLogger:
    """Logger especializado para auditoría de acciones de usuario"""
    
    def __init__(self):
        self.logger = logging.getLogger('diamante.audit')
    
    def log_action(self, action, entity, entity_id=None, user_id=None, 
                   ip_address=None, extra_data=None, level='INFO'):
        """
        Registra una acción de auditoría.
        
        Args:
            action: Tipo de acción (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.)
            entity: Entidad afectada (cliente, prestamo, pago, etc.)
            entity_id: ID de la entidad
            user_id: ID del usuario que realiza la acción
            ip_address: Dirección IP del cliente
            extra_data: Datos adicionales (dict)
            level: Nivel de log (INFO, WARNING, etc.)
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        extra = {
            'action': action,
            'entity': entity,
            'entity_id': entity_id,
            'user_id': user_id,
            'ip_address': ip_address,
            'extra_data': extra_data
        }
        
        message = f"{action} {entity}"
        if entity_id:
            message += f" #{entity_id}"
        
        self.logger.log(log_level, message, extra=extra)
    
    def login_success(self, user_id, username, ip_address):
        """Registra un login exitoso"""
        self.log_action('LOGIN_SUCCESS', 'session', 
                       user_id=user_id, ip_address=ip_address,
                       extra_data={'username': username})
    
    def login_failed(self, username, ip_address, reason='invalid_credentials'):
        """Registra un intento de login fallido"""
        self.log_action('LOGIN_FAILED', 'session',
                       ip_address=ip_address, level='WARNING',
                       extra_data={'username': username, 'reason': reason})
    
    def logout(self, user_id, ip_address):
        """Registra un logout"""
        self.log_action('LOGOUT', 'session', user_id=user_id, ip_address=ip_address)
    
    def create_entity(self, entity, entity_id, user_id, ip_address=None, data=None):
        """Registra la creación de una entidad"""
        self.log_action('CREATE', entity, entity_id, user_id, ip_address, data)
    
    def update_entity(self, entity, entity_id, user_id, ip_address=None, changes=None):
        """Registra la actualización de una entidad"""
        self.log_action('UPDATE', entity, entity_id, user_id, ip_address, changes)
    
    def delete_entity(self, entity, entity_id, user_id, ip_address=None):
        """Registra la eliminación de una entidad"""
        self.log_action('DELETE', entity, entity_id, user_id, ip_address, level='WARNING')
    
    def register_payment(self, prestamo_id, pago_id, monto, user_id, ip_address=None):
        """Registra un pago"""
        self.log_action('PAYMENT', 'pago', pago_id, user_id, ip_address,
                       extra_data={'prestamo_id': prestamo_id, 'monto': monto})


# Instancia global del audit logger
audit = AuditLogger()
