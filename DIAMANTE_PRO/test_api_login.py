import requests
import json

BASE_URL = "http://localhost:5001/api/v1"

def test_flow():
    # 1. Login
    print("=== LOGIN ===")
    try:
        resp = requests.post(f"{BASE_URL}/login", json={"usuario": "cvampi", "password": "1234"})
        if resp.status_code != 200:
            print(f"Error Login: {resp.status_code} - {resp.text}")
            return
            
        data = resp.json()
        token = data.get('access_token')
        print(f"Token recibido: {token[:20]}...")
        
        # 2. Get Loans
        print("\n=== GET LOANS ===")
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(f"{BASE_URL}/cobrador/prestamos", headers=headers)
        
        if resp.status_code != 200:
            print(f"Error Loans: {resp.status_code} - {resp.text}")
            return
            
        loans = resp.json()
        print(f"Préstamos recibidos ({len(loans)}):")
        print(json.dumps(loans, indent=2))
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_flow()
