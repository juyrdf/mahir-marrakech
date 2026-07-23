import requests
import json
import time

def test_create_driver():
    url = "http://localhost:8000/api/v1/admin/drivers"
    payload = {
        "full_name": "Hamid El Idrissi",
        "phone_number": "+212600000001",
        "vehicle_plate": "40-A-98765",
        "vehicle_type": "Petit Taxi"
    }
    
    print(f"Creating driver at {url}...")
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Driver Created:")
            print(json.dumps(data, indent=2))
        else:
            print(f"[FAILED] Status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

def test_list_drivers():
    url = "http://localhost:8000/api/v1/admin/drivers"
    print(f"Listing drivers at {url}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Drivers found: {len(data)}")
            print(json.dumps(data, indent=2))
        else:
            print(f"[FAILED] Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

def test_create_service():
    url = "http://localhost:8000/api/v1/admin/services"
    payload = {
        "name": "Cafe des Epices",
        "type": "Restaurant",
        "description": "Famous rooftop in Medina",
        "location": "Rahba Kedima",
        "price_range": "$$"
    }
    print(f"Creating service at {url}...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[SUCCESS] Service Created:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"[FAILED] {response.text}")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    time.sleep(2)
    # test_create_driver() 
    # test_list_drivers()
    test_create_service()
