# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.v1 import router as api_router

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:5173", "http://127.0.0.1:3001"],
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