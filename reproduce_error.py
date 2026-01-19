import requests
import json

BASE_URL = 'http://diamante-pro-1951dcdb66df.herokuapp.com/api/v1'
ENDPOINT = '/cobrador/registrar-pago'

def test_http_redirect():
    print("Testing HTTP to HTTPS redirect with Header...")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer test_token'
    }
    data = {"test": "data"}
    
    try:
        response = requests.post(f"{BASE_URL}{ENDPOINT}", json=data, headers=headers) # requests follows redirects by default
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        print(f"History: {response.history}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_http_redirect()
