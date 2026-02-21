# backend/test_db.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.models.user import User
from sqlalchemy import text

def test_database():
    print("=" * 60)
    print("🔬 Testing Database Connection")
    print("=" * 60)
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    try:
        # Check if users table exists
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
            if result.fetchone():
                print("✅ Users table exists")
            else:
                print("❌ Users table does not exist")
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
    
    try:
        # Try to create a test user directly
        db = SessionLocal()
        test_user = User(
            email="debug@example.com",
            username="debuguser",
            full_name="Debug User",
            hashed_password="dummy_hash"
        )
        db.add(test_user)
        db.commit()
        print("✅ Able to create user directly in database")
        db.rollback()  # Rollback to not keep the test user
    except Exception as e:
        print(f"❌ Failed to create user: {e}")
    finally:
        db.close()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_database()