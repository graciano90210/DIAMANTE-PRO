"""Verificar rutas registradas"""
from app import create_app

app = create_app()

rutas = sorted([r.rule for r in app.url_map.iter_rules() if not r.rule.startswith('/static')])

print(f"Total de rutas: {len(rutas)}")
print("\n=== BLUEPRINTS REGISTRADOS ===")
for bp_name in app.blueprints:
    print(f"  ✅ {bp_name}")

print("\n=== RUTAS AUTH (nuevo blueprint) ===")
for r in rutas:
    if r in ['/', '/login', '/logout', '/estado']:
        print(f"  {r}")

print("\n=== RUTAS CLIENTES (nuevo blueprint) ===")
for r in rutas:
    if '/clientes' in r:
        print(f"  {r}")

print("\n=== RUTAS PRINCIPALES (routes.py) ===")
principales = ['/dashboard', '/prestamos', '/cobro/lista', '/rutas', '/sociedades', '/reportes']
for r in rutas:
    for p in principales:
        if r == p or r.startswith(p + '/'):
            print(f"  {r}")
            break
