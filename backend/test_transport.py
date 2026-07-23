import requests
import json
import time

def test_transport_quote():
    url = "http://localhost:8000/api/v1/transport/quote"
    payload = {
        "origin": "Jemaa el-Fnaa",
        "destination": "Majorelle Garden",
        "passenger_count": 2
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Quote received:")
            print(f"Price Range: {data.get('min_price')} - {data.get('max_price')} MAD")
            print(json.dumps(data, indent=2))
        else:
            print(f"[FAILED] Status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    # Wait a bit for server to start if running via script
    time.sleep(2)
    test_transport_quote()
