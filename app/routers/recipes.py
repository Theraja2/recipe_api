from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_session

from app.models.category import Category
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.user import User
from app.models.recipe_step import RecipeStep

from app.schemas.recipe import (
    RecipeCreate,
    RecipeDetailResponse,
    RecipeResponse,
    RecipeUpdate,
)

from app.schemas.recipe_ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientDetailResponse,
    RecipeIngredientResponse,
    RecipeIngredientUpdate,
)


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)



# CREATE RECIPE
# POST /recipes
@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Check whether the category exists
    category = await db.get(Category, recipe_data.category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {recipe_data.category_id} does not exist",
        )

    # Create the recipe
    recipe = Recipe(
        name=recipe_data.name,
        description=recipe_data.description,
        category_id=recipe_data.category_id,
        owner_id=current_user.id,
        is_public=recipe_data.is_public,
        prep_minutes=recipe_data.prep_minutes,
        cook_minutes=recipe_data.cook_minutes,
    )

    # Add recipe steps
    for step_data in recipe_data.steps:
        recipe.steps.append(
            RecipeStep(
                step_number=step_data.step_number,
                instruction=step_data.instruction,
            )
        )

    db.add(recipe)

    await db.commit()
    await db.refresh(recipe)

    return recipe


# LIST RECIPES

