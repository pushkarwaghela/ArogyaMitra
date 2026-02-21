# backend/debug_registration.py
import requests
import json
import sys

url = "http://localhost:8000/api/v1/auth/register"

# Test different combinations
test_cases = [
    {
        "name": "Test 1 - Minimal",
        "data": {
            "email": "test1@example.com",
            "username": "test1",
            "password": "Test@123456",
            "full_name": "Test User 1"
        }
    },
    {
        "name": "Test 2 - With valid enums",
        "data": {
            "email": "test2@example.com",
            "username": "test2",
            "password": "Test@123456",
            "full_name": "Test User 2",
            "age": 25,
            "gender": "male",
            "height": 175,
            "weight": 70,
            "fitness_level": "beginner",
            "fitness_goal": "weight_loss",
            "workout_preference": "moderate",
            "diet_preference": "vegetarian"
        }
    },
    {
        "name": "Test 3 - Alternative enums",
        "data": {
            "email": "test3@example.com",
            "username": "test3",
            "password": "Test@123456",
            "full_name": "Test User 3",
            "age": 30,
            "gender": "female",
            "height": 165,
            "weight": 60,
            "fitness_level": "intermediate",
            "fitness_goal": "muscle_gain",
            "workout_preference": "high_intensity",
            "diet_preference": "non_vegetarian"
        }
    }
]

for test in test_cases:
    print("\n" + "=" * 60)
    print(f"🔍 {test['name']}")
    print("=" * 60)
    print(f"Data: {json.dumps(test['data'], indent=2)}")
    
    try:
        response = requests.post(url, json=test['data'])
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            break  # Stop on first success
        else:
            try:
                error_data = response.json()
                print(f"❌ Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"❌ Raw response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n" + "=" * 60)