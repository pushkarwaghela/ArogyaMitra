# backend/test_password.py
from app.core.security import get_password_hash, verify_password

def test_password_hashing():
    print("Testing password hashing...")
    
    # Test password
    password = "Test@123456"
    
    # Hash the password
    hashed = get_password_hash(password)
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed}")
    
    # Verify the password
    is_valid = verify_password(password, hashed)
    print(f"Verification result: {is_valid}")
    
    # Test wrong password
    is_valid = verify_password("wrongpassword", hashed)
    print(f"Wrong password verification: {is_valid}")
    
    print("\n✅ Password hashing test complete!")

if __name__ == "__main__":
    test_password_hashing()