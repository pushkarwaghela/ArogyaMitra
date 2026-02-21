# backend/app/api/v1/endpoints/__init__.py
"""Endpoints package"""
from . import auth
from . import users
from . import workouts
from . import nutrition
from . import progress
from . import analytics
from . import aromi

__all__ = ["auth", "users", "workouts", "nutrition", "progress", "analytics", "aromi"]