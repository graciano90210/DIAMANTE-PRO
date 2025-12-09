from flask import Flask, render_template

app = Flask(__name__, template_folder='app/templates')

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/estado')
def estado():
    return {"estado": "OK"}

if __name__ == '__main__':
    print("💎 SERVIDOR DE PRUEBA 💎")
    print("🌐 Abre: http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
