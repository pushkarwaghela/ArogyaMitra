# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.v1 import router as api_router
import json
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Get CORS origins from environment variable
cors_origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:3001"]')
try:
    cors_origins = json.loads(cors_origins_str)
except:
    cors_origins = ["http://localhost:3001"]

print(f"🌐 CORS Origins configured: {cors_origins}")  # This will show in Render logs

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to ArogyaMitra API",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "workouts": "/api/v1/workouts",
            "nutrition": "/api/v1/nutrition",
            "progress": "/api/v1/progress",
            "analytics": "/api/v1/analytics",
            "aromi": "/api/v1/aromi",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }