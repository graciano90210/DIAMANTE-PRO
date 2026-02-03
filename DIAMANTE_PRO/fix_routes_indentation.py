"""
Script para corregir la indentación del archivo routes.py
El problema: desde la línea ~2318, todo el código está indentado dentro de la función reportes()
cuando debería estar a nivel del módulo.
"""

import re

def fix_routes_indentation():
    with open('app/routes.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar la línea donde termina correctamente la función reportes()
    # Es donde está el return render_template('reportes.html'...)
    # y después viene código indentado que no debería estarlo
    
    in_reportes_return = False
    reportes_return_end = 0
    
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Buscar el inicio del return de reportes
        if 'return render_template(' in line and "'reportes.html'" in line:
            in_reportes_return = True
            fixed_lines.append(line)
            i += 1
            continue
        
        # Si estamos dentro del return de reportes, buscar donde termina
        if in_reportes_return:
            fixed_lines.append(line)
            if "rol=session.get('rol'))" in line:
                in_reportes_return = False
                reportes_return_end = i
                i += 1
                # Ahora todo lo que sigue debe perder 4 espacios de indentación
                continue
            i += 1
            continue
        
        # Si ya pasamos el return de reportes, quitar la indentación extra
        if reportes_return_end > 0 and i > reportes_return_end:
            # Quitar 4 espacios de indentación al inicio si la línea tiene al menos 4 espacios
            if line.startswith('    '):
                line = line[4:]  # Quitar los primeros 4 espacios
        
        fixed_lines.append(line)
        i += 1
    
    # Escribir el archivo corregido
    with open('app/routes.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Archivo corregido. Se procesaron {len(lines)} líneas.")
    print(f"📍 La indentación se corrigió desde la línea {reportes_return_end + 1}")

if __name__ == '__main__':
    fix_routes_indentation()
