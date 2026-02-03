from flask import Blueprint, render_template
from flask_login import login_required
# Creamos un blueprint fresco, sin errores heredados
admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/usuarios')
@login_required
def usuarios_lista():
    # Asegúrate de tener el template usuarios_lista.html
    return render_template('usuarios_lista.html')

@admin_bp.route('/caja')
@login_required
def caja_inicio():
    return render_template('caja.html')

@admin_bp.route('/traslados')
@login_required
def traslados_lista():
    return render_template('traslados.html')

@admin_bp.route('/capital/aportes')
@login_required
def capital_aportes():
    return render_template('capital_aportes.html')
