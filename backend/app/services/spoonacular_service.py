# backend/app/services/spoonacular_service.py
import httpx
import asyncio
from typing import List, Dict, Optional, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class SpoonacularService:
    """Service to interact with Spoonacular API for nutrition and recipes"""
    
    def __init__(self):
        self.api_key = settings.SPOONACULAR_API_KEY
        self.base_url = "https://api.spoonacular.com"
        
    async def search_recipes(
        self,
        query: str,
        cuisine: Optional[str] = None,
        diet: Optional[str] = None,
        intolerances: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for recipes based on criteria"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/recipes/complexSearch",
                    params={
                        "apiKey": self.api_key,
                        "query": query,
                        "cuisine": cuisine,
                        "diet": diet,
                        "intolerances": intolerances,
                        "number": max_results,
                        "addRecipeInformation": True,
                        "addRecipeNutrition": True,
                        "fillIngredients": True
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                else:
                    logger.error(f"Spoonacular API error: {response.status_code}")
                    return self._get_fallback_recipes(query)
                    
        except Exception as e:
            logger.error(f"Error searching recipes: {e}")
            return self._get_fallback_recipes(query)
    
    async def get_recipe_information(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific recipe"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/recipes/{recipe_id}/information",
                    params={
                        "apiKey": self.api_key,
                        "includeNutrition": True
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error getting recipe info: {e}")
        
        return None
    
    async def generate_meal_plan(
        self,
        target_calories: int,
        diet: str = "vegetarian",
        exclude: Optional[str] = None,
        time_frame: str = "day"
    ) -> Dict[str, Any]:
        """
        Generate a complete meal plan
        
        Args:
            target_calories: Daily calorie target
            diet: Diet type (vegetarian, vegan, etc.)
            exclude: Foods to exclude (allergies)
            time_frame: "day" or "week"
            
        Returns:
            Meal plan with recipes and nutrition info
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/mealplanner/generate",
                    params={
                        "apiKey": self.api_key,
                        "timeFrame": time_frame,
                        "targetCalories": target_calories,
                        "diet": diet,
                        "exclude": exclude
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Log the response structure for debugging
                    logger.info(f"Meal plan response type: {type(data)}")
                    if isinstance(data, list):
                        logger.info(f"List length: {len(data)}")
                        # Convert list to expected dictionary format
                        return {
                            "meals": {f"meal_{i+1}": meal for i, meal in enumerate(data)},
                            "nutrients": self._calculate_nutrients_from_meals(data)
                        }
                    return data
                else:
                    logger.error(f"Meal plan generation failed: {response.status_code}")
                    return self._generate_fallback_meal_plan(target_calories, diet)
                    
        except Exception as e:
            logger.error(f"Error generating meal plan: {e}")
            return self._generate_fallback_meal_plan(target_calories, diet)
    
    def _calculate_nutrients_from_meals(self, meals: List[Dict]) -> Dict[str, float]:
        """Calculate total nutrients from a list of meals"""
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        
        for meal in meals:
            if "nutrition" in meal:
                for nutrient in meal["nutrition"].get("nutrients", []):
                    if nutrient["name"] == "Calories":
                        total_calories += nutrient["amount"]
                    elif nutrient["name"] == "Protein":
                        total_protein += nutrient["amount"]
                    elif nutrient["name"] == "Fat":
                        total_fat += nutrient["amount"]
                    elif nutrient["name"] == "Carbohydrates":
                        total_carbs += nutrient["amount"]
        
        return {
            "calories": total_calories,
            "protein": total_protein,
            "fat": total_fat,
            "carbohydrates": total_carbs
        }
    
    async def get_recipe_nutrition(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Get nutrition information for a recipe"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/recipes/{recipe_id}/nutritionWidget.json",
                    params={"apiKey": self.api_key}
                )
                
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error getting nutrition: {e}")
        
        return None
    
    async def get_random_recipes(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get random recipe suggestions"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/recipes/random",
                    params={
                        "apiKey": self.api_key,
                        "number": limit
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("recipes", [])
        except Exception as e:
            logger.error(f"Error getting random recipes: {e}")
        
        return []
    
    async def search_food_products(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for food products (for grocery lists)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/food/products/search",
                    params={
                        "apiKey": self.api_key,
                        "query": query,
                        "number": max_results
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("products", [])
        except Exception as e:
            logger.error(f"Error searching products: {e}")
        
        return []
    
    def _get_fallback_recipes(self, query: str) -> List[Dict[str, Any]]:
        """Provide fallback recipes when API fails"""
        fallback_recipes = {
            "chicken": [
                {
                    "id": 1,
                    "title": "Grilled Chicken Breast",
                    "image": "https://spoonacular.com/placeholder.jpg",
                    "readyInMinutes": 30,
                    "servings": 4,
                    "nutrition": {
                        "nutrients": [
                            {"name": "Calories", "amount": 250, "unit": "kcal"},
                            {"name": "Protein", "amount": 35, "unit": "g"},
                            {"name": "Fat", "amount": 8, "unit": "g"},
                            {"name": "Carbs", "amount": 0, "unit": "g"}
                        ]
                    }
                }
            ],
            "paneer": [
                {
                    "id": 2,
                    "title": "Palak Paneer",
                    "image": "https://spoonacular.com/placeholder.jpg",
                    "readyInMinutes": 45,
                    "servings": 4,
                    "nutrition": {
                        "nutrients": [
                            {"name": "Calories", "amount": 320, "unit": "kcal"},
                            {"name": "Protein", "amount": 18, "unit": "g"},
                            {"name": "Fat", "amount": 22, "unit": "g"},
                            {"name": "Carbs", "amount": 12, "unit": "g"}
                        ]
                    }
                }
            ]
        }
        
        for key, recipes in fallback_recipes.items():
            if key in query.lower():
                return recipes
        
        # Generic fallback
        return [{
            "id": 0,
            "title": f"Healthy {query} Recipe",
            "image": "https://spoonacular.com/placeholder.jpg",
            "readyInMinutes": 30,
            "servings": 2,
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 400, "unit": "kcal"},
                    {"name": "Protein", "amount": 20, "unit": "g"},
                    {"name": "Fat", "amount": 15, "unit": "g"},
                    {"name": "Carbs", "amount": 40, "unit": "g"}
                ]
            }
        }]
    
    def _generate_fallback_meal_plan(self, target_calories: int, diet: str) -> Dict[str, Any]:
        """Generate a simple fallback meal plan"""
        meals = {
            "breakfast": [
                {"title": "Oatmeal with Fruits", "calories": 350},
                {"title": "Greek Yogurt with Berries", "calories": 300},
                {"title": "Smoothie Bowl", "calories": 380}
            ],
            "lunch": [
                {"title": "Quinoa Salad", "calories": 450},
                {"title": "Lentil Soup with Bread", "calories": 400},
                {"title": "Vegetable Stir-fry with Tofu", "calories": 420}
            ],
            "dinner": [
                {"title": "Chickpea Curry with Rice", "calories": 500},
                {"title": "Grilled Vegetables with Pasta", "calories": 480},
                {"title": "Mushroom Risotto", "calories": 520}
            ],
            "snack": [
                {"title": "Apple with Peanut Butter", "calories": 200},
                {"title": "Mixed Nuts", "calories": 180},
                {"title": "Fruit Smoothie", "calories": 220}
            ]
        }
        
        return {
            "meals": {
                "breakfast": meals["breakfast"][0],
                "lunch": meals["lunch"][0],
                "dinner": meals["dinner"][0],
                "snack": meals["snack"][0]
            },
            "nutrients": {
                "calories": target_calories,
                "protein": round(target_calories * 0.15 / 4),
                "fat": round(target_calories * 0.30 / 9),
                "carbohydrates": round(target_calories * 0.55 / 4)
            }
        }

# Create singleton instance
spoonacular_service = SpoonacularService()