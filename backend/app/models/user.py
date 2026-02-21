# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class FitnessGoal(str, enum.Enum):
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"

class WorkoutPreference(str, enum.Enum):
    HIGH = "high_intensity"
    MODERATE = "moderate"
    LOW = "low_intensity"
    YOGA = "yoga"
    CARDIO = "cardio"

class DietPreference(str, enum.Enum):
    VEGETARIAN = "vegetarian"
    NON_VEGETARIAN = "non_vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"

class ActivityLevel(str, enum.Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Role and status
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Personal details
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    fitness_level = Column(String, default="beginner")  # ADD THIS LINE
    activity_level = Column(Enum(ActivityLevel), default=ActivityLevel.MODERATE)
    
    # Fitness preferences
    fitness_goal = Column(Enum(FitnessGoal), default=FitnessGoal.MAINTENANCE)
    workout_preference = Column(Enum(WorkoutPreference), default=WorkoutPreference.MODERATE)  # Changed from HYBRID
    diet_preference = Column(Enum(DietPreference), default=DietPreference.VEGETARIAN)
    
    # Medical information
    medical_conditions = Column(Text, nullable=True)  # JSON string
    allergies = Column(Text, nullable=True)  # JSON string
    injuries = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    health_assessments = relationship("HealthAssessment", back_populates="user", cascade="all, delete-orphan")
    workout_plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")
    nutrition_plans = relationship("NutritionPlan", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("ProgressRecord", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"