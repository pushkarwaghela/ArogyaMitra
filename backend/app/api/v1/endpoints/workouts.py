from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.workout import WorkoutPlan, Exercise, WeeklySchedule, ExerciseInstance
from app.services.ai_agent import arogya_mitra_agent
from app.services.youtube_service import youtube_service

router = APIRouter(prefix="/workouts", tags=["Workouts"])

@router.post("/generate")
async def generate_workout_plan(
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new AI-powered workout plan using Groq"""
    try:
        # Generate plan using AI agent with real Groq API
        ai_plan = await arogya_mitra_agent.generate_workout_plan(current_user, preferences)
        
        # Enhance with real YouTube videos
        if "weekly_schedule" in ai_plan:
            for day in ai_plan["weekly_schedule"]:
                for exercise in day.get("exercises", []):
                    # Get real YouTube videos
                    videos = await youtube_service.search_exercise_videos(
                        exercise_name=exercise.get("name", ""),
                        workout_type=preferences.get("workout_type"),
                        difficulty=preferences.get("difficulty", "beginner")
                    )
                    if videos:
                        exercise["video_url"] = videos[0].get("embed_url")
                        exercise["video_title"] = videos[0].get("title")
        
        # Create workout plan in database
        workout_plan = WorkoutPlan(
            user_id=current_user.id,
            title=ai_plan.get("title", "Personalized Workout Plan"),
            description=ai_plan.get("description", ""),
            workout_type=preferences.get("workout_type", "strength"),
            difficulty=preferences.get("difficulty", "beginner"),
            duration_weeks=preferences.get("duration_weeks", 4),
            sessions_per_week=preferences.get("days_per_week", 5),
            session_duration=preferences.get("session_duration", 45),
            is_active=True,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=preferences.get("duration_weeks", 4) * 7)
        )
        
        db.add(workout_plan)
        db.commit()
        db.refresh(workout_plan)
        
        # Store weekly schedule and exercises
        for day_data in ai_plan.get("weekly_schedule", []):
            weekly_schedule = WeeklySchedule(
                workout_plan_id=workout_plan.id,
                week_number=1,
                day_of_week=day_data.get("day_number", 0),
                is_rest_day=day_data.get("isRestDay", False)
            )
            db.add(weekly_schedule)
            db.flush()
            
            for exercise_data in day_data.get("exercises", []):
                # Find or create exercise
                exercise = db.query(Exercise).filter(
                    Exercise.name.ilike(f"%{exercise_data.get('name')}%")
                ).first()
                
                if not exercise:
                    exercise = Exercise(
                        name=exercise_data.get("name", ""),
                        description=exercise_data.get("description", ""),
                        muscle_group=exercise_data.get("muscleGroup", ""),
                        difficulty=exercise_data.get("difficulty", "beginner"),
                        video_url=exercise_data.get("video_url", ""),
                        calories_per_minute=exercise_data.get("calories_per_minute", 5)
                    )
                    db.add(exercise)
                    db.flush()
                
                exercise_instance = ExerciseInstance(
                    weekly_schedule_id=weekly_schedule.id,
                    exercise_id=exercise.id,
                    sets=exercise_data.get("sets", 3),
                    reps=exercise_data.get("reps", 10),
                    duration=exercise_data.get("duration"),
                    rest_time=exercise_data.get("rest_time", 60),
                    notes=exercise_data.get("notes")
                )
                db.add(exercise_instance)
        
        db.commit()
        
        return {
            "success": True,
            "plan_id": workout_plan.id,
            "message": "Workout plan generated successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plans")
async def get_workout_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workout plans for current user"""
    plans = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id
    ).order_by(WorkoutPlan.created_at.desc()).all()
    
    result = []
    for plan in plans:
        weekly_schedules = []
        for schedule in plan.weekly_schedules:
            exercises = []
            for instance in schedule.exercise_instances:
                exercises.append({
                    "id": instance.id,
                    "name": instance.exercise.name,
                    "sets": instance.sets,
                    "reps": instance.reps,
                    "duration": instance.duration,
                    "rest_time": instance.rest_time,
                    "video_url": instance.exercise.video_url,
                    "muscle_group": instance.exercise.muscle_group,
                    "calories_burn": instance.exercise.calories_per_minute * (instance.duration or 30) / 60
                })
            
            weekly_schedules.append({
                "day_number": schedule.day_of_week,
                "is_rest_day": schedule.is_rest_day,
                "exercises": exercises
            })
        
        result.append({
            "id": plan.id,
            "title": plan.title,
            "description": plan.description,
            "duration": plan.duration_weeks,
            "difficulty": plan.difficulty,
            "weekly_schedule": weekly_schedules,
            "created_at": plan.created_at.isoformat()
        })
    
    return result

@router.get("/active")
async def get_active_workout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active workout plan for current user"""
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == current_user.id,
        WorkoutPlan.is_active == True
    ).first()
    
    if not plan:
        return None
    
    weekly_schedules = []
    for schedule in plan.weekly_schedules:
        exercises = []
        for instance in schedule.exercise_instances:
            exercises.append({
                "id": instance.id,
                "name": instance.exercise.name,
                "sets": instance.sets,
                "reps": instance.reps,
                "duration": instance.duration,
                "rest_time": instance.rest_time,
                "video_url": instance.exercise.video_url
            })
        
        weekly_schedules.append({
            "day_number": schedule.day_of_week,
            "is_rest_day": schedule.is_rest_day,
            "exercises": exercises
        })
    
    return {
        "id": plan.id,
        "title": plan.title,
        "description": plan.description,
        "duration": plan.duration_weeks,
        "difficulty": plan.difficulty,
        "weekly_schedule": weekly_schedules
    }

@router.post("/{workout_id}/complete")
async def complete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a workout as complete"""
    workout = db.query(WorkoutPlan).filter(
        WorkoutPlan.id == workout_id,
        WorkoutPlan.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    workout.is_active = False
    workout.is_completed = True
    workout.end_date = datetime.now()
    
    db.commit()
    
    return {"success": True, "message": "Workout completed!"}