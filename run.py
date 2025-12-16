from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Heroku asigna el puerto dinámicamente
    port = int(os.environ.get('PORT', 5001))
    
    print("💎 SISTEMA DIAMANTE PRO INICIADO 💎")
    print(f"🌐 Servidor corriendo en puerto: {port}")
    
    # En desarrollo usa localhost, en producción 0.0.0.0
    host = '0.0.0.0' if os.environ.get('DATABASE_URL') else '127.0.0.1'
    debug = not bool(os.environ.get('DATABASE_URL'))
    
    app.run(host=host, port=port, debug=debug, threaded=True)