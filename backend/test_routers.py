# backend/test_routers.py
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ {name}: OK (200)")
            if response.text:
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
        elif response.status_code == 404:
            print(f"⚠️ {name}: Not Found (404) - Endpoint may require auth")
        else:
            print(f"❌ {name}: Error ({response.status_code})")
    except Exception as e:
        print(f"❌ {name}: Connection Error - {str(e)}")

print("=" * 60)
print("🔬 Testing ArogyaMitra API Endpoints")
print("=" * 60)

# Test basic endpoints
test_endpoint("Root API", f"{BASE_URL}/")
test_endpoint("Health Check", f"{BASE_URL}/health")
test_endpoint("Docs (Swagger)", f"{BASE_URL}/docs")
test_endpoint("ReDoc", f"{BASE_URL}/redoc")
test_endpoint("OpenAPI JSON", f"{BASE_URL}/openapi.json")

print("\n" + "=" * 60)
print("Testing API Routers (if implemented)")
print("=" * 60)

# Test API endpoints (if they exist)
api_endpoints = [
    ("Auth", "/api/v1/auth"),
    ("Users", "/api/v1/users"),
    ("Workouts", "/api/v1/workouts"),
    ("Nutrition", "/api/v1/nutrition"),
    ("Progress", "/api/v1/progress"),
    ("AROMI", "/api/v1/aromi"),
]

for name, path in api_endpoints:
    test_endpoint(name, f"{BASE_URL}{path}")

print("=" * 60)