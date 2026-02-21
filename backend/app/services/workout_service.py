# backend/app/services/workout_service.py
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging
from app.models.user import User
from app.models.workout import WorkoutPlan, Exercise, WeeklySchedule, ExerciseInstance, DifficultyLevel, WorkoutType
from app.services.ai_agent import arogya_mitra_agent

logger = logging.getLogger(__name__)

class WorkoutService:
    
    @staticmethod
    async def generate_workout_plan(
        db: Session, 
        user: User, 
        preferences: Dict[str, Any]
    ) -> WorkoutPlan:
        """Generate and save a workout plan for user"""
        
        # Get AI-generated plan
        ai_plan = await arogya_mitra_agent.generate_workout_plan(user, preferences)
        
        # Create workout plan in database
        workout_plan = WorkoutPlan(
            user_id=user.id,
            title=ai_plan.get("title", "Personalized Workout Plan"),
            description=ai_plan.get("description", ""),
            workout_type=preferences.get("workout_type", WorkoutType.STRENGTH),
            difficulty=preferences.get("difficulty", DifficultyLevel.BEGINNER),
            duration_weeks=preferences.get("duration_weeks", 4),
            sessions_per_week=preferences.get("days_per_week", 5),
            session_duration=preferences.get("session_duration", 45),
            target_calories_burn=ai_plan.get("daily_calories_burn"),
            is_active=True,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=preferences.get("duration_weeks", 4) * 7)
        )
        
        db.add(workout_plan)
        db.flush()  # Get ID without committing
        
        # Create weekly schedules
        weekly_schedules = await WorkoutService._create_weekly_schedules(
            db, workout_plan, ai_plan.get("weekly_schedule", [])
        )
        
        db.commit()
        db.refresh(workout_plan)
        
        return workout_plan
    
    @staticmethod
    async def _create_weekly_schedules(
        db: Session, 
        workout_plan: WorkoutPlan, 
        schedule_data: List[Dict]
    ) -> List[WeeklySchedule]:
        """Create weekly schedules from AI plan"""
        weekly_schedules = []
        
        for week_data in schedule_data:
            week_number = week_data.get("week", 1)
            days = week_data.get("days", [])
            
            for day_data in days:
                day_of_week = day_data.get("day_of_week", 0)
                is_rest_day = day_data.get("is_rest_day", False)
                
                weekly_schedule = WeeklySchedule(
                    workout_plan_id=workout_plan.id,
                    week_number=week_number,
                    day_of_week=day_of_week,
                    is_rest_day=is_rest_day
                )
                db.add(weekly_schedule)
                db.flush()
                
                # Create exercise instances
                if not is_rest_day:
                    exercises = day_data.get("exercises", [])
                    await WorkoutService._create_exercise_instances(
                        db, weekly_schedule, exercises
                    )
                
                weekly_schedules.append(weekly_schedule)
        
        return weekly_schedules
    
    @staticmethod
    async def _create_exercise_instances(
        db: Session, 
        weekly_schedule: WeeklySchedule, 
        exercises: List[Dict]
    ):
        """Create exercise instances for a schedule"""
        for exercise_data in exercises:
            # Find or create exercise
            exercise = await WorkoutService._get_or_create_exercise(db, exercise_data)
            
            exercise_instance = ExerciseInstance(
                weekly_schedule_id=weekly_schedule.id,
                exercise_id=exercise.id,
                sets=exercise_data.get("sets", 3),
                reps=exercise_data.get("reps"),
                duration=exercise_data.get("duration"),
                rest_time=exercise_data.get("rest_time", 60),
                weight=exercise_data.get("weight"),
                notes=exercise_data.get("notes")
            )
            db.add(exercise_instance)
    
    @staticmethod
    async def _get_or_create_exercise(db: Session, exercise_data: Dict) -> Exercise:
        """Get existing exercise or create new one"""
        exercise_name = exercise_data.get("name", "").strip()
        
        # Try to find existing exercise
        exercise = db.query(Exercise).filter(
            Exercise.name.ilike(f"%{exercise_name}%")
        ).first()
        
        if not exercise:
            # Create new exercise
            exercise = Exercise(
                name=exercise_name,
                description=exercise_data.get("description", ""),
                muscle_group=exercise_data.get("muscle_group"),
                equipment_needed=json.dumps(exercise_data.get("equipment", [])),
                difficulty=exercise_data.get("difficulty", DifficultyLevel.BEGINNER),
                workout_type=exercise_data.get("workout_type"),
                video_url=exercise_data.get("video_url"),
                instructions=exercise_data.get("instructions"),
                calories_per_minute=exercise_data.get("calories_per_minute")
            )
            db.add(exercise)
            db.flush()
        
        return exercise
    
    @staticmethod
    async def get_user_workout_plans(db: Session, user_id: int) -> List[WorkoutPlan]:
        """Get all workout plans for a user"""
        return db.query(WorkoutPlan).filter(
            WorkoutPlan.user_id == user_id
        ).order_by(WorkoutPlan.created_at.desc()).all()
    
    @staticmethod
    async def get_active_workout_plan(db: Session, user_id: int) -> Optional[WorkoutPlan]:
        """Get active workout plan for user"""
        return db.query(WorkoutPlan).filter(
            WorkoutPlan.user_id == user_id,
            WorkoutPlan.is_active == True
        ).first()
    
    @staticmethod
    async def mark_exercise_completed(
        db: Session, 
        exercise_instance_id: int, 
        actual_data: Dict
    ) -> Optional[ExerciseInstance]:
        """Mark an exercise as completed with actual data"""
        exercise_instance = db.query(ExerciseInstance).filter(
            ExerciseInstance.id == exercise_instance_id
        ).first()
        
        if exercise_instance:
            exercise_instance.is_completed = True
            exercise_instance.actual_sets = actual_data.get("sets")
            exercise_instance.actual_reps = actual_data.get("reps")
            exercise_instance.actual_duration = actual_data.get("duration")
            exercise_instance.actual_weight = actual_data.get("weight")
            exercise_instance.completion_date = datetime.now()
            
            db.commit()
            db.refresh(exercise_instance)
        
        return exercise_instance
    
    @staticmethod
    async def adjust_workout_plan(
        db: Session,
        plan_id: int,
        adjustment_type: str,
        details: Dict
    ) -> Optional[WorkoutPlan]:
        """Dynamically adjust workout plan"""
        workout_plan = db.query(WorkoutPlan).filter(
            WorkoutPlan.id == plan_id
        ).first()
        
        if not workout_plan:
            return None
        
        # Get current plan as dict
        plan_dict = {
            "id": workout_plan.id,
            "title": workout_plan.title,
            "description": workout_plan.description,
            "weekly_schedule": []  # Would need to fetch related data
        }
        
        # Adjust using AI agent
        adjusted_plan = await arogya_mitra_agent.adjust_plan_dynamically(
            workout_plan.user, plan_dict, adjustment_type, details
        )
        
        # Update plan with adjustments
        workout_plan.title = adjusted_plan.get("title", workout_plan.title)
        workout_plan.description = adjusted_plan.get("description", workout_plan.description)
        
        db.commit()
        db.refresh(workout_plan)
        
        return workout_plan
    
    # Add this method to WorkoutService class
    @staticmethod
    async def sync_workout_to_calendar(
        db: Session,
        user_id: int,
        workout_plan_id: int,
        start_date: datetime.date
    ) -> Dict[str, Any]:
        """Sync a workout plan to Google Calendar"""
        from app.services.google_calendar_service import google_calendar_service

        # Get workout plan with all related data
        workout_plan = db.query(WorkoutPlan).filter(
            WorkoutPlan.id == workout_plan_id,
            WorkoutPlan.user_id == user_id
        ).first()

        if not workout_plan:
            raise HTTPException(status_code=404, detail="Workout plan not found")

        # Convert to dict format for calendar service
        plan_dict = {
            'weekly_schedule': []
        }

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
                'start_hour': 7,
                'location': 'Home/Gym'
            })

        # Create calendar events
        events = await google_calendar_service.create_weekly_workout_schedule(
            user_id=user_id,
            workout_plan=plan_dict,
            start_date=start_date
        )

        return {
            'workout_plan_id': workout_plan_id,
            'events_created': len(events),
            'events': events
        }