from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.progress import ProgressRecord, Achievement
from app.services.ai_agent import arogya_mitra_agent

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.post("/track")
async def track_progress(
    progress_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track daily progress"""
    progress = ProgressRecord(
        user_id=current_user.id,
        record_date=datetime.now(),
        weight=progress_data.get("weight"),
        calories_burned=progress_data.get("calories_burned"),
        workout_completed=progress_data.get("workout_completed", False),
        workout_duration=progress_data.get("workout_duration"),
        water_intake=progress_data.get("water_intake"),
        sleep_hours=progress_data.get("sleep_hours"),
        mood=progress_data.get("mood"),
        notes=progress_data.get("notes")
    )
    
    db.add(progress)
    db.commit()
    
    return {"success": True, "message": "Progress tracked successfully"}

@router.get("/stats")
async def get_progress_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress statistics for current user"""
    # Get all progress records
    records = db.query(ProgressRecord).filter(
        ProgressRecord.user_id == current_user.id
    ).order_by(ProgressRecord.record_date.desc()).all()
    
    if not records:
        return {
            "currentStreak": 0,
            "totalWorkouts": 0,
            "totalCaloriesBurned": 0,
            "completionRate": 0,
            "weightChange": 0,
            "avgWorkoutDuration": 0
        }
    
    # Calculate stats
    total_workouts = sum(1 for r in records if r.workout_completed)
    total_calories = sum(r.calories_burned or 0 for r in records)
    avg_duration = sum(r.workout_duration or 0 for r in records) / total_workouts if total_workouts > 0 else 0
    
    # Calculate streak
    streak = 0
    for record in records:
        if record.workout_completed:
            streak += 1
        else:
            break
    
    # Calculate weight change
    weight_change = 0
    if len(records) >= 2 and records[-1].weight and records[0].weight:
        weight_change = records[0].weight - records[-1].weight
    
    return {
        "currentStreak": streak,
        "totalWorkouts": total_workouts,
        "totalCaloriesBurned": total_calories,
        "completionRate": round((total_workouts / 30) * 100 if total_workouts > 0 else 0, 1),
        "weightChange": round(weight_change, 1),
        "avgWorkoutDuration": round(avg_duration, 1)
    }

@router.get("/history")
async def get_progress_history(
    period: str = "month",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress history for charts"""
    # Calculate date range
    end_date = datetime.now()
    if period == "week":
        start_date = end_date - timedelta(days=7)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "3months":
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=30)
    
    records = db.query(ProgressRecord).filter(
        ProgressRecord.user_id == current_user.id,
        ProgressRecord.record_date >= start_date
    ).order_by(ProgressRecord.record_date.asc()).all()
    
    history = []
    for record in records:
        history.append({
            "date": record.record_date.strftime("%Y-%m-%d"),
            "weight": record.weight,
            "calories": record.calories_burned,
            "workouts": 1 if record.workout_completed else 0,
            "water": record.water_intake,
            "sleep": record.sleep_hours,
            "mood": record.mood
        })
    
    return history

@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user achievements"""
    achievements = db.query(Achievement).filter(
        Achievement.user_id == current_user.id
    ).order_by(Achievement.achieved_at.desc()).all()
    
    return achievements