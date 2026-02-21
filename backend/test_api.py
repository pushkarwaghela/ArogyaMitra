# backend/test_api.py
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def register_user():
    """Register a new test user"""
    print("\n📝 Registering test user...")
    
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test@123456",
        "full_name": "Test User",
        "age": 25,
        "gender": "male",
        "height": 175,
        "weight": 70,
        "fitness_level": "beginner",
        "fitness_goal": "weight_loss",
        "workout_preference": "moderate",
        "diet_preference": "vegetarian"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return response.json()
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def login_user():
    """Login to get access token"""
    print("\n🔐 Logging in...")
    
    login_data = {
        "username": "testuser",
        "password": "Test@123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/json", json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            return token_data["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 Testing Registration")
    print("=" * 60)
    
    result = register_user()
    if result:
        print(f"User created: {result}")
    
    print("\n" + "=" * 60)