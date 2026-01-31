"""
Limpiar datos antes de importar a Heroku
Asignar ruta_id a préstamos que no lo tengan
"""
import json

# Leer datos
with open('datos_completos.json', 'r', encoding='utf-8') as f:
    datos = json.load(f)

print(f"📊 Analizando {len(datos['prestamos'])} préstamos...")

# Contar préstamos sin ruta
sin_ruta = sum(1 for p in datos['prestamos'] if p['ruta_id'] is None)
print(f"⚠️  {sin_ruta} préstamos sin ruta_id")

if sin_ruta > 0:
    print("\n🔧 Asignando rutas a préstamos...")
    
    # Para cada préstamo sin ruta, buscar ruta del cobrador
    for prestamo in datos['prestamos']:
        if prestamo['ruta_id'] is None:
            cobrador_id = prestamo['cobrador_id']
            
            # Buscar ruta del cobrador
            ruta_cobrador = next((r for r in datos['rutas'] if r['cobrador_id'] == cobrador_id), None)
            
            if ruta_cobrador:
                prestamo['ruta_id'] = ruta_cobrador['id']
                print(f"   ✅ Préstamo {prestamo['id']} → Ruta {ruta_cobrador['nombre']}")
            else:
                # Si no hay ruta, asignar a la primera disponible
                prestamo['ruta_id'] = datos['rutas'][0]['id'] if datos['rutas'] else 1
                print(f"   ⚠️  Préstamo {prestamo['id']} → Ruta por defecto")

# Guardar datos limpios
with open('datos_completos.json', 'w', encoding='utf-8') as f:
    json.dump(datos, f, indent=2, ensure_ascii=False)

print(f"\n✅ Datos limpios guardados")
print(f"📊 Verificación: {sum(1 for p in datos['prestamos'] if p['ruta_id'] is None)} préstamos sin ruta")
