from app import create_app

app = create_app()

if __name__ == '__main__':
    print("💎 SISTEMA DIAMANTE PRO INICIADO 💎")
    app.run(debug=True)