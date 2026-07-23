import requests
import json
import time

def check_endpoint(url):
    print(f"Checking {url}...")
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                print("Body snippet: " + str(response.json())[:200])
            except:
                print("Body snippet: " + response.text[:200])
                
            if "openapi" in url:
                data = response.json()
                paths = data.get("paths", {}).keys()
                print("\nRegistered Paths:")
                for p in paths:
                    print(f" - {p}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    time.sleep(2)
    check_endpoint("http://localhost:8000/")
    check_endpoint("http://localhost:8000/openapi.json")
