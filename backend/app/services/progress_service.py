# backend/app/services/progress_service.py
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date

from app.models.user import User
from app.models.progress import ProgressRecord, Achievement
from app.services.ai_agent import arogya_mitra_agent
import logging

logger = logging.getLogger(__name__)

class ProgressService:
    
    @staticmethod
    async def record_progress(
        db: Session,
        user_id: int,
        progress_data: Dict[str, Any]
    ) -> ProgressRecord:
        """Record daily progress"""
        
        progress_record = ProgressRecord(
            user_id=user_id,
            record_date=progress_data.get("date", datetime.now()),
            weight=progress_data.get("weight"),
            body_fat_percentage=progress_data.get("body_fat_percentage"),
            muscle_mass=progress_data.get("muscle_mass"),
            waist_circumference=progress_data.get("waist_circumference"),
            hip_circumference=progress_data.get("hip_circumference"),
            chest_circumference=progress_data.get("chest_circumference"),
            arm_circumference=progress_data.get("arm_circumference"),
            thigh_circumference=progress_data.get("thigh_circumference"),
            strength_score=progress_data.get("strength_score"),
            endurance_score=progress_data.get("endurance_score"),
            flexibility_score=progress_data.get("flexibility_score"),
            steps_taken=progress_data.get("steps_taken"),
            calories_consumed=progress_data.get("calories_consumed"),
            calories_burned=progress_data.get("calories_burned"),
            water_intake=progress_data.get("water_intake"),
            sleep_hours=progress_data.get("sleep_hours"),
            mood=progress_data.get("mood"),
            energy_level=progress_data.get("energy_level"),
            stress_level=progress_data.get("stress_level"),
            workout_completed=progress_data.get("workout_completed", False),
            workout_duration=progress_data.get("workout_duration"),
            workout_intensity=progress_data.get("workout_intensity"),
            notes=progress_data.get("notes")
        )
        
        db.add(progress_record)
        db.commit()
        db.refresh(progress_record)
        
        # Check for achievements
        await ProgressService._check_achievements(db, user_id)
        
        return progress_record
    
    @staticmethod
    async def get_user_progress(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> List[ProgressRecord]:
        """Get user progress for last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return db.query(ProgressRecord).filter(
            ProgressRecord.user_id == user_id,
            ProgressRecord.record_date >= cutoff_date
        ).order_by(ProgressRecord.record_date.desc()).all()
    
    @staticmethod
    async def get_progress_insights(
        db: Session,
        user: User
    ) -> Dict[str, Any]:
        """Get AI-powered insights from user progress"""
        
        # Get recent progress records
        progress_records = await ProgressService.get_user_progress(db, user.id, 30)
        
        # Get insights from AI agent
        insights = await arogya_mitra_agent.analyze_progress(user, progress_records)
        
        return insights
    
    @staticmethod
    async def _check_achievements(db: Session, user_id: int):
        """Check and award achievements based on progress"""
        
        # Get user's progress
        progress_records = db.query(ProgressRecord).filter(
            ProgressRecord.user_id == user_id
        ).order_by(ProgressRecord.record_date).all()
        
        if not progress_records:
            return
        
        # Check for first workout
        first_workout = next((r for r in progress_records if r.workout_completed), None)
        if first_workout and not db.query(Achievement).filter(
            Achievement.user_id == user_id,
            Achievement.name == "First Workout"
        ).first():
            achievement = Achievement(
                user_id=user_id,
                name="First Workout",
                description="Completed your first workout!",
                category="workout",
                criteria_type="first_workout"
            )
            db.add(achievement)
        
        # Check for workout streak
        streak = 0
        for record in sorted(progress_records, key=lambda r: r.record_date, reverse=True):
            if record.workout_completed:
                streak += 1
            else:
                break
        
        if streak >= 7 and not db.query(Achievement).filter(
            Achievement.user_id == user_id,
            Achievement.name == "7-Day Streak"
        ).first():
            achievement = Achievement(
                user_id=user_id,
                name="7-Day Streak",
                description="Worked out 7 days in a row!",
                category="streak",
                criteria_type="workout_streak",
                criteria_value="7"
            )
            db.add(achievement)
        
        if streak >= 30 and not db.query(Achievement).filter(
            Achievement.user_id == user_id,
            Achievement.name == "30-Day Streak"
        ).first():
            achievement = Achievement(
                user_id=user_id,
                name="30-Day Streak",
                description="Worked out 30 days in a row! Amazing dedication!",
                category="streak",
                criteria_type="workout_streak",
                criteria_value="30"
            )
            db.add(achievement)
        
        # Check for weight loss milestone
        if len(progress_records) >= 2:
            first_weight = progress_records[0].weight
            latest_weight = progress_records[-1].weight
            
            if first_weight and latest_weight:
                weight_loss = first_weight - latest_weight
                if weight_loss >= 5 and not db.query(Achievement).filter(
                    Achievement.user_id == user_id,
                    Achievement.name == "5kg Weight Loss"
                ).first():
                    achievement = Achievement(
                        user_id=user_id,
                        name="5kg Weight Loss",
                        description="Lost 5kg on your fitness journey!",
                        category="milestone",
                        criteria_type="weight_loss",
                        criteria_value="5"
                    )
                    db.add(achievement)
        
        db.commit()
    
    @staticmethod
    async def get_user_achievements(db: Session, user_id: int) -> List[Achievement]:
        """Get all achievements for a user"""
        return db.query(Achievement).filter(
            Achievement.user_id == user_id
        ).order_by(Achievement.achieved_at.desc()).all()
    
    @staticmethod
    async def get_progress_summary(db: Session, user_id: int) -> Dict[str, Any]:
        """Get summary statistics of user progress"""
        
        progress_records = await ProgressService.get_user_progress(db, user_id, 30)
        
        if not progress_records:
            return {
                "message": "No progress data available",
                "total_workouts": 0,
                "total_calories_burned": 0
            }
        
        # Calculate statistics
        total_workouts = sum(1 for r in progress_records if r.workout_completed)
        total_calories_burned = sum(r.calories_burned or 0 for r in progress_records)
        avg_workout_duration = sum(r.workout_duration or 0 for r in progress_records) / total_workouts if total_workouts > 0 else 0
        
        # Weight trend
        weights = [r.weight for r in progress_records if r.weight]
        weight_change = None
        if len(weights) >= 2:
            weight_change = weights[-1] - weights[0]
        
        return {
            "period": "30 days",
            "total_workouts": total_workouts,
            "total_calories_burned": total_calories_burned,
            "average_workout_duration": round(avg_workout_duration, 1),
            "weight_change": round(weight_change, 1) if weight_change else None,
            "current_streak": ProgressService._calculate_streak(progress_records)
        }
    
    @staticmethod
    def _calculate_streak(records: List[ProgressRecord]) -> int:
        """Calculate current workout streak"""
        sorted_records = sorted(records, key=lambda r: r.record_date, reverse=True)
        
        streak = 0
        for record in sorted_records:
            if record.workout_completed:
                streak += 1
            else:
                break
        
        return streak