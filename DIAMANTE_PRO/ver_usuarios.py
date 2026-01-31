import sqlite3
import os

db_path = os.path.join('instance', 'diamante.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT nombre, usuario, password, rol, activo FROM usuarios')
    usuarios = cursor.fetchall()
    
    print("\n" + "="*80)
    print("                👥 USUARIOS REGISTRADOS EN DIAMANTE PRO")
    print("="*80 + "\n")
    
    if usuarios:
        for u in usuarios:
            print(f"📌 Nombre:   {u[0]}")
            print(f"   Usuario:  {u[1]}")
            print(f"   Password: {u[2]}")
            print(f"   Rol:      {u[3].upper()}")
            estado = "ACTIVO ✅" if u[4] else "INACTIVO ❌"
            print(f"   Estado:   {estado}")
            print("-" * 80)
    else:
        print("⚠️  No hay usuarios registrados.")
        print("    Ejecuta: python crear_admin.py\n")
    
    conn.close()
else:
    print("❌ No se encontró la base de datos en: " + db_path)
