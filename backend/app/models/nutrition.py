# backend/app/models/nutrition.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.user import DietPreference

# Association table for meal plan - meal many-to-many relationship
meal_plan_meals = Table(
    'meal_plan_meals',
    Base.metadata,
    Column('nutrition_plan_id', Integer, ForeignKey('nutrition_plans.id')),
    Column('meal_id', Integer, ForeignKey('meals.id'))
)

class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"

class CuisineType(str, enum.Enum):
    INDIAN = "indian"
    CHINESE = "chinese"
    ITALIAN = "italian"
    MEXICAN = "mexican"
    THAI = "thai"
    JAPANESE = "japanese"
    MEDITERRANEAN = "mediterranean"
    AMERICAN = "american"
    CONTINENTAL = "continental"

class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Plan details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Dietary preferences
    diet_preference = Column(Enum(DietPreference), nullable=False)
    cuisine_type = Column(Enum(CuisineType), nullable=True)
    
    # Calorie targets
    target_calories = Column(Integer, nullable=False)
    target_protein = Column(Float, nullable=True)  # in grams
    target_carbs = Column(Float, nullable=True)  # in grams
    target_fats = Column(Float, nullable=True)  # in grams
    target_fiber = Column(Float, nullable=True)  # in grams
    
    # Restrictions
    allergies = Column(Text, nullable=True)  # JSON string
    excluded_ingredients = Column(Text, nullable=True)  # JSON string
    
    # Duration
    duration_days = Column(Integer, default=7)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="nutrition_plans")
    meals = relationship("Meal", secondary=meal_plan_meals, back_populates="nutrition_plans")
    daily_meal_plans = relationship("DailyMealPlan", back_populates="nutrition_plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<NutritionPlan {self.title}>"

class Meal(Base):
    __tablename__ = "meals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Meal details
    meal_type = Column(Enum(MealType), nullable=False)
    cuisine_type = Column(Enum(CuisineType), nullable=True)
    
    # Nutritional info
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    
    # Recipe
    ingredients = Column(Text, nullable=True)  # JSON string
    instructions = Column(Text, nullable=True)
    prep_time = Column(Integer, nullable=True)  # in minutes
    cook_time = Column(Integer, nullable=True)  # in minutes
    
    # Media
    image_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    
    # Dietary tags
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_dairy_free = Column(Boolean, default=False)
    
    # Relationships
    nutrition_plans = relationship("NutritionPlan", secondary=meal_plan_meals, back_populates="meals")
    daily_meal_instances = relationship("DailyMealInstance", back_populates="meal")
    
    def __repr__(self):
        return f"<Meal {self.name}>"

class DailyMealPlan(Base):
    __tablename__ = "daily_meal_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id"), nullable=False)
    
    day_number = Column(Integer, nullable=False)  # 1-7
    total_calories = Column(Integer, nullable=False)
    total_protein = Column(Float, nullable=True)
    total_carbs = Column(Float, nullable=True)
    total_fats = Column(Float, nullable=True)
    
    # Relationships
    nutrition_plan = relationship("NutritionPlan", back_populates="daily_meal_plans")
    meal_instances = relationship("DailyMealInstance", back_populates="daily_meal_plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DailyMealPlan Day {self.day_number}>"

class DailyMealInstance(Base):
    __tablename__ = "daily_meal_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    daily_meal_plan_id = Column(Integer, ForeignKey("daily_meal_plans.id"), nullable=False)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    
    meal_type = Column(Enum(MealType), nullable=False)
    time_of_day = Column(String, nullable=True)  # e.g., "08:00", "13:00"
    serving_size = Column(Float, default=1.0)  # multiplier for servings
    
    # Tracking
    is_consumed = Column(Boolean, default=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    daily_meal_plan = relationship("DailyMealPlan", back_populates="meal_instances")
    meal = relationship("Meal", back_populates="daily_meal_instances")
    
    def __repr__(self):
        return f"<DailyMealInstance {self.meal_type} on Day {self.daily_meal_plan_id}>"