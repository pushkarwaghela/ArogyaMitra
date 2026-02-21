# backend/app/api/v1/__init__.py
"""API v1 package"""
from fastapi import APIRouter

# Create the router
router = APIRouter(prefix="/api/v1")

# Import endpoints
from .endpoints import auth
from .endpoints import users
from .endpoints import workouts
from .endpoints import nutrition
from .endpoints import progress
from .endpoints import analytics
from .endpoints import aromi
from .endpoints import ai_test  # Add this line
from .endpoints import youtube
from .endpoints import nutrition_api
from .endpoints import calendar


# Include routers
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(workouts.router)
router.include_router(nutrition.router)
router.include_router(progress.router)
router.include_router(analytics.router)
router.include_router(aromi.router)
router.include_router(ai_test.router)  # Add this line
router.include_router(youtube.router)
router.include_router(nutrition_api.router)
router.include_router(calendar.router)



__all__ = ["router"]