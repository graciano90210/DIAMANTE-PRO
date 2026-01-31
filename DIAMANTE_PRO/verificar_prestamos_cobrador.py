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
    
    # Obtener ID de cvampi
    cursor.execute("SELECT id, nombre, usuario FROM usuarios WHERE usuario = 'cvampi'")
    cobrador = cursor.fetchone()
    
    if not cobrador:
        print("❌ Usuario cvampi no encontrado")
        exit()
    
    cobrador_id, nombre, usuario = cobrador
    
    print("="*80)
    print(f"           PRÉSTAMOS DEL COBRADOR: {nombre} (@{usuario})")
    print(f"           ID de cobrador: {cobrador_id}")
    print("="*80 + "\n")
    
    # Obtener préstamos del cobrador
    cursor.execute("""
        SELECT p.id, c.nombre as cliente, p.monto_prestado, p.saldo_actual, 
               p.estado, p.cobrador_id, p.frecuencia
        FROM prestamos p
        JOIN clientes c ON c.id = p.cliente_id
        WHERE p.cobrador_id = %s
        ORDER BY p.fecha_inicio DESC
        LIMIT 20
    """, (cobrador_id,))
    
    prestamos = cursor.fetchall()
    
    if prestamos:
        print(f"✅ Total de préstamos encontrados: {len(prestamos)}\n")
        for p in prestamos:
            prestamo_id, cliente, monto, saldo, estado, cob_id, freq = p
            print(f"📌 Préstamo #{prestamo_id}")
            print(f"   Cliente: {cliente}")
            print(f"   Monto: ${monto} - Saldo: ${saldo}")
            print(f"   Estado: {estado} - Frecuencia: {freq}")
            print(f"   Cobrador ID: {cob_id}")
            print("-" * 80)
    else:
        print(f"⚠️  NO SE ENCONTRARON PRÉSTAMOS para el cobrador_id={cobrador_id}")
        print("\n🔍 Verificando si hay préstamos con ruta_id del cobrador...\n")
        
        # Verificar si hay préstamos con rutas asignadas al cobrador
        cursor.execute("""
            SELECT p.id, c.nombre as cliente, p.monto_prestado, p.saldo_actual, 
                   p.estado, p.cobrador_id, p.ruta_id, r.nombre as ruta
            FROM prestamos p
            JOIN clientes c ON c.id = p.cliente_id
            LEFT JOIN rutas r ON r.id = p.ruta_id
            WHERE p.ruta_id IN (SELECT id FROM rutas WHERE cobrador_id = %s)
            ORDER BY p.fecha_inicio DESC
            LIMIT 20
        """, (cobrador_id,))
        
        prestamos_ruta = cursor.fetchall()
        
        if prestamos_ruta:
            print(f"✅ Préstamos encontrados por RUTA: {len(prestamos_ruta)}")
            print("\n⚠️  PROBLEMA: Los préstamos tienen ruta_id pero NO tienen cobrador_id\n")
            print("💡 SOLUCIÓN: Necesitas actualizar los préstamos para asignarles cobrador_id\n")
            
            for p in prestamos_ruta:
                prestamo_id, cliente, monto, saldo, estado, cob_id, ruta_id, ruta = p
                print(f"📌 Préstamo #{prestamo_id}")
                print(f"   Cliente: {cliente}")
                print(f"   Ruta: {ruta} (ID: {ruta_id})")
                print(f"   Cobrador ID actual: {cob_id} (NULL o incorrecto)")
                print(f"   Estado: {estado}")
                print("-" * 80)
        else:
            print("❌ No se encontraron préstamos ni por cobrador_id ni por ruta_id")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}\n")
