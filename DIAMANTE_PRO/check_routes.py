"""Script para verificar rutas registradas"""
from app import create_app

app = create_app()

rutas = [r.rule for r in app.url_map.iter_rules()]

print("RUTAS DE SOCIEDADES:")
for r in sorted(rutas):
    if 'socied' in r:
        print(f"  ✅ {r}")

print("\nRUTAS DE CLIENTES:")
for r in sorted(rutas):
    if 'client' in r:
        print(f"  ✅ {r}")

print("\nRUTAS GENERALES:")
for r in sorted(rutas):
    if 'ruta' in r.lower():
        print(f"  ✅ {r}")
