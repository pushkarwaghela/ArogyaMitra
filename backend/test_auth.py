# backend/test_auth.py
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_register():
    print("\n📝 Testing User Registration...")
    
    user_data = {
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
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Registration successful!")
            print(f"Access Token: {data['access_token'][:20]}...")
            return data
        else:
            print("❌ Registration failed:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Raw response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return None

def test_login():
    print("\n🔐 Testing User Login...")
    
    login_data = {
        "username": "testuser",
        "password": "Test@123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/json", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Access Token: {data['access_token'][:20]}...")
            return data
        else:
            print("❌ Login failed:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Raw response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return None

def test_get_current_user(token):
    print("\n👤 Testing Get Current User...")
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print("✅ Got user info:")
            print(f"  Username: {user['username']}")
            print(f"  Email: {user['email']}")
            print(f"  Full Name: {user['full_name']}")
            return user
        else:
            print("❌ Failed to get user info:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Raw response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return None

def test_refresh_token(refresh_token):
    print("\n🔄 Testing Token Refresh...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh", 
                                json={"refresh_token": refresh_token})
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Token refresh successful!")
            print(f"New Access Token: {data['access_token'][:20]}...")
            return data
        else:
            print("❌ Token refresh failed:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Raw response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return None

def run_all_tests():
    print("=" * 60)
    print("🔬 Testing ArogyaMitra Authentication API")
    print("=" * 60)
    
    # Test registration
    reg_result = test_register()
    
    # Test login
    login_result = test_login()
    
    if login_result:
        # Test get current user
        test_get_current_user(login_result["access_token"])
        
        # Test refresh token
        refresh_result = test_refresh_token(login_result["refresh_token"])
        
        if refresh_result:
            # Test with new token
            test_get_current_user(refresh_result["access_token"])
    
    print("\n" + "=" * 60)
    print("✅ Authentication tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()