@router.get(
    "",
    response_model=list[RecipeResponse],
    status_code=status.HTTP_200_OK,
)
async def list_recipes(
    search: Optional[str] = Query(
        default=None,
        description="Search your recipes by name or description",
    ),
    ingredient: list[str] | None = Query(
        default=None,
        description="Filter your recipes by one or more ingredient names",
    ),
    category: Optional[str] = Query(
        default=None,
        description="Filter your recipes by category name",
    ),
    max_time: int | None = Query(
        default=None,
        ge=0,
        description="Maximum total preparation + cooking time",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of recipes to return",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of recipes to skip",
    ),
    sort: Optional[str] = Query(
        default=None,
        description=(
            "Sort by name or created_at. "
            "Use - for descending order."
        ),
    ),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    List recipes belonging to the current authenticated user.

    Supports:

    - Search by recipe name or description
    - Filter by one or more ingredients
    - Filter by category
    - Filter by maximum preparation + cooking time
    - Pagination using limit and offset
    - Sorting by name or created_at
    """


    # START WITH CURRENT USER'S RECIPES ONLY
    

    query = select(Recipe).where(
        Recipe.owner_id == current_user.id
    )

    
    # SEARCH BY NAME OR DESCRIPTION
    

    if search:
        search_term = f"%{search.strip()}%"

        query = query.where(
            Recipe.name.ilike(search_term)
            | Recipe.description.ilike(search_term)
        )


    # FILTER BY CATEGORY


    if category:
        category_term = category.strip().lower()

        query = (
            query
            .join(
                Category,
                Category.id == Recipe.category_id,
            )
            .where(
                func.lower(Category.name) == category_term
            )
        )

    
    # FILTER BY ONE OR MORE INGREDIENTS
    

    if ingredient:
        normalized_ingredients = {
            name.strip().lower()
            for name in ingredient
            if name.strip()
        }

        if normalized_ingredients:
            query = (
                query
                .join(
                    RecipeIngredient,
                    RecipeIngredient.recipe_id == Recipe.id,
                )
                .join(
                    Ingredient,
                    Ingredient.id == RecipeIngredient.ingredient_id,
                )
                .where(
                    func.lower(Ingredient.name).in_(
                        normalized_ingredients
                    )
                )
                .group_by(Recipe.id)
                .having(
                    func.count(
                        func.distinct(Ingredient.id)
                    )
                    == len(normalized_ingredients)
                )
            )

    
    # FILTER BY MAXIMUM TOTAL RECIPE TIME
    if max_time is not None:
        query = query.where(
            and_(
                Recipe.prep_minutes.is_not(None),
                Recipe.cook_minutes.is_not(None),
                (
                    Recipe.prep_minutes
                    + Recipe.cook_minutes
                ) <= max_time,
            )
        )

    
    # SORTING
    if sort == "name":
        query = query.order_by(
            asc(Recipe.name)
        )

    elif sort == "-name":
        query = query.order_by(
            desc(Recipe.name)
        )

    elif sort == "created_at":
        query = query.order_by(
            asc(Recipe.created_at)
        )

    elif sort == "-created_at":
        query = query.order_by(
            desc(Recipe.created_at)
        )

    else:
        # Default sorting
        query = query.order_by(
            asc(Recipe.id)
        )

    
    # PAGINATION
    query = (
        query
        .limit(limit)
        .offset(offset)
    )

    # EXECUTE QUERY
    result = await db.execute(query)
    # RETURN UNIQUE RECIPES
    recipes = result.scalars().unique().all()

    return recipes



# GET CURRENT USER RECIPES
# GET /recipes/mine
@router.get(
    "/mine",
    response_model=list[RecipeResponse],
)
async def get_my_recipes(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Recipe)
        .where(
            Recipe.owner_id == current_user.id
        )
        .order_by(
            Recipe.created_at.desc()
        )
    )

    recipes = result.scalars().all()

    return recipes


# GET PUBLIC RECIPES
# GET /recipes/public

@router.get(
    "/public",
    response_model=list[RecipeResponse],
)
async def get_public_recipes(
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Recipe)
        .where(
            Recipe.is_public.is_(True)
        )
        .order_by(
            Recipe.id.desc()
        )
    )

    recipes = result.scalars().all()

    return recipes




# GET ONE RECIPE
# GET /recipes/{recipe_id}
@router.get(
    "/{recipe_id}",
    response_model=RecipeDetailResponse,
)
async def get_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single recipe.

    Access rules:

    - The owner can view their own recipe.
    - Any authenticated user can view a public recipe.
    - A user cannot view another user's private recipe.
    """

    
    # GET RECIPE
    result = await db.execute(
        select(Recipe)
        .options(
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
        )
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    
    # CHECK WHETHER RECIPE EXISTS
    

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )



    # CHECK OWNERSHIP / PUBLIC ACCESS
    
    if (
        recipe.owner_id != current_user.id
        and not recipe.is_public
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this recipe",
        )

    
    # RETURN RECIPE
    return recipe



# UPDATE RECIPE
# PUT /recipes/{recipe_id}
@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
async def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Recipe)
        .options(
            selectinload(Recipe.steps)
        )
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    
    # OWNERSHIP CHECK
    

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this recipe",
        )

    
    # UPDATE PROVIDED RECIPE FIELDS
    

    if recipe_data.name is not None:
        recipe.name = recipe_data.name

    if recipe_data.description is not None:
        recipe.description = recipe_data.description

    if recipe_data.category_id is not None:
        recipe.category_id = recipe_data.category_id

    if recipe_data.is_public is not None:
        recipe.is_public = recipe_data.is_public

    if recipe_data.prep_minutes is not None:
        recipe.prep_minutes = recipe_data.prep_minutes

    if recipe_data.cook_minutes is not None:
        recipe.cook_minutes = recipe_data.cook_minutes

    
    # UPDATE RECIPE STEP

    if recipe_data.steps is not None:

        # Remove existing steps
        recipe.steps.clear()

        # Add the new steps
        for step_data in recipe_data.steps:
            recipe.steps.append(
                RecipeStep(
                    step_number=step_data.step_number,
                    instruction=step_data.instruction,
                )
            )

    await db.commit()
    await db.refresh(recipe)

    return recipe


# DELETE RECIPE
# DELETE /recipes/{recipe_id}


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    
    # OWNERSHIP CHECK
    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this recipe",
        )

    await db.delete(recipe)
    await db.commit()

    return None




