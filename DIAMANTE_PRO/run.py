print("DEBUG: Starting run.py")
# Parche de compatibilidad para Python 3.14 en Windows
import platform
try:
    platform.machine()
except Exception:
    platform.machine = lambda: 'AMD64'

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    print("SISTEMA DIAMANTE PRO INICIADO")
    app.run(debug=True, port=5001)