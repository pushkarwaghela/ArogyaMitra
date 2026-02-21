# backend/scripts/test_env.py
import os
from dotenv import load_dotenv
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

def test_environment():
    """Test if environment variables are loaded correctly"""
    print("=" * 50)
    print("🔧 Testing Environment Variables")
    print("=" * 50)
    
    # Test database
    print(f"\n📁 Database:")
    print(f"  DATABASE_URL: {settings.DATABASE_URL}")
    print(f"  SECRET_KEY: {'✅ Set' if settings.SECRET_KEY else '❌ Missing'}")
    
    # Test AI Services
    print(f"\n🤖 AI Services:")
    print(f"  GROQ_API_KEY: {'✅ Set' if settings.GROQ_API_KEY else '❌ Missing'}")
    print(f"  OPENAI_API_KEY: {'✅ Set' if settings.OPENAI_API_KEY else '❌ Missing'}")
    print(f"  GEMINI_API_KEY: {'✅ Set' if settings.GEMINI_API_KEY else '❌ Missing'}")
    
    # Test Google Services
    print(f"\n📅 Google Services:")
    print(f"  GOOGLE_CALENDAR_CLIENT_ID: {'✅ Set' if settings.GOOGLE_CALENDAR_CLIENT_ID else '❌ Missing'}")
    print(f"  GOOGLE_CALENDAR_CLIENT_SECRET: {'✅ Set' if settings.GOOGLE_CALENDAR_CLIENT_SECRET else '❌ Missing'}")
    print(f"  YOUTUBE_API_KEY: {'✅ Set' if settings.YOUTUBE_API_KEY else '❌ Missing'}")
    
    # Test CORS
    print(f"\n🌐 CORS Origins:")
    for origin in settings.get_cors_origins():
        print(f"  - {origin}")
    
    print("\n" + "=" * 50)
    
    # Summary
    all_keys = [
        settings.GROQ_API_KEY,
        settings.YOUTUBE_API_KEY,
        settings.GOOGLE_CALENDAR_CLIENT_ID
    ]
    
    if all(all_keys):
        print("✅ All required API keys are set!")
    else:
        print("⚠️ Some API keys are missing. Check your .env file")
    
    print("=" * 50)

if __name__ == "__main__":
    # Load .env file
    load_dotenv()
    test_environment()