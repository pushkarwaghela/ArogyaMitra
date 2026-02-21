# backend/app/services/nutrition_service.py
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging

from app.models.user import User
from app.models.nutrition import NutritionPlan, Meal, DailyMealPlan, DailyMealInstance, MealType, CuisineType
from app.services.ai_agent import arogya_mitra_agent
from app.services.spoonacular_service import spoonacular_service

logger = logging.getLogger(__name__)

class NutritionService:
    
    @staticmethod
    async def generate_nutrition_plan(
        db: Session,
        user: User,
        preferences: Dict[str, Any]
    ) -> NutritionPlan:
        """Generate and save a nutrition plan for user"""
        
        # Get AI-generated plan
        ai_plan = await arogya_mitra_agent.generate_nutrition_plan(user, preferences)
        
        # Create nutrition plan in database
        nutrition_plan = NutritionPlan(
            user_id=user.id,
            title=ai_plan.get("title", "Personalized Nutrition Plan"),
            description=ai_plan.get("description", ""),
            diet_preference=user.diet_preference,
            cuisine_type=preferences.get("cuisine_type"),
            target_calories=ai_plan.get("target_calories", 2000),
            target_protein=ai_plan.get("target_protein"),
            target_carbs=ai_plan.get("target_carbs"),
            target_fats=ai_plan.get("target_fats"),
            target_fiber=ai_plan.get("target_fiber"),
            allergies=user.allergies,
            duration_days=preferences.get("duration_days", 7),
            is_active=True,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=preferences.get("duration_days", 7))
        )
        
        db.add(nutrition_plan)
        db.flush()
        
        # Create daily meal plans
        daily_plans = await NutritionService._create_daily_meal_plans(
            db, nutrition_plan, ai_plan.get("daily_plans", [])
        )
        
        db.commit()
        db.refresh(nutrition_plan)
        
        return nutrition_plan
    
    @staticmethod
    async def _create_daily_meal_plans(
        db: Session,
        nutrition_plan: NutritionPlan,
        daily_plans_data: List[Dict]
    ) -> List[DailyMealPlan]:
        """Create daily meal plans from AI data"""
        daily_meal_plans = []
        
        for day_data in daily_plans_data:
            day_number = day_data.get("day", 1)
            
            daily_plan = DailyMealPlan(
                nutrition_plan_id=nutrition_plan.id,
                day_number=day_number,
                total_calories=day_data.get("total_calories", 0),
                total_protein=day_data.get("total_protein"),
                total_carbs=day_data.get("total_carbs"),
                total_fats=day_data.get("total_fats")
            )
            db.add(daily_plan)
            db.flush()
            
            # Create meal instances
            meals = day_data.get("meals", [])
            await NutritionService._create_meal_instances(db, daily_plan, meals)
            
            daily_meal_plans.append(daily_plan)
        
        return daily_meal_plans
    
    @staticmethod
    async def _create_meal_instances(
        db: Session,
        daily_plan: DailyMealPlan,
        meals_data: List[Dict]
    ):
        """Create meal instances for a daily plan"""
        for meal_data in meals_data:
            # Find or create meal
            meal = await NutritionService._get_or_create_meal(db, meal_data)
            
            meal_instance = DailyMealInstance(
                daily_meal_plan_id=daily_plan.id,
                meal_id=meal.id,
                meal_type=meal_data.get("type", MealType.MEAL),
                time_of_day=meal_data.get("time"),
                serving_size=meal_data.get("serving_size", 1.0)
            )
            db.add(meal_instance)
    
    @staticmethod
    async def _get_or_create_meal(db: Session, meal_data: Dict) -> Meal:
        """Get existing meal or create new one"""
        meal_name = meal_data.get("name", "").strip()
        
        # Try to find existing meal
        meal = db.query(Meal).filter(
            Meal.name.ilike(f"%{meal_name}%")
        ).first()
        
        if not meal:
            # Create new meal
            meal = Meal(
                name=meal_name,
                description=meal_data.get("description", ""),
                meal_type=meal_data.get("type", MealType.MEAL),
                cuisine_type=meal_data.get("cuisine"),
                calories=meal_data.get("calories", 0),
                protein=meal_data.get("protein"),
                carbs=meal_data.get("carbs"),
                fats=meal_data.get("fats"),
                fiber=meal_data.get("fiber"),
                ingredients=json.dumps(meal_data.get("ingredients", [])),
                instructions=meal_data.get("instructions"),
                prep_time=meal_data.get("prep_time"),
                cook_time=meal_data.get("cook_time"),
                image_url=meal_data.get("image_url"),
                is_vegetarian=meal_data.get("is_vegetarian", False),
                is_vegan=meal_data.get("is_vegan", False),
                is_gluten_free=meal_data.get("is_gluten_free", False),
                is_dairy_free=meal_data.get("is_dairy_free", False)
            )
            db.add(meal)
            db.flush()
        
        return meal
    
    @staticmethod
    async def get_user_nutrition_plans(db: Session, user_id: int) -> List[NutritionPlan]:
        """Get all nutrition plans for a user"""
        return db.query(NutritionPlan).filter(
            NutritionPlan.user_id == user_id
        ).order_by(NutritionPlan.created_at.desc()).all()
    
    @staticmethod
    async def get_active_nutrition_plan(db: Session, user_id: int) -> Optional[NutritionPlan]:
        """Get active nutrition plan for user"""
        return db.query(NutritionPlan).filter(
            NutritionPlan.user_id == user_id,
            NutritionPlan.is_active == True
        ).first()
    
    @staticmethod
    async def mark_meal_consumed(
        db: Session,
        meal_instance_id: int
    ) -> Optional[DailyMealInstance]:
        """Mark a meal as consumed"""
        meal_instance = db.query(DailyMealInstance).filter(
            DailyMealInstance.id == meal_instance_id
        ).first()
        
        if meal_instance:
            meal_instance.is_consumed = True
            meal_instance.consumed_at = datetime.now()
            db.commit()
            db.refresh(meal_instance)
        
        return meal_instance