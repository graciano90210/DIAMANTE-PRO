from flask import current_app as app

@app.route('/')
def home():
    return "<h1>💎 DIAMANTE PRO ESTÁ VIVO 💎</h1><p>Sistema de Cobros y Préstamos Activo.</p>"

@app.route('/estado')
def estado():
    return {"estado": "OK", "mensaje": "Base de datos conectada", "version": "1.0"}