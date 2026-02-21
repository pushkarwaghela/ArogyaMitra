# backend/app/api/v1/endpoints/progress.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.progress import ProgressRecord

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.get("/stats")
async def get_progress_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress statistics for current user"""
    # Return mock stats
    return {
        "current_streak": 7,
        "total_calories_burned": 2450,
        "total_workouts": 12,
        "completion_rate": 85,
        "weight_change": -2.5,
        "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "last_workout": datetime.now().isoformat()
    }

@router.get("/history")
async def get_progress_history(
    current_user: User = Depends(get_current_user),
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get progress history for the last N days"""
    # Generate mock history
    mock_history = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        mock_history.append({
            "date": date.strftime("%Y-%m-%d"),
            "weight": round(70 + (i * 0.1), 1),
            "workout_completed": i % 3 != 0,  # Every 3rd day rest
            "calories_burned": 300 if i % 3 != 0 else 0,
            "water_intake": 2000,
            "sleep_hours": 7.5
        })
    
    return mock_history

@router.post("/track")
async def track_progress(
    progress_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track daily progress"""
    # For now, just return the received data
    return {
        "message": "Progress tracked successfully",
        "data": progress_data,
        "user_id": current_user.id
    }

@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user achievements"""
    mock_achievements = [
        {
            "id": 1,
            "name": "First Workout",
            "description": "Completed your first workout",
            "achieved_at": (datetime.now() - timedelta(days=28)).isoformat(),
            "icon": "🏆"
        },
        {
            "id": 2,
            "name": "7-Day Streak",
            "description": "Worked out 7 days in a row",
            "achieved_at": (datetime.now() - timedelta(days=21)).isoformat(),
            "icon": "🔥"
        },
        {
            "id": 3,
            "name": "Weight Loss Milestone",
            "description": "Lost 2.5 kg",
            "achieved_at": (datetime.now() - timedelta(days=7)).isoformat(),
            "icon": "⭐"
        }
    ]
    
    return mock_achievements