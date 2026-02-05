"""
Migración: Agregar campo metodo_pago a la tabla pagos
Fecha: 2026-02-05
Descripción: Permite diferenciar pagos por EFECTIVO, PIX o TRANSFERENCIA
"""
import sqlite3
import os

def migrate(db_path):
    """
    Ejecuta la migración para agregar el campo metodo_pago
    """
    print(f"Conectando a la base de datos: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(pagos)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'metodo_pago' not in columns:
            print("Agregando columna 'metodo_pago' a la tabla 'pagos'...")
            cursor.execute("""
                ALTER TABLE pagos
                ADD COLUMN metodo_pago VARCHAR(20) DEFAULT 'EFECTIVO'
            """)
            conn.commit()
            print("Columna 'metodo_pago' agregada exitosamente.")

            # Actualizar registros existentes
            cursor.execute("""
                UPDATE pagos SET metodo_pago = 'EFECTIVO' WHERE metodo_pago IS NULL
            """)
            conn.commit()
            print("Registros existentes actualizados con valor por defecto 'EFECTIVO'.")
        else:
            print("La columna 'metodo_pago' ya existe. Migración omitida.")

        print("Migración completada exitosamente!")

    except Exception as e:
        print(f"Error durante la migración: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def rollback(db_path):
    """
    Revierte la migración (SQLite no soporta DROP COLUMN fácilmente)
    """
    print("NOTA: SQLite no soporta DROP COLUMN directamente.")
    print("Para revertir, se requiere recrear la tabla sin la columna.")
    print("Esta operación no se implementa automáticamente por seguridad.")


if __name__ == '__main__':
    # Ruta por defecto de la base de datos
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'instance', 'diamantepro.db')

    # Verificar rutas alternativas
    if not os.path.exists(db_path):
        db_path = os.path.join(base_dir, 'diamantepro.db')

    if not os.path.exists(db_path):
        print(f"Base de datos no encontrada en: {db_path}")
        print("Por favor, especifique la ruta correcta.")
    else:
        migrate(db_path)
