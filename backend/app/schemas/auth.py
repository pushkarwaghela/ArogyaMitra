# backend/app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, field_serializer
from typing import Optional
from enum import Enum
import re
from datetime import datetime

# Enums matching the models
class FitnessGoal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"

class WorkoutPreference(str, Enum):
    HIGH = "high_intensity"
    MODERATE = "moderate"
    LOW = "low_intensity"
    YOGA = "yoga"
    CARDIO = "cardio"

class DietPreference(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    NON_VEGETARIAN = "non_vegetarian"
    EGGETARIAN = "eggetarian"
    KETO = "keto"
    PALEO = "paleo"

# Registration schema
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=13, le=120)
    gender: Optional[str] = None
    height: Optional[float] = Field(None, ge=50, le=300)
    weight: Optional[float] = Field(None, ge=20, le=500)
    fitness_level: Optional[str] = "beginner"
    fitness_goal: Optional[FitnessGoal] = FitnessGoal.MAINTENANCE
    workout_preference: Optional[WorkoutPreference] = WorkoutPreference.MODERATE
    diet_preference: Optional[DietPreference] = DietPreference.VEGETARIAN
    
    @field_validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @field_validator('username')
    def validate_username(cls, v):
        if not re.match('^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

# Login schema
class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str
    
    @model_validator(mode='after')
    def validate_login_field(self):
        if not self.username and not self.email:
            raise ValueError('Either username or email must be provided')
        return self

# Token response
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

# User response - FIXED with field_serializer
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    fitness_level: str
    fitness_goal: str
    workout_preference: str
    diet_preference: str
    is_active: bool
    is_verified: bool
    created_at: datetime  # Keep as datetime but add serializer
    
    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info):
        return dt.isoformat()
    
    class Config:
        from_attributes = True

# Refresh token request
class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Password change request
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @field_validator('new_password')
    def validate_new_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v