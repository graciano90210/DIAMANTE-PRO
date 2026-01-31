from app import create_app, db
from app.models import Usuario, Sociedad, Ruta, Cliente, Prestamo, Pago, AporteCapital, Transaccion
from datetime import datetime, timedelta

# Inicializamos la app para tener acceso a la base de datos
app = create_app()

def prueba_maestra():
    with app.app_context():
        print("\n🧪 --- INICIANDO PRUEBA MAESTRA DE DIAMANTE PRO --- 🧪\n")

        # ---------------------------------------------------------
        # 1. LIMPIEZA (Opcional: para empezar de cero en la prueba)
        # ---------------------------------------------------------
        # db.drop_all()
        # db.create_all()
        # print("🧹 Base de datos limpiada y recreada.")

        # ---------------------------------------------------------
        # 2. CREANDO LA ESTRUCTURA (Dueño, Sociedad, Ruta)
        # ---------------------------------------------------------
        try:
            # Crear Usuario Dueño
            dueno = Usuario.query.filter_by(usuario='admin_test').first()
            if not dueno:
                dueno = Usuario(nombre="Juan Fernando", usuario="admin_test", password="123", rol="dueno")
                db.session.add(dueno)
                print("✅ Usuario Dueño creado.")
            
            # Crear Sociedad
            sociedad = Sociedad(nombre="Inversiones El Cerrito", nombre_socio="Socio Principal", porcentaje_socio=50.0)
            db.session.add(sociedad)
            db.session.flush() # Para obtener el ID
            print("✅ Sociedad creada.")

            # Crear Ruta
            ruta = Ruta(nombre="Ruta Centro", pais="Colombia", moneda="COP", sociedad_id=sociedad.id)
            db.session.add(ruta)
            db.session.flush()
            print("✅ Ruta creada y asignada a la Sociedad.")
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en Estructura: {e}")
            return

        # ---------------------------------------------------------
        # 3. METER PLATICA (Aporte de Capital)
        # ---------------------------------------------------------
        try:
            # Aportamos 10 millones
            aporte = AporteCapital(
                sociedad_id=sociedad.id,
                nombre_aportante="Juan Fernando",
                monto=10000000,
                registrado_por_id=dueno.id,
                descripcion="Capital inicial para pruebas"
            )
            db.session.add(aporte)
            db.session.commit()
            print(f"✅ Aporte de Capital registrado: ${aporte.monto:,.0f}")
        except Exception as e:
            print(f"❌ Error en Capital: {e}")

        # ---------------------------------------------------------
        # 4. EL CLIENTE (Doña María)
        # ---------------------------------------------------------
        try:
            cliente = Cliente(
                nombre="Doña María Tienda",
                documento="111222333",
                telefono="3001234567",
                direccion_negocio="Plaza Principal El Cerrito"
            )
            db.session.add(cliente)
            db.session.flush()
            print(f"✅ Cliente '{cliente.nombre}' registrado.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ El cliente ya existía o hubo error: {e}")
            cliente = Cliente.query.filter_by(documento="111222333").first()

        # ---------------------------------------------------------
        # 5. EL PRÉSTAMO (La hora de la verdad)
        # ---------------------------------------------------------
        try:
            monto_prestar = 1000000  # 1 millón
            interes = 0.20           # 20%
            total_pagar = monto_prestar * (1 + interes) # 1.2 millones
            cuotas = 24
            valor_cuota = total_pagar / cuotas

            prestamo = Prestamo(
                cliente_id=cliente.id,
                ruta_id=ruta.id,
                monto_prestado=monto_prestar,
                tasa_interes=interes,
                monto_a_pagar=total_pagar,
                saldo_actual=total_pagar,
                valor_cuota=valor_cuota,
                numero_cuotas=cuotas,
                frecuencia='DIARIO',
                estado='ACTIVO'
            )
            db.session.add(prestamo)
            db.session.commit()
            print(f"✅ Préstamo creado exitosamente.")
            print(f"   - Prestado: ${monto_prestar:,.0f}")
            print(f"   - A pagar: ${total_pagar:,.0f}")
            print(f"   - Cuota diaria: ${valor_cuota:,.0f}")
        except Exception as e:
            print(f"❌ Error al crear préstamo: {e}")

        # ---------------------------------------------------------
        # 6. EL COBRO (Recibir dinero)
        # ---------------------------------------------------------
        try:
            # Pagamos la primera cuota
            pago = Pago(
                prestamo_id=prestamo.id,
                cobrador_id=dueno.id,
                monto=valor_cuota,
                saldo_anterior=prestamo.saldo_actual,
                saldo_nuevo=prestamo.saldo_actual - valor_cuota,
                observaciones="Primer pago de prueba"
            )
            
            # Actualizamos el préstamo
            prestamo.saldo_actual -= valor_cuota
            prestamo.cuotas_pagadas += 1
            prestamo.fecha_ultimo_pago = datetime.utcnow()
            
            db.session.add(pago)
            db.session.commit()
            
            print(f"✅ Pago registrado exitosamente.")
            print(f"   - Nuevo Saldo del Cliente: ${prestamo.saldo_actual:,.0f}")
        except Exception as e:
            print(f"❌ Error al registrar pago: {e}")

        print("\n✨ --- PRUEBA FINALIZADA CON ÉXITO --- ✨\n")

if __name__ == "__main__":
    prueba_maestra()