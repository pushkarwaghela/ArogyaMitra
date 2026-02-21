import os
import re

print("🔍 Checking backend files for missing imports...")

backend_dir = "app"
issues_found = False

for root, dirs, files in os.walk(backend_dir):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for common missing imports
            if 'User' in content and 'from app.models.user import User' not in content and 'import User' not in content:
                if 'class User' not in content:  # Not the definition file
                    print(f"⚠️  Possible missing User import in {filepath}")
                    issues_found = True
            
            if 'WorkoutPlan' in content and 'from app.models.workout import WorkoutPlan' not in content:
                if 'class WorkoutPlan' not in content:
                    print(f"⚠️  Possible missing WorkoutPlan import in {filepath}")
                    issues_found = True
            
            if 'NutritionPlan' in content and 'from app.models.nutrition import NutritionPlan' not in content:
                if 'class NutritionPlan' not in content:
                    print(f"⚠️  Possible missing NutritionPlan import in {filepath}")
                    issues_found = True

if not issues_found:
    print("✅ No obvious import issues found!")