# ADD INGREDIENT TO RECIPE
# POST /recipes/{recipe_id}/ingredients
@router.post(
    "/{recipe_id}/ingredients",
    response_model=RecipeIngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_ingredient_to_recipe(
    recipe_id: int,
    ingredient_data: RecipeIngredientCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    # CHECK RECIPE
    recipe_result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    
    # CHECK RECIPE OWNERSHIP
    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this recipe",
        )

    
    # CHECK INGREDIENT
    ingredient_result = await db.execute(
        select(Ingredient).where(
            Ingredient.id == ingredient_data.ingredient_id
        )
    )

    ingredient = ingredient_result.scalar_one_or_none()

    if ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found",
        )

    
    # CREATE RECIPE-INGREDIENT RELATIONSHIP

    recipe_ingredient = RecipeIngredient(
    recipe_id=recipe_id,
    ingredient_id=ingredient_data.ingredient_id,
    amount=ingredient_data.amount,
    unit=ingredient_data.unit,
    preparation=ingredient_data.preparation,
    )

    db.add(recipe_ingredient)

    await db.commit()
    await db.refresh(recipe_ingredient)

    return recipe_ingredient



# LIST RECIPE INGREDIENTS
# GET /recipes/{recipe_id}/ingredients
@router.get(
    "/{recipe_id}/ingredients",
    response_model=list[RecipeIngredientDetailResponse],
    status_code=status.HTTP_200_OK,
)
async def list_recipe_ingredients(
    recipe_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    
    # CHECK RECIPE
    recipe_result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    
    # CHECK ACCESS
    if (
        recipe.owner_id != current_user.id
        and not recipe.is_public
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this recipe",
        )

    
    # GET INGREDIENTS WITH NAMES
    

    statement = (
        select(
            RecipeIngredient.id,
            RecipeIngredient.recipe_id,
            RecipeIngredient.ingredient_id,
            Ingredient.name.label("ingredient_name"),
            RecipeIngredient.amount,
            RecipeIngredient.unit,
            RecipeIngredient.preparation,
        )
        .join(
            Ingredient,
            Ingredient.id == RecipeIngredient.ingredient_id,
        )
        .where(
            RecipeIngredient.recipe_id == recipe_id
        )
        .order_by(
            RecipeIngredient.id
        )
    )

    result = await db.execute(statement)

    rows = result.all()

    return [
        {
            "id": row.id,
            "recipe_id": row.recipe_id,
            "ingredient_id": row.ingredient_id,
            "ingredient_name": row.ingredient_name,
            "amount": row.amount,
            "unit": row.unit,
            "preparation": row.preparation,
        }
        for row in rows
    ]


# UPDATE RECIPE INGREDIENT
# PUT /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}
@router.put(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    response_model=RecipeIngredientResponse,
)
async def update_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    ingredient_data: RecipeIngredientUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    
    # CHECK RECIPE
    

    recipe_result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    
    # CHECK RECIPE OWNERSHIP
    

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this recipe",
        )

    
    # CHECK RECIPE INGREDIENT
    

    result = await db.execute(
        select(RecipeIngredient).where(
            RecipeIngredient.id == recipe_ingredient_id,
            RecipeIngredient.recipe_id == recipe_id,
        )
    )

    recipe_ingredient = result.scalar_one_or_none()

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    
    # UPDATE FIELD

    if ingredient_data.amount is not None:
        recipe_ingredient.amount = ingredient_data.amount

    if ingredient_data.unit is not None:
        recipe_ingredient.unit = ingredient_data.unit

    if ingredient_data.preparation is not None:
        recipe_ingredient.preparation = (
            ingredient_data.preparation
        )

    await db.commit()
    await db.refresh(recipe_ingredient)

    return recipe_ingredient



# DELETE RECIPE INGREDIENT
# DELETE /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}
@router.delete(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    
    # CHECK RECIPE


    recipe_result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    
    # CHECK RECIPE OWNERSHIP


    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this recipe",
        )

    
    # CHECK RECIPE INGREDIENT
    

    result = await db.execute(
        select(RecipeIngredient).where(
            RecipeIngredient.id == recipe_ingredient_id,
            RecipeIngredient.recipe_id == recipe_id,
        )
    )

    recipe_ingredient = result.scalar_one_or_none()

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    
    # DELETE
    await db.delete(recipe_ingredient)
    await db.commit()

    return None