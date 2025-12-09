from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = 5001
    print("💎 SISTEMA DIAMANTE PRO INICIADO 💎")
    print(f"🌐 Abre tu navegador en: http://127.0.0.1:{port}")
    os.environ['FLASK_ENV'] = 'development'
    app.run(host='127.0.0.1', port=port, debug=False, threaded=True)