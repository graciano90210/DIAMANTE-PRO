print("DEBUG: Starting run.py")
# Parche de compatibilidad para Python 3.14 en Windows
import platform
try:
    platform.machine()
except Exception:
    platform.machine = lambda: 'AMD64'

import os
import sys

# Cambiar al directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("  SISTEMA DIAMANTE PRO INICIADO")
    print("  Servidor: http://127.0.0.1:5001")
    print("=" * 50)
    app.run(debug=True, port=5001, host='127.0.0.1', use_reloader=False)