# backend/register_user.py
import requests
import json

url = "http://localhost:8000/api/v1/auth/register"

# Use the correct enum values from your schema
data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test@123456",
    "full_name": "Test User",
    "age": 25,
    "gender": "male",
    "height": 175,
    "weight": 70,
    "fitness_level": "beginner",
    "fitness_goal": "weight_loss",  # Valid value
    "workout_preference": "moderate",  # Changed from "hybrid" to "moderate"
    "diet_preference": "vegetarian"  # Valid value
}

print("Sending data:")
print(json.dumps(data, indent=2))

response = requests.post(url, json=data)
print(f"\nStatus Code: {response.status_code}")

try:
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except:
    print(f"Raw response: {response.text}")