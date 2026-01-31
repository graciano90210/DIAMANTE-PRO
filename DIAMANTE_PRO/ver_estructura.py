import os
import sys

# Forzar la salida a usar UTF-8 por si acaso, o usar caracteres simples
sys.stdout.reconfigure(encoding='utf-8')

def listar_archivos(startpath):
    print(f"\n[PROYECTO] Estructura: {startpath}\n")
    for root, dirs, files in os.walk(startpath):
        # Ignoramos carpetas del sistema o venv para limpiar la vista
        if '.git' in root or 'venv' in root or '__pycache__' in root or '.idea' in root:
            continue
            
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}[DIR] {os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{subindent}- {f}')

# Ejecutar en la carpeta actual
listar_archivos('.')