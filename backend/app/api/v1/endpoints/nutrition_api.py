# backend/app/api/v1/endpoints/nutrition_api.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.services.spoonacular_service import spoonacular_service
from app.api.v1.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/nutrition-api", tags=["Nutrition API"])

@router.get("/search/recipes")
async def search_recipes(
    query: str = Query(..., description="Search term"),
    cuisine: Optional[str] = Query(None, description="Cuisine type"),
    diet: Optional[str] = Query(None, description="Diet type"),
    intolerances: Optional[str] = Query(None, description="Allergies/intolerances"),
    max_results: int = Query(10, description="Maximum number of results"),
    current_user: User = Depends(get_current_user)
):
    """Search for recipes based on criteria"""
    recipes = await spoonacular_service.search_recipes(
        query=query,
        cuisine=cuisine,
        diet=diet,
        intolerances=intolerances,
        max_results=max_results
    )
    
    return {
        "query": query,
        "total_results": len(recipes),
        "recipes": recipes
    }

@router.get("/recipes/{recipe_id}")
async def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific recipe"""
    recipe = await spoonacular_service.get_recipe_information(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.get("/meal-plan/generate")
async def generate_meal_plan(
    target_calories: int = Query(2000, description="Daily calorie target"),
    diet: str = Query("vegetarian", description="Diet type"),
    exclude: Optional[str] = Query(None, description="Foods to exclude"),
    time_frame: str = Query("day", description="Time frame (day or week)"),
    current_user: User = Depends(get_current_user)
):
    """Generate a complete meal plan"""
    meal_plan = await spoonacular_service.generate_meal_plan(
        target_calories=target_calories,
        diet=diet,
        exclude=exclude,
        time_frame=time_frame
    )
    
    return meal_plan

@router.get("/recipes/random")
async def get_random_recipes(
    limit: int = Query(3, description="Number of random recipes"),
    current_user: User = Depends(get_current_user)
):
    """Get random recipe suggestions"""
    recipes = await spoonacular_service.get_random_recipes(limit=limit)
    return {
        "total_results": len(recipes),
        "recipes": recipes
    }

@router.get("/search/products")
async def search_products(
    query: str = Query(..., description="Product search term"),
    max_results: int = Query(10, description="Maximum number of results"),
    current_user: User = Depends(get_current_user)
):
    """Search for food products (for grocery lists)"""
    products = await spoonacular_service.search_food_products(
        query=query,
        max_results=max_results
    )
    
    return {
        "query": query,
        "total_results": len(products),
        "products": products
    }