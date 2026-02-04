"""
Script de migración para convertir socios legacy a la nueva tabla Socio.
Ejecutar una sola vez después de actualizar los modelos.

Uso: python -m migrations.migrate_socios
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Sociedad, Socio


def migrate_socios():
    """Migra los socios de los campos legacy a la nueva tabla Socio"""
    
    app = create_app()
    
    with app.app_context():
        # Crear la tabla si no existe
        db.create_all()
        
        sociedades = Sociedad.query.all()
        migrados = 0
        omitidos = 0
        
        print("=" * 50)
        print("🔄 Migrando socios a nueva estructura...")
        print("=" * 50)
        
        for sociedad in sociedades:
            # Verificar si ya tiene socios en la nueva tabla
            if sociedad.socios.count() > 0:
                print(f"⏭️  Sociedad '{sociedad.nombre}' ya tiene socios migrados, omitiendo...")
                omitidos += 1
                continue
            
            socios_a_crear = []
            
            # Socio 1 (legacy)
            if sociedad.nombre_socio:
                socios_a_crear.append(Socio(
                    sociedad_id=sociedad.id,
                    nombre=sociedad.nombre_socio,
                    telefono=sociedad.telefono_socio,
                    porcentaje=sociedad.porcentaje_socio or 0,
                    tipo_socio='INVERSOR',
                    activo=True
                ))
            
            # Socio 2 (legacy)
            if sociedad.nombre_socio_2:
                socios_a_crear.append(Socio(
                    sociedad_id=sociedad.id,
                    nombre=sociedad.nombre_socio_2,
                    telefono=sociedad.telefono_socio_2,
                    porcentaje=sociedad.porcentaje_socio_2 or 0,
                    tipo_socio='INVERSOR',
                    activo=True
                ))
            
            # Socio 3 (legacy)
            if sociedad.nombre_socio_3:
                socios_a_crear.append(Socio(
                    sociedad_id=sociedad.id,
                    nombre=sociedad.nombre_socio_3,
                    telefono=sociedad.telefono_socio_3,
                    porcentaje=sociedad.porcentaje_socio_3 or 0,
                    tipo_socio='INVERSOR',
                    activo=True
                ))
            
            if socios_a_crear:
                for socio in socios_a_crear:
                    db.session.add(socio)
                print(f"✅ Sociedad '{sociedad.nombre}': {len(socios_a_crear)} socio(s) migrado(s)")
                migrados += len(socios_a_crear)
        
        db.session.commit()
        
        print("=" * 50)
        print(f"📊 Resumen: {migrados} socios migrados, {omitidos} sociedades omitidas")
        print("=" * 50)
        
        return migrados, omitidos


if __name__ == '__main__':
    migrate_socios()
