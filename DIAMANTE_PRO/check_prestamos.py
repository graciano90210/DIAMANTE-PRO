#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificar préstamos en la base de datos
"""
from app import create_app
from app.models import Prestamo, Ruta, Cliente

app = create_app()
with app.app_context():
    # Verificar cuántos préstamos hay en total
    total_prestamos = Prestamo.query.count()
    print(f'Total de prestamos en BD: {total_prestamos}')

    # Ver préstamos activos
    activos = Prestamo.query.filter_by(estado='ACTIVO').all()
    print(f'Prestamos ACTIVOS: {len(activos)}')

    # Ver todos los préstamos
    todos = Prestamo.query.all()
    print(f'Todos los prestamos: {len(todos)}')

    if todos:
        print('\nDetalle de prestamos:')
        for p in todos:
            cliente = Cliente.query.get(p.cliente_id)
            ruta = Ruta.query.get(p.ruta_id) if p.ruta_id else None
            print(f'  - ID {p.id}: Cliente "{cliente.nombre if cliente else "N/A"}", Monto ${p.monto_prestado:,.0f}, Estado: {p.estado}, Ruta: "{ruta.nombre if ruta else "Sin ruta"}"')
    else:
        print('\nNo hay prestamos en la base de datos')
