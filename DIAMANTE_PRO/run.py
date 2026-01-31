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
    # Heroku asigna el puerto dinámicamente
    port = int(os.environ.get('PORT', 5001))
    
    print("💎 SISTEMA DIAMANTE PRO INICIADO 💎")
    print(f"🌐 Servidor corriendo en puerto: {port}")
    
    # En desarrollo usa 0.0.0.0 para ser visible externamente
    host = '0.0.0.0'
    debug = not bool(os.environ.get('DATABASE_URL'))
    
    app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=False)