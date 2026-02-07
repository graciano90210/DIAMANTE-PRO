"""
Migración: Agregar campo moneda a la tabla transacciones
Fecha: 2026-02-06
Descripción: Permite segregar gastos/ingresos por moneda (COP, BRL, PEN, etc.)
             Necesario para el dashboard multi-país.
"""
import sqlite3
import os


def migrate(db_path):
    """
    Ejecuta la migración para agregar el campo moneda a transacciones
    """
    print(f"Conectando a la base de datos: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(transacciones)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'moneda' not in columns:
            print("Agregando columna 'moneda' a la tabla 'transacciones'...")
            cursor.execute("""
                ALTER TABLE transacciones
                ADD COLUMN moneda VARCHAR(3) DEFAULT 'COP'
            """)
            conn.commit()
            print("Columna 'moneda' agregada exitosamente.")

            # Actualizar registros existentes
            cursor.execute("""
                UPDATE transacciones SET moneda = 'COP' WHERE moneda IS NULL
            """)
            conn.commit()
            print("Registros existentes actualizados con valor por defecto 'COP'.")
        else:
            print("La columna 'moneda' ya existe en transacciones. Migración omitida.")

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


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'instance', 'diamante.db')

    if not os.path.exists(db_path):
        db_path = os.path.join(base_dir, 'diamante.db')

    if not os.path.exists(db_path):
        print(f"Base de datos no encontrada en: {db_path}")
        print("Por favor, especifique la ruta correcta.")
    else:
        migrate(db_path)
