"""
Blueprint de Autenticación - Diamante Pro
Maneja: login, logout, home, estado
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from ..models import Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def home():
    """Ruta principal - redirige según estado de sesión"""
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.dashboard'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión"""
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        user = Usuario.query.filter_by(usuario=usuario).first()
        
        if user:
            # Verificar contraseña - soporta hash y texto plano
            password_valid = False
            try:
                # Intentar verificar como hash
                if user.password.startswith('scrypt:') or user.password.startswith('pbkdf2:'):
                    password_valid = check_password_hash(user.password, password)
                else:
                    # Contraseña en texto plano
                    password_valid = (user.password == password)
            except:
                # Si falla, comparar como texto plano
                password_valid = (user.password == password)
            
            if password_valid:
                result = login_user(user, remember=True)
                print(f"DEBUG LOGIN: login_user returned {result}, user.id={user.id}, is_active={user.is_active}")
                session['usuario_id'] = user.id
                session['nombre'] = user.nombre
                session['rol'] = user.rol
                session.modified = True
                print(f"DEBUG LOGIN: session keys after login: {list(session.keys())}")
                flash('Bienvenido, {}'.format(user.nombre), 'success')
                return redirect(url_for('main.dashboard'))
        
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/estado')
def estado():
    """Estado del sistema (health check)"""
    return {"estado": "OK", "version": "1.0"}
