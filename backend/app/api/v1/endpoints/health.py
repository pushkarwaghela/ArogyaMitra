from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json
import logging
import re

from app.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.health import HealthAssessment as HealthAssessmentModel

router = APIRouter(prefix="/health", tags=["Health"])
logger = logging.getLogger(__name__)

def extract_number(value):
    """Extract first number from a string, or return the value if it's already a number"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Extract first number from string (e.g., "7-8 hours" -> 7.5)
        match = re.search(r'(\d+(?:\.\d+)?)', value)
        if match:
            return float(match.group(1))
        # Try to parse common ranges
        if '-' in value:
            parts = value.split('-')
            if len(parts) == 2:
                try:
                    low = float(re.search(r'\d+', parts[0]).group())
                    high = float(re.search(r'\d+', parts[1]).group())
                    return (low + high) / 2
                except:
                    pass
    return None

@router.post("/assessment")
async def submit_health_assessment(
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit health assessment data"""
    try:
        logger.info(f"Received health assessment for user {current_user.id}")
        
        # Check if user already has a health assessment
        existing = db.query(HealthAssessmentModel).filter(
            HealthAssessmentModel.user_id == current_user.id
        ).first()

        # Helper function to safely get values
        def get_value(key, default=None):
            return assessment_data.get(key, default)

        # Helper function to handle lists/arrays
        def get_list_value(key):
            value = assessment_data.get(key, [])
            if isinstance(value, list):
                return json.dumps(value)
            return json.dumps([])

        # Extract numeric values from strings
        sleep_value = extract_number(get_value("sleep_hours"))
        water_value = extract_number(get_value("water_intake"))

        if existing:
            # Update existing assessment
            existing.age = get_value("age")
            existing.gender = get_value("gender")
            existing.height = get_value("height")
            existing.weight = get_value("weight")
            existing.bmi = get_value("bmi")
            existing.medical_conditions = get_list_value("medical_conditions")
            existing.injuries = get_list_value("injuries")
            existing.medications = get_list_value("medications")
            existing.allergies = get_list_value("allergies")
            existing.sleep_hours = sleep_value
            existing.stress_level = get_value("stress_level")
            existing.water_intake = water_value
            existing.smoking = get_value("smoking", False)
            existing.alcohol = get_value("alcohol", False)
            existing.fitness_level = get_value("fitness_level")
            existing.workout_frequency = get_value("workout_frequency")
            existing.preferred_workout_time = get_value("workout_time")
            existing.fitness_goal = get_value("fitness_goal")
            existing.diet_type = get_value("diet_type")
            existing.meal_prep_time = get_value("meal_prep_time")
            existing.cooking_skill = get_value("cooking_skill")
            existing.updated_at = datetime.now()
            logger.info(f"Updated existing health assessment for user {current_user.id}")
        else:
            # Create new assessment
            assessment = HealthAssessmentModel(
                user_id=current_user.id,
                age=get_value("age"),
                gender=get_value("gender"),
                height=get_value("height"),
                weight=get_value("weight"),
                bmi=get_value("bmi"),
                medical_conditions=get_list_value("medical_conditions"),
                injuries=get_list_value("injuries"),
                medications=get_list_value("medications"),
                allergies=get_list_value("allergies"),
                sleep_hours=sleep_value,
                stress_level=get_value("stress_level"),
                water_intake=water_value,
                smoking=get_value("smoking", False),
                alcohol=get_value("alcohol", False),
                fitness_level=get_value("fitness_level"),
                workout_frequency=get_value("workout_frequency"),
                preferred_workout_time=get_value("workout_time"),
                fitness_goal=get_value("fitness_goal"),
                diet_type=get_value("diet_type"),
                meal_prep_time=get_value("meal_prep_time"),
                cooking_skill=get_value("cooking_skill")
            )
            db.add(assessment)
            logger.info(f"Created new health assessment for user {current_user.id}")

        db.commit()
        
        return {"success": True, "message": "Health assessment saved successfully"}

    except Exception as e:
        db.rollback()
        logger.error(f"Error saving health assessment: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assessment")
async def get_health_assessment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's health assessment"""
    try:
        assessment = db.query(HealthAssessmentModel).filter(
            HealthAssessmentModel.user_id == current_user.id
        ).first()

        if not assessment:
            return None

        def parse_json_field(field):
            if field:
                try:
                    return json.loads(field)
                except:
                    return []
            return []

        return {
            "age": assessment.age,
            "gender": assessment.gender,
            "height": assessment.height,
            "weight": assessment.weight,
            "bmi": assessment.bmi,
            "medical_conditions": parse_json_field(assessment.medical_conditions),
            "injuries": parse_json_field(assessment.injuries),
            "medications": parse_json_field(assessment.medications),
            "allergies": parse_json_field(assessment.allergies),
            "sleep_hours": assessment.sleep_hours,
            "stress_level": assessment.stress_level,
            "water_intake": assessment.water_intake,
            "smoking": assessment.smoking,
            "alcohol": assessment.alcohol,
            "fitness_level": assessment.fitness_level,
            "workout_frequency": assessment.workout_frequency,
            "preferred_workout_time": assessment.preferred_workout_time,
            "fitness_goal": assessment.fitness_goal,
            "diet_type": assessment.diet_type,
            "meal_prep_time": assessment.meal_prep_time,
            "cooking_skill": assessment.cooking_skill
        }
    except Exception as e:
        logger.error(f"Error fetching health assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))