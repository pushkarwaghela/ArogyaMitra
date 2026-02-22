from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json

from app.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.health import HealthAssessment as HealthAssessmentModel

router = APIRouter(prefix="/health", tags=["Health"])

@router.post("/assessment")
async def submit_health_assessment(
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit health assessment data"""
    try:
        # Check if user already has a health assessment
        existing = db.query(HealthAssessmentModel).filter(
            HealthAssessmentModel.user_id == current_user.id
        ).first()

        if existing:
            # Update existing assessment
            existing.age = assessment_data.get("age", existing.age)
            existing.gender = assessment_data.get("gender", existing.gender)
            existing.height = assessment_data.get("height", existing.height)
            existing.weight = assessment_data.get("weight", existing.weight)
            existing.bmi = assessment_data.get("bmi", existing.bmi)
            existing.medical_conditions = json.dumps(assessment_data.get("medical_conditions", []))
            existing.injuries = json.dumps(assessment_data.get("injuries", []))
            existing.medications = json.dumps(assessment_data.get("medications", []))
            existing.allergies = json.dumps(assessment_data.get("allergies", []))
            existing.sleep_hours = assessment_data.get("sleep_hours")
            existing.stress_level = assessment_data.get("stress_level")
            existing.water_intake = assessment_data.get("water_intake")
            existing.smoking = assessment_data.get("smoking", False)
            existing.alcohol = assessment_data.get("alcohol", False)
            existing.fitness_level = assessment_data.get("fitness_level")
            existing.workout_frequency = assessment_data.get("workout_frequency")
            existing.preferred_workout_time = assessment_data.get("workout_time")
            existing.fitness_goal = assessment_data.get("fitness_goal")
            existing.diet_type = assessment_data.get("diet_type")
            existing.meal_prep_time = assessment_data.get("meal_prep_time")
            existing.cooking_skill = assessment_data.get("cooking_skill")
            existing.updated_at = datetime.now()
        else:
            # Create new assessment
            assessment = HealthAssessmentModel(
                user_id=current_user.id,
                age=assessment_data.get("age"),
                gender=assessment_data.get("gender"),
                height=assessment_data.get("height"),
                weight=assessment_data.get("weight"),
                bmi=assessment_data.get("bmi"),
                medical_conditions=json.dumps(assessment_data.get("medical_conditions", [])),
                injuries=json.dumps(assessment_data.get("injuries", [])),
                medications=json.dumps(assessment_data.get("medications", [])),
                allergies=json.dumps(assessment_data.get("allergies", [])),
                sleep_hours=assessment_data.get("sleep_hours"),
                stress_level=assessment_data.get("stress_level"),
                water_intake=assessment_data.get("water_intake"),
                smoking=assessment_data.get("smoking", False),
                alcohol=assessment_data.get("alcohol", False),
                fitness_level=assessment_data.get("fitness_level"),
                workout_frequency=assessment_data.get("workout_frequency"),
                preferred_workout_time=assessment_data.get("workout_time"),
                fitness_goal=assessment_data.get("fitness_goal"),
                diet_type=assessment_data.get("diet_type"),
                meal_prep_time=assessment_data.get("meal_prep_time"),
                cooking_skill=assessment_data.get("cooking_skill")
            )
            db.add(assessment)

        db.commit()
        
        return {"success": True, "message": "Health assessment saved successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assessment")
async def get_health_assessment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's health assessment"""
    assessment = db.query(HealthAssessmentModel).filter(
        HealthAssessmentModel.user_id == current_user.id
    ).first()

    if not assessment:
        return None

    return {
        "age": assessment.age,
        "gender": assessment.gender,
        "height": assessment.height,
        "weight": assessment.weight,
        "bmi": assessment.bmi,
        "medical_conditions": json.loads(assessment.medical_conditions) if assessment.medical_conditions else [],
        "injuries": json.loads(assessment.injuries) if assessment.injuries else [],
        "medications": json.loads(assessment.medications) if assessment.medications else [],
        "allergies": json.loads(assessment.allergies) if assessment.allergies else [],
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