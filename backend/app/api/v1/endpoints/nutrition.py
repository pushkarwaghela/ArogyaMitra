from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.models.nutrition import NutritionPlan, Meal, DailyMealPlan, DailyMealInstance
from app.services.ai_agent import arogya_mitra_agent
from app.services.spoonacular_service import spoonacular_service

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])

@router.post("/generate")
async def generate_nutrition_plan(
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new AI-powered nutrition plan using Spoonacular"""
    try:
        # Get real meal plan from Spoonacular
        calorie_target = preferences.get("calorieTarget", 2000)
        diet = current_user.diet_preference.value if current_user.diet_preference else "vegetarian"
        
        spoonacular_plan = await spoonacular_service.generate_meal_plan(
            target_calories=calorie_target,
            diet=diet,
            exclude=current_user.allergies,
            time_frame="day"
        )
        
        # Create nutrition plan in database
        nutrition_plan = NutritionPlan(
            user_id=current_user.id,
            title=f"Personalized {diet.capitalize()} Meal Plan",
            description=f"{calorie_target} calorie meal plan based on your preferences",
            diet_preference=current_user.diet_preference,
            target_calories=calorie_target,
            duration_days=preferences.get("duration_days", 7),
            is_active=True,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=preferences.get("duration_days", 7))
        )
        
        db.add(nutrition_plan)
        db.commit()
        db.refresh(nutrition_plan)
        
        # Create daily meal plan
        daily_plan = DailyMealPlan(
            nutrition_plan_id=nutrition_plan.id,
            day_number=1,
            total_calories=spoonacular_plan.get("nutrients", {}).get("calories", calorie_target),
            total_protein=spoonacular_plan.get("nutrients", {}).get("protein", 0),
            total_carbs=spoonacular_plan.get("nutrients", {}).get("carbohydrates", 0),
            total_fats=spoonacular_plan.get("nutrients", {}).get("fat", 0)
        )
        db.add(daily_plan)
        db.flush()
        
        # Add meals
        meals_data = spoonacular_plan.get("meals", {})
        for meal_type, meal_data in meals_data.items():
            # Get or create meal
            meal = db.query(Meal).filter(
                Meal.name.ilike(f"%{meal_data.get('title', '')}%")
            ).first()
            
            if not meal:
                meal = Meal(
                    name=meal_data.get("title", ""),
                    description=meal_data.get("description", ""),
                    meal_type=meal_type,
                    calories=meal_data.get("nutrition", {}).get("nutrients", [{}])[0].get("amount", 0),
                    protein=0,
                    carbs=0,
                    fats=0,
                    ingredients=json.dumps(meal_data.get("ingredients", [])),
                    instructions=meal_data.get("instructions", ""),
                    prep_time=meal_data.get("readyInMinutes", 30),
                    image_url=meal_data.get("image", "")
                )
                db.add(meal)
                db.flush()
            
            meal_instance = DailyMealInstance(
                daily_meal_plan_id=daily_plan.id,
                meal_id=meal.id,
                meal_type=meal_type,
                time_of_day="08:00" if meal_type == "breakfast" else "13:00" if meal_type == "lunch" else "20:00"
            )
            db.add(meal_instance)
        
        db.commit()
        
        return {
            "success": True,
            "plan_id": nutrition_plan.id,
            "message": "Nutrition plan generated successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plans")
async def get_nutrition_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all nutrition plans for current user"""
    plans = db.query(NutritionPlan).filter(
        NutritionPlan.user_id == current_user.id
    ).order_by(NutritionPlan.created_at.desc()).all()
    
    result = []
    for plan in plans:
        daily_plans = []
        for daily in plan.daily_meal_plans:
            meals = []
            for instance in daily.meal_instances:
                meals.append({
                    "id": instance.meal.id,
                    "name": instance.meal.name,
                    "type": instance.meal_type,
                    "calories": instance.meal.calories,
                    "protein": instance.meal.protein,
                    "carbs": instance.meal.carbs,
                    "fats": instance.meal.fats,
                    "ingredients": json.loads(instance.meal.ingredients) if instance.meal.ingredients else [],
                    "recipe": instance.meal.instructions,
                    "prep_time": instance.meal.prep_time,
                    "image_url": instance.meal.image_url
                })
            
            daily_plans.append({
                "day": daily.day_number,
                "total_calories": daily.total_calories,
                "total_protein": daily.total_protein,
                "total_carbs": daily.total_carbs,
                "total_fats": daily.total_fats,
                "meals": meals
            })
        
        result.append({
            "id": plan.id,
            "title": plan.title,
            "description": plan.description,
            "diet_type": plan.diet_preference.value if plan.diet_preference else "vegetarian",
            "calorie_target": plan.target_calories,
            "duration": plan.duration_days,
            "daily_plans": daily_plans,
            "created_at": plan.created_at.isoformat()
        })
    
    return result