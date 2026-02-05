#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de Rate Limiting para la API
Verifica que el endpoint /api/v1/login tenga protección contra fuerza bruta
"""
import requests
import time

BASE_URL = "http://127.0.0.1:5001"
LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/login"

def test_rate_limiting():
    """
    Prueba que el rate limiting funciona correctamente.
    Debe permitir 5 requests por minuto y luego bloquear.
    """
    print("=" * 60)
    print("TEST DE RATE LIMITING - API LOGIN")
    print("=" * 60)
    print(f"Endpoint: {LOGIN_ENDPOINT}")
    print(f"Límite esperado: 5 requests/minuto\n")

    # Payload de prueba (credenciales inválidas)
    payload = {
        "usuario": "test_usuario_inexistente",
        "password": "password_incorrecto"
    }

    resultados = []

    # Intentar 7 requests (debe bloquear después de la 5ta)
    for i in range(1, 8):
        try:
            response = requests.post(LOGIN_ENDPOINT, json=payload, timeout=5)
            status = response.status_code

            # Verificar si fue bloqueado por rate limit
            if status == 429:  # HTTP 429 Too Many Requests
                print(f"[OK] Request #{i}: BLOQUEADO por rate limit (429)")
                resultados.append(("BLOQUEADO", status))
            elif status == 401:  # Credenciales inválidas (esperado)
                print(f"[  ] Request #{i}: Permitido (401 - credenciales invalidas)")
                resultados.append(("PERMITIDO", status))
            elif status == 400:  # Bad request
                print(f"[  ] Request #{i}: Permitido (400 - bad request)")
                resultados.append(("PERMITIDO", status))
            else:
                print(f"[??] Request #{i}: Estado inesperado ({status})")
                resultados.append(("OTRO", status))

        except requests.exceptions.RequestException as e:
            print(f"[ERR] Request #{i}: ERROR - {str(e)}")
            resultados.append(("ERROR", None))

        # Pequeña pausa entre requests
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("RESULTADOS DEL TEST")
    print("=" * 60)

    permitidos = sum(1 for r, _ in resultados if r == "PERMITIDO")
    bloqueados = sum(1 for r, _ in resultados if r == "BLOQUEADO")

    print(f"Requests permitidos: {permitidos}")
    print(f"Requests bloqueados: {bloqueados}")

    if bloqueados >= 2:  # Al menos 2 bloqueados (6to y 7mo)
        print("\n[OK] RATE LIMITING FUNCIONANDO CORRECTAMENTE")
        print("     El sistema esta protegido contra ataques de fuerza bruta.")
        return True
    else:
        print("\n[WARN] RATE LIMITING NO DETECTADO")
        print("       Verifica que Flask-Limiter este correctamente configurado.")
        return False

def test_hashing_bcrypt():
    """
    Verifica que el sistema de hashing use bcrypt de forma consistente.
    """
    print("\n" + "=" * 60)
    print("TEST DE CONSISTENCIA DE HASHING")
    print("=" * 60)

    from app.models import Usuario

    # Crear usuario de prueba en memoria
    test_user = Usuario(
        nombre="Test Usuario",
        usuario="test_user_temp",
        rol="cobrador"
    )

    # Verificar que set_password usa bcrypt
    test_password = "test_password_123"
    test_user.set_password(test_password)

    # El hash bcrypt siempre empieza con $2b$
    if test_user.password.startswith('$2b$'):
        print("[OK] set_password() usa bcrypt correctamente")

        # Verificar que check_password funciona
        if test_user.check_password(test_password):
            print("[OK] check_password() verifica correctamente")
            print("\n[OK] SISTEMA DE HASHING CONSISTENTE")
            return True
        else:
            print("[ERR] check_password() NO funciona")
            return False
    else:
        print(f"[ERR] set_password() NO usa bcrypt (hash: {test_user.password[:10]}...)")
        return False

if __name__ == "__main__":
    print("\n[SEGURIDAD] SUITE DE TESTS - DIAMANTE PRO\n")

    # Test 1: Hashing consistente
    test1_passed = test_hashing_bcrypt()

    # Test 2: Rate limiting
    test2_passed = test_rate_limiting()

    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    print(f"Test de Hashing:       {'[PASS]' if test1_passed else '[FAIL]'}")
    print(f"Test de Rate Limiting: {'[PASS]' if test2_passed else '[FAIL]'}")

    if test1_passed and test2_passed:
        print("\n[OK] TODOS LOS TESTS DE SEGURIDAD PASARON")
    else:
        print("\n[WARN] ALGUNOS TESTS FALLARON - REVISAR CONFIGURACION")
