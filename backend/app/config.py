# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List
import json
import os
from dotenv import load_dotenv

# Force load .env file
load_dotenv(override=True)

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./arogyamitra.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "arogyamitra-super-secret-key-2024-fitness-ai")
    
    # App Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: List[str] = ["http://localhost:3001", "http://localhost:5173", "http://127.0.0.1:3001"]
    
    # Security
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # AI Services
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Google Services
    GOOGLE_CALENDAR_CLIENT_ID: str = os.getenv("GOOGLE_CALENDAR_CLIENT_ID", "")
    GOOGLE_CALENDAR_CLIENT_SECRET: str = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET", "")
    GOOGLE_CALENDAR_REDIRECT_URI: str = os.getenv("GOOGLE_CALENDAR_REDIRECT_URI", "http://localhost:8000/api/v1/calendar/callback")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    
    # Spoonacular API
    SPOONACULAR_API_KEY: str = os.getenv("SPOONACULAR_API_KEY", "")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields

# Create global settings object
settings = Settings()

# Print loaded settings for debugging (remove in production)
print(f"✅ Loaded Google Calendar Client ID: {settings.GOOGLE_CALENDAR_CLIENT_ID[:20]}...")