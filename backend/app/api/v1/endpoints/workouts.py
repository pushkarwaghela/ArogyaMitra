# backend/app/api/v1/endpoints/workouts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.workout import WorkoutPlan, WeeklySchedule, ExerciseInstance

router = APIRouter(prefix="/workouts", tags=["Workouts"])

@router.get("/active")
async def get_active_workout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active workout plan for current user"""
    workout_plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).first()
    
    if not workout_plan:
        # Return mock data for now
        return {
            "id": 1,
            "title": "4-Week Weight Loss Challenge",
            "description": "A comprehensive plan to kickstart your weight loss journey",
            "workout_type": "strength",
            "difficulty": "intermediate",
            "sessions_per_week": 5,
            "session_duration": 45,
            "is_active": True
        }
    
    return workout_plan

@router.get("/upcoming")
async def get_upcoming_workouts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming workouts for the week"""
    # Get current date
    today = datetime.now().date()
    
    # Calculate days of week
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    current_day_index = today.weekday()
    
    # Return mock upcoming workouts
    mock_workouts = [
        {
            "id": 1,
            "title": "Full Body Strength",
            "day": days[current_day_index],
            "time": "7:00 AM",
            "duration": 45,
            "exercises": 6,
            "completed": False
        },
        {
            "id": 2,
            "title": "Cardio HIIT",
            "day": days[(current_day_index + 1) % 7],
            "time": "6:30 AM",
            "duration": 30,
            "exercises": 8,
            "completed": False
        },
        {
            "id": 3,
            "title": "Upper Body Focus",
            "day": days[(current_day_index + 2) % 7],
            "time": "7:00 AM",
            "duration": 45,
            "exercises": 5,
            "completed": False
        }
    ]
    
    return mock_workouts

@router.get("/history")
async def get_workout_history(
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get workout history"""
    # Return mock history
    mock_history = [
        {
            "id": 1,
            "date": "2026-02-20",
            "title": "Full Body Strength",
            "duration": 45,
            "calories_burned": 320,
            "exercises_completed": 6
        },
        {
            "id": 2,
            "date": "2026-02-19",
            "title": "Cardio HIIT",
            "duration": 30,
            "calories_burned": 280,
            "exercises_completed": 8
        },
        {
            "id": 3,
            "date": "2026-02-18",
            "title": "Upper Body Focus",
            "duration": 45,
            "calories_burned": 300,
            "exercises_completed": 5
        }
    ]
    
    return mock_history