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

# Create FastAPI app
app = FastAPI(
    title="ArogyaMitra API",
    description="AI-Driven Workout Planning, Nutrition Guidance, and Health Coaching Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", '["http://localhost:3001"]')
app.add_middleware(
    CORSMiddleware,
    allow_origins=json.loads(cors_origins),
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