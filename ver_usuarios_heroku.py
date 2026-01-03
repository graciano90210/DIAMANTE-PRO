import os
import psycopg2

# URL de conexión de Heroku Postgres
DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgres://u95hqjcm0mtr95:pbfbe43634b6665a8119f80dfdeda03171ca2bd96a52cc56197d05672285e7554@c85cgnr0vdhse3.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d807tg1keg7c24'

# Ajustar URL si empieza con postgres:// en vez de postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    print("\n🔄 Conectando a la base de datos de Heroku...\n")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    cursor.execute('SELECT nombre, usuario, password, rol, activo FROM usuarios ORDER BY id')
    usuarios = cursor.fetchall()
    
    print("="*80)
    print("                👥 USUARIOS REGISTRADOS EN HEROKU")
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
        
        print(f"\n✅ Total de usuarios: {len(usuarios)}\n")
    else:
        print("⚠️  No hay usuarios registrados en Heroku.\n")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error al conectar con Heroku: {e}\n")
