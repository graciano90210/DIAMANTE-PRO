import os
import psycopg2

# URL de conexión de Heroku Postgres
DATABASE_URL = 'postgres://u95hqjcm0mtr95:pbfbe43634b6665a8119f80dfdeda03171ca2bd96a52cc56197d05672285e7554@c85cgnr0vdhse3.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d807tg1keg7c24'

# Ajustar URL si empieza con postgres:// en vez de postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    print("\n🔄 Conectando a la base de datos de Heroku...\n")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    # Obtener usuarios cobradores
    cursor.execute("""
        SELECT id, nombre, usuario, rol 
        FROM usuarios 
        WHERE rol = 'COBRADOR' 
        ORDER BY id
    """)
    cobradores = cursor.fetchall()
    
    print("="*80)
    print("           👥 COBRADORES Y SUS RUTAS ASIGNADAS")
    print("="*80 + "\n")
    
    for cobrador in cobradores:
        cobrador_id, nombre, usuario, rol = cobrador
        
        # Obtener rutas del cobrador
        cursor.execute("""
            SELECT r.id, r.nombre, r.zona, r.activo, COUNT(c.id) as total_clientes
            FROM rutas r
            LEFT JOIN clientes c ON c.ruta_id = r.id AND c.activo = TRUE
            WHERE r.cobrador_id = %s
            GROUP BY r.id, r.nombre, r.zona, r.activo
            ORDER BY r.id
        """, (cobrador_id,))
        
        rutas = cursor.fetchall()
        
        print(f"📌 {nombre} (@{usuario})")
        print(f"   ID: {cobrador_id}")
        
        if rutas:
            print(f"   Rutas asignadas: {len(rutas)}")
            for ruta in rutas:
                ruta_id, ruta_nombre, zona, activo, total_clientes = ruta
                estado = "✅ ACTIVA" if activo else "❌ INACTIVA"
                print(f"      • Ruta #{ruta_id}: {ruta_nombre} - Zona: {zona} - {estado} - {total_clientes} clientes")
        else:
            print(f"   ⚠️  SIN RUTAS ASIGNADAS")
        
        print("-" * 80)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error al conectar con Heroku: {e}\n")
