# backend/test_spoonacular.py
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.spoonacular_service import spoonacular_service
import logging

logging.basicConfig(level=logging.INFO)

async def test_spoonacular():
    print("=" * 60)
    print("🍳 Testing Spoonacular API Integration")
    print("=" * 60)
    
    # Test 1: Search for recipes
    print("\n📋 Test 1: Searching for 'paneer' recipes...")
    recipes = await spoonacular_service.search_recipes(
        query="paneer",
        cuisine="Indian",
        diet="vegetarian",
        max_results=3
    )
    
    print(f"Found {len(recipes)} recipes")
    for i, recipe in enumerate(recipes, 1):
        print(f"\n  Recipe {i}:")
        print(f"    Title: {recipe.get('title', 'N/A')}")
        print(f"    Ready in: {recipe.get('readyInMinutes', 'N/A')} minutes")
        print(f"    Servings: {recipe.get('servings', 'N/A')}")
    
    # Test 2: Generate meal plan
    print("\n\n📋 Test 2: Generating 2000-calorie vegetarian meal plan...")
    meal_plan = await spoonacular_service.generate_meal_plan(
        target_calories=2000,
        diet="vegetarian",
        time_frame="day"
    )
    
    print("\n  Today's Meals:")
    
    # Check what type of response we got
    if isinstance(meal_plan, dict):
        if "meals" in meal_plan:
            # Dictionary format with meals key
            meals_dict = meal_plan["meals"]
            if isinstance(meals_dict, dict):
                for meal_type, meal in meals_dict.items():
                    if isinstance(meal, dict):
                        print(f"    {meal_type.replace('_', ' ').title()}: {meal.get('title', 'N/A')}")
            elif isinstance(meals_dict, list):
                for i, meal in enumerate(meals_dict):
                    print(f"    Meal {i+1}: {meal.get('title', 'N/A') if isinstance(meal, dict) else meal}")
        else:
            # Just print the dict keys
            print(f"    Response keys: {list(meal_plan.keys())}")
    elif isinstance(meal_plan, list):
        # List format
        for i, meal in enumerate(meal_plan):
            if isinstance(meal, dict):
                print(f"    Meal {i+1}: {meal.get('title', 'N/A')}")
            else:
                print(f"    Meal {i+1}: {meal}")
    
    # Display nutrients if available
    if isinstance(meal_plan, dict) and "nutrients" in meal_plan:
        print(f"\n  Daily Totals:")
        print(f"    Calories: {meal_plan['nutrients'].get('calories', 0)}")
        print(f"    Protein: {meal_plan['nutrients'].get('protein', 0)}g")
        print(f"    Fat: {meal_plan['nutrients'].get('fat', 0)}g")
        print(f"    Carbs: {meal_plan['nutrients'].get('carbohydrates', 0)}g")
    
    # Test 3: Get random recipes
    print("\n\n📋 Test 3: Getting random recipes...")
    random_recipes = await spoonacular_service.get_random_recipes(limit=2)
    
    print(f"Found {len(random_recipes)} random recipes")
    for i, recipe in enumerate(random_recipes, 1):
        print(f"\n  Random Recipe {i}:")
        print(f"    Title: {recipe.get('title', 'N/A')}")
    
    # Test 4: Search for products
    print("\n\n📋 Test 4: Searching for 'protein powder'...")
    products = await spoonacular_service.search_food_products(
        query="protein powder",
        max_results=2
    )
    
    print(f"Found {len(products)} products")
    for i, product in enumerate(products, 1):
        print(f"\n  Product {i}:")
        print(f"    Title: {product.get('title', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✅ Spoonacular API Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_spoonacular())