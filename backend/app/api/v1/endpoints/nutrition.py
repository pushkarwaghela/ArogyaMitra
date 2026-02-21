# backend/app/api/v1/endpoints/nutrition.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.api.v1.dependencies import get_current_user

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])

# Pydantic models for nutrition
class MealPlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    calories: int
    meals: List[dict]
    dietary_restrictions: List[str] = []

class MealPlanCreate(MealPlanBase):
    pass

class MealPlanResponse(MealPlanBase):
    id: int
    user_id: int
    created_at: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[MealPlanResponse])
async def get_meal_plans(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all meal plans for current user"""
    return {"message": "Nutrition endpoint - Coming soon with Spoonacular API"}

@router.post("/generate", response_model=MealPlanResponse)
async def generate_meal_plan(
    preferences: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered meal plan based on user preferences and restrictions"""
    return {"message": "Meal plan generation - Coming soon"}