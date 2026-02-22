import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = None

def test_registration():
    print("\n📝 Testing Registration...")
    data = {
        "email": "test1@example.com",
        "username": "testuser1",
        "password": "Test@123456",
        "full_name": "Test User1"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print("  ✅ Registration working")
    elif response.status_code == 400:
        print("  ⚠️ User already exists")
    else:
        print(f"  ❌ Failed: {response.text}")

def test_login():
    global TOKEN
    print("\n🔐 Testing Login...")
    data = {"username": "testuser", "password": "Test@123456"}
    response = requests.post(f"{BASE_URL}/auth/login/json", json=data)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        TOKEN = response.json()["access_token"]
        print("  ✅ Login working, token received")
    else:
        print(f"  ❌ Failed: {response.text}")

def test_auth_me():
    print("\n👤 Testing /auth/me...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"  Status: {response.status_code}")
    print(f"  ✅ Working" if response.status_code == 200 else f"  ❌ Failed")

def test_workout_generate():
    print("\n💪 Testing Workout Generation...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "fitnessLevel": "beginner",
        "goal": "weight_loss",
        "preference": "moderate",
        "daysPerWeek": 5,
        "duration": 30
    }
    response = requests.post(f"{BASE_URL}/workouts/generate", headers=headers, json=data)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print("  ✅ AI Workout Generation working")
    else:
        print(f"  ❌ Failed: {response.text}")

def test_workout_plans():
    print("\n📋 Testing Get Workout Plans...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/workouts/plans", headers=headers)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        plans = response.json()
        print(f"  ✅ Found {len(plans)} workout plans")
    else:
        print(f"  ❌ Failed: {response.text}")

def test_nutrition_generate():
    print("\n🍎 Testing Nutrition Generation...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "calorieTarget": 2000,
        "dietType": "vegetarian",
        "allergies": ["peanuts", "lactose"],
        "mealsPerDay": 4,
        "durationDays": 7
    }
    response = requests.post(f"{BASE_URL}/nutrition/generate", headers=headers, json=data)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print("  ✅ AI Nutrition Generation working")
    else:
        print(f"  ❌ Failed: {response.text}")

def test_nutrition_plans():
    print("\n📋 Testing Get Nutrition Plans...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/nutrition/plans", headers=headers)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        plans = response.json()
        print(f"  ✅ Found {len(plans)} nutrition plans")
    else:
        print(f"  ❌ Failed: {response.text}")

def test_health_assessment():
    print("\n🏥 Testing Health Assessment...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "age": 28,
        "gender": "male",
        "height": 175,
        "weight": 70,
        "bmi": 22.9,
        "medical_conditions": ["None"],
        "injuries": ["None"],
        "medications": ["None"],
        "allergies": ["peanuts", "lactose"],
        "sleep_hours": "7-8 hours",
        "stress_level": "Moderate",
        "water_intake": "6-8 glasses",
        "smoking": False,
        "alcohol": False,
        "fitness_level": "Beginner",
        "workout_frequency": "3-4 days",
        "workout_time": "Morning",
        "fitness_goal": "Weight Loss",
        "diet_type": "Vegetarian",
        "meal_prep_time": "30-60 mins",
        "cooking_skill": "Intermediate"
    }
    response = requests.post(f"{BASE_URL}/health/assessment", headers=headers, json=data)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print("  ✅ Health Assessment working")
    else:
        print(f"  ❌ Failed: {response.text}")

def test_progress_stats():
    print("\n📊 Testing Progress Stats...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/progress/stats", headers=headers)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"  ✅ Progress stats: Streak {stats.get('currentStreak', 0)} days")
    else:
        print(f"  ❌ Failed: {response.text}")

def test_aromi_chat():
    print("\n🤖 Testing AROMI Chat...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {"message": "Give me a quick home workout", "session_id": None}
    response = requests.post(f"{BASE_URL}/aromi/chat", headers=headers, json=data)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  ✅ AROMI response: {response.json()['response'][:50]}...")
    else:
        print(f"  ❌ Failed: {response.text}")

def test_youtube_search():
    print("\n🎥 Testing YouTube Search...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/youtube/search?exercise=push%20ups", headers=headers)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        videos = response.json()
        print(f"  ✅ Found {len(videos.get('videos', []))} videos")
    else:
        print(f"  ❌ Failed: {response.text}")

def run_all_tests():
    print("=" * 60)
    print("🔬 TESTING AROGYAMITRA BACKEND API")
    print("=" * 60)
    
    test_registration()
    test_login()
    
    if TOKEN:
        test_auth_me()
        test_workout_generate()
        test_workout_plans()
        test_nutrition_generate()
        test_nutrition_plans()
        test_health_assessment()
        test_progress_stats()
        test_aromi_chat()
        test_youtube_search()
    else:
        print("\n❌ Cannot proceed without authentication token")
    
    print("\n" + "=" * 60)
    print("✅ TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()