# backend/test_import.py
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Test importing the app module
try:
    import app
    print("✅ app module found")
    print(f"app location: {app.__file__}")
except ImportError as e:
    print(f"❌ app module not found: {e}")

# Test importing api module
try:
    from app import api
    print("✅ api module found")
    print(f"api location: {api.__file__}")
except ImportError as e:
    print(f"❌ api module not found: {e}")

# Test importing v1 module
try:
    from app.api import v1
    print("✅ v1 module found")
    print(f"v1 location: {v1.__file__}")
except ImportError as e:
    print(f"❌ v1 module not found: {e}")

# Test importing router
try:
    from app.api.v1 import router
    print(f"✅ Successfully imported router from app.api.v1")
    print(f"router type: {type(router)}")
except Exception as e:
    print(f"❌ Failed to import router: {e}")

# Test importing auth
try:
    from app.api.v1.endpoints import auth
    print(f"✅ Successfully imported auth from app.api.v1.endpoints")
    print(f"auth location: {auth.__file__}")
except Exception as e:
    print(f"❌ Failed to import auth: {e}")

# Test importing auth_router
try:
    from app.api.v1.endpoints.auth import router as auth_router
    print(f"✅ Successfully imported auth_router directly")
    print(f"auth_router type: {type(auth_router)}")
except Exception as e:
    print(f"❌ Failed to import auth_router: {e}")