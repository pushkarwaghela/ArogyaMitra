# backend/app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from datetime import timedelta

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import (
    verify_password, 
    get_password_hash,
    create_access_token, 
    create_refresh_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> dict:
        """Register a new user"""
        try:
            print("🔍 AuthService.register_user called")
            
            # Check if email already exists
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            if existing_email:
                print(f"❌ Email already exists: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Check if username already exists
            existing_username = db.query(User).filter(User.username == user_data.username).first()
            if existing_username:
                print(f"❌ Username already exists: {user_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            
            # Hash password
            print("🔐 Hashing password...")
            hashed_password = get_password_hash(user_data.password)
            print("✅ Password hashed successfully")
            
            # Create new user
            print("👤 Creating user object...")
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                age=user_data.age,
                gender=user_data.gender,
                height=user_data.height,
                weight=user_data.weight,
                fitness_level=user_data.fitness_level,
                fitness_goal=user_data.fitness_goal,
                workout_preference=user_data.workout_preference,
                diet_preference=user_data.diet_preference
            )
            
            print("💾 Adding user to database...")
            db.add(db_user)
            db.commit()
            print(f"✅ User committed with ID: {db_user.id}")
            db.refresh(db_user)
            
            # Generate tokens
            print("🔑 Generating tokens...")
            access_token = create_access_token(
                data={"sub": str(db_user.id), "username": db_user.username}
            )
            refresh_token = create_refresh_token(
                data={"sub": str(db_user.id)}
            )
            print("✅ Tokens generated")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": db_user
            }
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            print(f"❌ Unexpected error in register_user: {str(e)}")
            import traceback
            traceback.print_exc()
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
    
    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> dict:
        """Authenticate and login user"""
        # Find user by username or email
        user = None
        if login_data.username:
            user = db.query(User).filter(User.username == login_data.username).first()
        elif login_data.email:
            user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is inactive"
            )
        
        # Generate tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user
        }
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> dict:
        """Get new access token using refresh token"""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """Get current user from token"""
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user