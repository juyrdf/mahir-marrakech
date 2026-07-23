import requests
import json

def test_full_diagnostics():
    base_url = "http://localhost:8000"
    print(f"🔍 Starting Deep Diagnostics for {base_url}...")
    
    # 1. Test Root
    try:
        r = requests.get(f"{base_url}/")
        print(f"✅ Root Status: {r.status_code}")
        print(f"   Response: {r.text}")
    except:
        print("❌ Could not connect to Root.")

    # 2. Test OpenAPI Spec (The real map)
    print("\n🗺️ Fetching Server Route Map...")
    try:
        r = requests.get(f"{base_url}/api/v1/openapi.json")
        if r.status_code == 200:
            spec = r.json()
            paths = spec.get("paths", {}).keys()
            print(f"✅ Found {len(paths)} registered routes.")
            print("--- Registered Admin Routes ---")
            admin_routes = [p for p in paths if "/admin" in p]
            for p in admin_routes:
                print(f"  -> {p}")
            
            if "/api/v1/admin/discover-partners" in paths:
                print("\n🌟 SUCCESS: The route IS registered in the server map!")
            else:
                print("\n🚫 MISSING: The discovery route is NOT in the map.")
        else:
            print(f"❌ Failed to fetch map (Status {r.status_code}).")
    except Exception as e:
        print(f"❌ Error fetching map: {e}")

    # 3. Test the specific endpoint and show exact error
    print("\n🎯 Testing Target Endpoint...")
    try:
        url = f"{base_url}/api/v1/admin/discover-partners"
        r = requests.get(url)
        print(f"   Status: {r.status_code}")
        print(f"   Details: {r.text}")
    except Exception as e:
        print(f"   Connection failed: {e}")

if __name__ == "__main__":
    test_full_diagnostics()
