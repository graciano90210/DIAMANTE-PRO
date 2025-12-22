import pytest
import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

# --- 1. FIXTURE PARA OBTENER TOKEN AUTOMÁTICAMENTE ---
@pytest.fixture
def token():
    """Esta función obtiene el token automáticamente para los tests que lo necesiten"""
    url = f"{BASE_URL}/login"
    payload = {
        "usuario": "cristian", 
        "password": "1234"
    }
    # Intentamos loguearnos
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        # Si falla (por ejemplo, si el usuario no existe en la BD limpia de GitHub)
        # Esto nos avisará claramente en el log
        print(f"\n⚠️ IMPORTANTE: No se pudo loguear. Status: {response.status_code}")
        print("¿Has creado el usuario 'cristian' en la base de datos de prueba?")
        pytest.fail(f"Login fallido. Status: {response.status_code}")

# --- 2. PRUEBAS UNITARIAS (COMPATIBLES CON PYTEST) ---

def test_login_explicit():
    """Prueba explícita del login para verificar status 200"""
    print("\n========== TEST LOGIN ==========")
    response = requests.post(f"{BASE_URL}/login", json={
        "usuario": "cristian",
        "password": "1234"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_obtener_rutas(token):
    """Probar obtener rutas del cobrador usando el token"""
    print("\n========== TEST OBTENER RUTAS ==========")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cobrador/rutas", headers=headers)
    
    # Validaciones
    assert response.status_code == 200
    print(f"Rutas encontradas: {len(response.json())}")
    return response.json()

def test_obtener_clientes(token):
    """Probar obtener clientes (sin filtrar por ruta específica para el test general)"""
    print("\n========== TEST OBTENER CLIENTES ==========")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cobrador/clientes", headers=headers)
    
    assert response.status_code == 200
    return response.json()

def test_obtener_prestamos(token):
    """Probar obtener préstamos"""
    print("\n========== TEST OBTENER PRÉSTAMOS ==========")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cobrador/prestamos", headers=headers)
    
    assert response.status_code == 200
    return response.json()

def test_ruta_cobro(token):
    """Probar obtener ruta de cobro del día"""
    print("\n========== TEST RUTA DE COBRO ==========")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cobrador/ruta-cobro", headers=headers)
    
    assert response.status_code == 200
    return response.json()

def test_estadisticas(token):
    """Probar obtener estadísticas"""
    print("\n========== TEST ESTADÍSTICAS ==========")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cobrador/estadisticas", headers=headers)
    
    assert response.status_code == 200
    return response.json()

# --- 3. BLOQUE PARA EJECUCIÓN MANUAL (OPCIONAL) ---
# Esto solo se ejecuta si corres "python test_api.py" manualmente, 
# Pytest ignorará esta parte.

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBAS DE API REST - MODO MANUAL")
    print("=" * 60)
    
    # Simulamos el login manual
    try:
        resp = requests.post(f"{BASE_URL}/login", json={"usuario": "cristian", "password": "1234"})
        if resp.status_code == 200:
            mi_token = resp.json()['access_token']
            print("✅ Login manual exitoso")
            
            # Ejecutamos pruebas pasando el token manualmente
            test_obtener_rutas(mi_token)
            test_obtener_clientes(mi_token)
            test_obtener_prestamos(mi_token)
            test_ruta_cobro(mi_token)
            test_estadisticas(mi_token)
        else:
            print("❌ Error en login manual.")
    except Exception as e:
        print(f"❌ Error conectando con el servidor: {e}")