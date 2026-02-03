"""
Script para corregir la indentación del archivo routes.py
El problema: desde la línea 2348, todo el código está indentado con 4 espacios extra
cuando debería estar a nivel del módulo (sin indentación para los decoradores @main.route).
"""

def fix_routes_indentation():
    with open('app/routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar la posición exacta donde termina el return de reportes
    # Buscamos: "     rol=session.get('rol'))\n\n    # ===================="
    marker = "     rol=session.get('rol'))\n\n    # ==================== GESTIÓN DE USUARIOS =="
    
    pos = content.find(marker)
    
    if pos == -1:
        print("❌ No se encontró el marcador. Buscando alternativa...")
        # Intento alternativo
        marker = "rol=session.get('rol'))\n\n    # ==================== GESTIÓN DE USUARIOS"
        pos = content.find(marker)
    
    if pos == -1:
        print("❌ No se pudo encontrar el punto de corrección.")
        return
    
    # Encontrar donde termina la línea del rol
    end_of_return = content.find("rol=session.get('rol'))", pos) + len("rol=session.get('rol'))")
    
    # Todo antes de este punto se mantiene igual
    before = content[:end_of_return]
    
    # Todo después necesita quitar 4 espacios de cada línea
    after = content[end_of_return:]
    
    # Procesar línea por línea
    lines = after.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Si la línea empieza con 4 espacios, quitarlos
        if line.startswith('    '):
            fixed_lines.append(line[4:])
        else:
            fixed_lines.append(line)
    
    fixed_after = '\n'.join(fixed_lines)
    
    # Combinar
    fixed_content = before + fixed_after
    
    with open('app/routes.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Archivo corregido exitosamente")
    print(f"📍 Se procesaron {len(lines)} líneas desde la posición {end_of_return}")

if __name__ == '__main__':
    fix_routes_indentation()
