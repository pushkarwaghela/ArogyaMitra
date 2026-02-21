# backend/app/api/v1/endpoints/calendar.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from pydantic import BaseModel

from app.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.services.google_calendar_service import google_calendar_service
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/calendar", tags=["Google Calendar"])

class WorkoutSyncRequest(BaseModel):
    workout_plan_id: int
    start_date: str  # ISO format date

class EventResponse(BaseModel):
    event_id: str
    html_link: str
    summary: str
    start: str
    end: str

@router.get("/auth")
async def google_calendar_auth(
    current_user: User = Depends(get_current_user)
):
    """Get Google Calendar authorization URL"""
    auth_url = google_calendar_service.get_authorization_url(current_user.id)
    return {"auth_url": auth_url}

@router.get("/callback")
async def google_calendar_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback from Google"""
    user_id = int(state)
    success = await google_calendar_service.handle_oauth_callback(code, user_id)
    
    if success:
        return {"message": "Successfully connected to Google Calendar!"}
    else:
        raise HTTPException(status_code=400, detail="Failed to connect to Google Calendar")

@router.get("/status")
async def check_calendar_status(
    current_user: User = Depends(get_current_user)
):
    """Check Google Calendar connection status"""
    status = await google_calendar_service.check_calendar_connection(current_user.id)
    return status

@router.post("/sync-workout", response_model=List[EventResponse])
async def sync_workout_to_calendar(
    request: WorkoutSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync a workout plan to Google Calendar"""
    # Check connection first
    connection_status = await google_calendar_service.check_calendar_connection(current_user.id)
    if not connection_status.get('connected'):
        raise HTTPException(
            status_code=401,
            detail="Not connected to Google Calendar. Please connect first."
        )
    
    # Get workout plan
    workout_plan = await WorkoutService.get_workout_plan_by_id(db, request.workout_plan_id, current_user.id)
    if not workout_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    # Parse start date
    try:
        start_date = datetime.date.fromisoformat(request.start_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Convert workout plan to dict for calendar service
    plan_dict = {
        'weekly_schedule': []
    }
    
    # Get weekly schedules
    for schedule in workout_plan.weekly_schedules:
        exercises = []
        for exercise_instance in schedule.exercise_instances:
            exercises.append({
                'name': exercise_instance.exercise.name,
                'sets': exercise_instance.sets,
                'reps': exercise_instance.reps,
                'duration': exercise_instance.duration
            })
        
        plan_dict['weekly_schedule'].append({
            'workout_type': workout_plan.workout_type.value if workout_plan.workout_type else "Workout",
            'exercises': exercises,
            'duration': workout_plan.session_duration,
            'is_rest_day': schedule.is_rest_day,
            'start_hour': 7,  # Default to 7 AM
            'location': 'Home/Gym'
        })
    
    # Create calendar events
    events = await google_calendar_service.create_weekly_workout_schedule(
        user_id=current_user.id,
        workout_plan=plan_dict,
        start_date=start_date
    )
    
    return events

@router.get("/upcoming", response_model=List[EventResponse])
async def get_upcoming_workouts(
    max_results: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get upcoming workout events from calendar"""
    events = await google_calendar_service.get_upcoming_workouts(
        user_id=current_user.id,
        max_results=max_results
    )
    return events

@router.delete("/event/{event_id}")
async def delete_workout_event(
    event_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a workout event from calendar"""
    success = await google_calendar_service.delete_workout_event(
        user_id=current_user.id,
        event_id=event_id
    )
    
    if success:
        return {"message": "Event deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to delete event")