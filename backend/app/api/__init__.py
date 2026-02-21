# backend/app/api/__init__.py
"""
API package.
This file makes the api directory a Python package.
"""
from . import v1

__all__ = ["v1"]