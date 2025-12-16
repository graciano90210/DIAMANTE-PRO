"""
Script para probar la API REST de la app móvil
Simula las peticiones que haría la aplicación móvil
"""
import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

def test_login():
    """Probar login y obtener token"""
    print("\n========== TEST LOGIN ==========")
    
    response = requests.post(f"{BASE_URL}/login", json={
        "usuario": "cristian",  # Cambiar por un usuario existente
        "password": "1234"
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        return response.json()['access_token']
    return None

def test_obtener_rutas(token):
    """Probar obtener rutas del cobrador"""
    print("\n========== TEST OBTENER RUTAS ==========")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cobrador/rutas", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()

def test_obtener_clientes(token, ruta_id=None):
    """Probar obtener clientes"""
    print("\n========== TEST OBTENER CLIENTES ==========")
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/cobrador/clientes"
    if ruta_id:
        url += f"?ruta_id={ruta_id}"
    
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()

def test_obtener_prestamos(token, ruta_id=None):
    """Probar obtener préstamos"""
    print("\n========== TEST OBTENER PRÉSTAMOS ==========")
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/cobrador/prestamos"
    if ruta_id:
        url += f"?ruta_id={ruta_id}"
    
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()

def test_ruta_cobro(token, ruta_id=None):
    """Probar obtener ruta de cobro del día"""
    print("\n========== TEST RUTA DE COBRO ==========")
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/cobrador/ruta-cobro"
    if ruta_id:
        url += f"?ruta_id={ruta_id}"
    
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()

def test_estadisticas(token, ruta_id=None):
    """Probar obtener estadísticas"""
    print("\n========== TEST ESTADÍSTICAS ==========")
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/cobrador/estadisticas"
    if ruta_id:
        url += f"?ruta_id={ruta_id}"
    
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()

def test_registrar_pago(token, prestamo_id, monto, observaciones=""):
    """Probar registrar un pago"""
    print("\n========== TEST REGISTRAR PAGO ==========")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/cobrador/registrar-pago", 
        headers=headers,
        json={
            "prestamo_id": prestamo_id,
            "monto": monto,
            "observaciones": observaciones
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBAS DE API REST - DIAMANTE PRO")
    print("=" * 60)
    
    # 1. Login
    token = test_login()
    
    if not token:
        print("\n❌ Error en login. Verifica usuario y contraseña.")
        exit(1)
    
    print(f"\n✅ Token obtenido: {token[:50]}...")
    
    # 2. Obtener rutas
    rutas = test_obtener_rutas(token)
    ruta_id = rutas[0]['id'] if rutas else None
    
    # 3. Obtener clientes
    clientes = test_obtener_clientes(token, ruta_id)
    
    # 4. Obtener préstamos
    prestamos = test_obtener_prestamos(token, ruta_id)
    
    # 5. Ruta de cobro del día
    ruta_cobro = test_ruta_cobro(token, ruta_id)
    
    # 6. Estadísticas
    estadisticas = test_estadisticas(token, ruta_id)
    
    # 7. Registrar pago (comentado para no modificar datos)
    # if prestamos:
    #     prestamo_id = prestamos[0]['id']
    #     valor_cuota = prestamos[0]['valor_cuota']
    #     test_registrar_pago(token, prestamo_id, valor_cuota, "Pago de prueba API")
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 60)
