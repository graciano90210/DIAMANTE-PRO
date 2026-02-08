"""
Script de Migración - Corregir Saldos Negativos en Cobradores
Fecha: 2026-02-08

Este script ajusta los saldos históricos para reflejar correctamente
los aportes de capital en las cajas del dueño.

PROBLEMA:
- Los aportes de capital se registraron como Transacciones(INGRESO)
- Pero NO se reflejaron en CajaDueno
- Los préstamos restaron de saldos que no existían → Saldos negativos

SOLUCIÓN:
1. Sumar todos los AportesCapital por moneda
2. Actualizar CajaDueno con esos montos
3. Recalcular saldos de cobradores
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import AporteCapital, CajaDueno, Usuario, Ruta
from sqlalchemy import func

def main():
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("SCRIPT DE MIGRACIÓN: Corrección de Saldos Negativos")
        print("=" * 60)
        print()
        
        # 1. Obtener todos los usuarios dueños
        duenos = Usuario.query.filter_by(rol='dueno').all()
        
        if not duenos:
            print("❌ No se encontraron usuarios con rol 'dueno'")
            return
        
        print(f"✅ Encontrados {len(duenos)} usuario(s) dueño(s)")
        print()
        
        for dueno in duenos:
            print(f"📊 Procesando usuario: {dueno.nombre} (ID: {dueno.id})")
            print("-" * 60)
            
            # 2. Obtener aportes de capital por moneda
            aportes_por_moneda = db.session.query(
                AporteCapital.moneda,
                func.sum(AporteCapital.monto).label('total')
            ).group_by(AporteCapital.moneda).all()
            
            if not aportes_por_moneda:
                print("⚠️  No se encontraron aportes de capital")
                continue
            
            print(f"\n💰 Aportes de Capital Registrados:")
            for moneda, total in aportes_por_moneda:
                print(f"   {moneda}: {total:,.2f}")
            
            # 3. Actualizar o crear CajaDueno por cada moneda
            print(f"\n🔧 Actualizando Cajas del Dueño...")
            
            for moneda, total_aportado in aportes_por_moneda:
                caja = CajaDueno.query.filter_by(
                    usuario_id=dueno.id,
                    moneda=moneda
                ).first()
                
                if caja:
                    saldo_anterior = caja.saldo
                    caja.saldo = total_aportado
                    print(f"   ✓ {moneda}: {saldo_anterior:,.2f} → {total_aportado:,.2f}")
                else:
                    caja = CajaDueno(
                        usuario_id=dueno.id,
                        saldo=total_aportado,
                        moneda=moneda
                    )
                    db.session.add(caja)
                    print(f"   ✓ {moneda}: CREADA con saldo {total_aportado:,.2f}")
            
            print()
        
        # 4. Commit de cambios
        try:
            db.session.commit()
            print("=" * 60)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            print()
            print("📋 Resumen:")
            print("   - Aportes de capital reflejados en CajaDueno")
            print("   - Los saldos de cobradores se calcularán dinámicamente")
            print("   - Reinicia el servidor para ver los cambios")
            print()
            
        except Exception as e:
            db.session.rollback()
            print("=" * 60)
            print("❌ ERROR EN LA MIGRACIÓN")
            print("=" * 60)
            print(f"Error: {str(e)}")
            print()
            return
        
        # 5. Mostrar estado final de cajas
        print("📊 Estado Final de Cajas del Dueño:")
        print("-" * 60)
        
        cajas_finales = CajaDueno.query.all()
        for caja in cajas_finales:
            usuario = Usuario.query.get(caja.usuario_id)
            print(f"   {usuario.nombre} - {caja.moneda}: {caja.saldo:,.2f}")
        
        print()
        print("=" * 60)
        print("🎉 Proceso completado. Verifica los saldos en la aplicación.")
        print("=" * 60)


if __name__ == '__main__':
    main()
