# backend/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, 
    UserResponse, RefreshTokenRequest
)
from app.services.auth_service import AuthService
from app.api.v1.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    try:
        print("=" * 60)
        print("REGISTRATION ATTEMPT")
        print(f"Email: {user_data.email}")
        print(f"Username: {user_data.username}")
        print(f"Full Name: {user_data.full_name}")
        print(f"Age: {user_data.age}")
        print(f"Gender: {user_data.gender}")
        print(f"Fitness Goal: {user_data.fitness_goal}")
        print(f"Workout Preference: {user_data.workout_preference}")
        print(f"Diet Preference: {user_data.diet_preference}")
        print("=" * 60)
        
        result = AuthService.register_user(db, user_data)
        
        print("✅ Registration successful!")
        return {
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": result["token_type"],
            "expires_in": result["expires_in"]
        }
    except Exception as e:
        import traceback
        print(f"❌ Registration error: {str(e)}")
        print(traceback.format_exc())
        raise  # Re-raise to let FastAPI handle it

@router.post("/login", response_model=TokenResponse)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    login_data = UserLogin(username=username, password=password)
    result = AuthService.login_user(db, login_data)
    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": result["token_type"],
        "expires_in": result["expires_in"]
    }

@router.post("/login/json", response_model=TokenResponse)
async def login_json(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    result = AuthService.login_user(db, login_data)
    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": result["token_type"],
        "expires_in": result["expires_in"]
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    result = AuthService.refresh_access_token(db, request.refresh_token)
    return result

@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(
    current_user = Depends(get_current_user)
):
    """
    Get current authenticated user details
    """
    return current_user

@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}

@router.post("/debug-register")
async def debug_register(user_data: dict, db: Session = Depends(get_db)):
    """Debug endpoint to see what's happening"""
    try:
        print("=" * 60)
        print("DEBUG REGISTER - Received data:")
        print(json.dumps(user_data, indent=2))
        print("=" * 60)
        
        # Check if user exists
        from app.models.user import User
        existing = db.query(User).filter(
            (User.email == user_data.get("email")) | 
            (User.username == user_data.get("username"))
        ).first()
        
        if existing:
            return {"error": "User already exists", "existing": existing.email}
        
        # Try to create user step by step
        from app.core.security import get_password_hash
        from app.models.user import User, FitnessGoal, WorkoutPreference, DietPreference
        
        hashed = get_password_hash(user_data.get("password"))
        print(f"Password hashed successfully")
        
        # Create user with minimal fields first
        user = User(
            email=user_data.get("email"),
            username=user_data.get("username"),
            full_name=user_data.get("full_name"),
            hashed_password=hashed
        )
        
        # Add optional fields if present
        if user_data.get("age"):
            user.age = user_data.get("age")
        if user_data.get("gender"):
            user.gender = user_data.get("gender")
        if user_data.get("height"):
            user.height = user_data.get("height")
        if user_data.get("weight"):
            user.weight = user_data.get("weight")
        if user_data.get("fitness_level"):
            user.fitness_level = user_data.get("fitness_level")
        if user_data.get("fitness_goal"):
            # Convert string to enum
            try:
                user.fitness_goal = FitnessGoal(user_data.get("fitness_goal"))
            except:
                print(f"Invalid fitness_goal: {user_data.get('fitness_goal')}")
        if user_data.get("workout_preference"):
            try:
                user.workout_preference = WorkoutPreference(user_data.get("workout_preference"))
            except:
                print(f"Invalid workout_preference: {user_data.get('workout_preference')}")
        if user_data.get("diet_preference"):
            try:
                user.diet_preference = DietPreference(user_data.get("diet_preference"))
            except:
                print(f"Invalid diet_preference: {user_data.get('diet_preference')}")
        
        db.add(user)
        db.commit()
        print(f"User created successfully with ID: {user.id}")
        return {"success": True, "user_id": user.id}
        
    except Exception as e:
        db.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR: {str(e)}")
        print(f"TRACE: {error_trace}")
        return {"success": False, "error": str(e), "trace": error_trace}