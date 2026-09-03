from fastapi import APIRouter, Depends, HTTPException, status

from typing import Optional

from fastapi import Query
from sqlalchemy import asc, desc

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies.database import get_session
from app.models.category import Category
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.recipe_ingredient import RecipeIngredient

from app.schemas.recipe import (
    RecipeCreate,
    RecipeDetailResponse,
    RecipeResponse,
    RecipeUpdate,
)

from app.schemas.recipe_ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientResponse,
    RecipeIngredientDetailResponse,
    RecipeIngredientUpdate,
)


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


# ============================================================
# CREATE RECIPE
# POST /recipes
# ============================================================

@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: AsyncSession = Depends(get_session),
):
    recipe = Recipe(
        name=recipe_data.name,
        description=recipe_data.description,
        category_id=recipe_data.category_id,
    )

    db.add(recipe)

    await db.commit()

    await db.refresh(recipe)

    return recipe


# ============================================================
# LIST RECIPES
# GET /recipes
# ============================================================

@router.get(
    "",
    response_model=list[RecipeResponse],
    status_code=status.HTTP_200_OK,
)
async def list_recipes(
    db: AsyncSession = Depends(get_session),
):
    statement = select(Recipe)

    result = await db.execute(statement)

    recipes = result.scalars().all()

    return recipes


# ============================================================
# GET ONE RECIPE
# GET /recipes/{recipe_id}
# ============================================================

@router.get(
    "/{recipe_id}",
    response_model=RecipeDetailResponse,
)
async def get_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Recipe)
        .options(
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
        )
        .where(Recipe.id == recipe_id)
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    return recipe

@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
)
async def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    db: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # FIND RECIPE
    # --------------------------------------------------------

    statement = select(Recipe).where(
        Recipe.id == recipe_id
    )

    result = await db.execute(statement)

    recipe = result.scalar_one_or_none()


    # --------------------------------------------------------
    # CHECK IF RECIPE EXISTS
    # --------------------------------------------------------

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )


    # --------------------------------------------------------
    # MODIFY RECIPE
    # --------------------------------------------------------

    if recipe_data.name is not None:
        recipe.name = recipe_data.name

    if recipe_data.description is not None:
        recipe.description = recipe_data.description

    if recipe_data.category_id is not None:
        recipe.category_id = recipe_data.category_id


    # --------------------------------------------------------
    # COMMIT CHANGES
    # --------------------------------------------------------

    await db.commit()


    # --------------------------------------------------------
    # REFRESH RECIPE
    # --------------------------------------------------------

    await db.refresh(recipe)


    return recipe


# ============================================================
# DELETE RECIPE
# DELETE /recipes/{recipe_id}
# ============================================================

@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # 1. FIND THE RECIPE
    # --------------------------------------------------------

    statement = select(Recipe).where(
        Recipe.id == recipe_id
    )

    result = await db.execute(statement)

    recipe = result.scalar_one_or_none()


    # --------------------------------------------------------
    # 2. CHECK IF RECIPE EXISTS
    # --------------------------------------------------------

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )


    # --------------------------------------------------------
    # 3. DELETE THE RECIPE
    # --------------------------------------------------------

    await db.delete(recipe)


    # --------------------------------------------------------
    # 4. COMMIT THE DELETE
    # --------------------------------------------------------

    await db.commit()


    # --------------------------------------------------------
    # 5. RETURN 204 NO CONTENT
    # --------------------------------------------------------

    return None


@router.post(
    "/{recipe_id}/ingredients",
    response_model=RecipeIngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_ingredient_to_recipe(
    recipe_id: int,
    ingredient_data: RecipeIngredientCreate,
    db: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # 1. FIND THE RECIPE
    # --------------------------------------------------------

    recipe_statement = select(Recipe).where(
        Recipe.id == recipe_id
    )

    recipe_result = await db.execute(recipe_statement)

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )


    # --------------------------------------------------------
    # 2. FIND THE INGREDIENT
    # --------------------------------------------------------

    ingredient_statement = select(Ingredient).where(
        Ingredient.id == ingredient_data.ingredient_id
    )

    ingredient_result = await db.execute(
        ingredient_statement
    )

    ingredient = ingredient_result.scalar_one_or_none()

    if ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found",
        )


    # --------------------------------------------------------
    # 3. CREATE RECIPE-INGREDIENT ASSOCIATION
    # --------------------------------------------------------

    recipe_ingredient = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=ingredient_data.ingredient_id,
        amount=ingredient_data.amount,
        unit=ingredient_data.unit,
        preparation=ingredient_data.preparation,
    )


    # --------------------------------------------------------
    # 4. ADD TO DATABASE SESSION
    # --------------------------------------------------------

    db.add(recipe_ingredient)


    # --------------------------------------------------------
    # 5. COMMIT
    # --------------------------------------------------------

    await db.commit()


    # --------------------------------------------------------
    # 6. REFRESH
    # --------------------------------------------------------

    await db.refresh(recipe_ingredient)


    # --------------------------------------------------------
    # 7. RETURN CREATED ASSOCIATION
    # --------------------------------------------------------

    return recipe_ingredient



# ============================================================
# LIST RECIPE INGREDIENTS
# GET /recipes/{recipe_id}/ingredients
# ============================================================

@router.get(
    "/{recipe_id}/ingredients",
    response_model=list[RecipeIngredientDetailResponse],
    status_code=status.HTTP_200_OK,
)
async def list_recipe_ingredients(
    recipe_id: int,
    db: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # 1. CHECK THAT RECIPE EXISTS
    # --------------------------------------------------------

    recipe_statement = select(Recipe).where(
        Recipe.id == recipe_id
    )

    recipe_result = await db.execute(
        recipe_statement
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )


    # --------------------------------------------------------
    # 2. JOIN RECIPE INGREDIENT WITH INGREDIENT
    # --------------------------------------------------------

    statement = (
        select(
            RecipeIngredient,
            Ingredient.name,
        )
        .join(
            Ingredient,
            RecipeIngredient.ingredient_id == Ingredient.id,
        )
        .where(
            RecipeIngredient.recipe_id == recipe_id
        )
    )


    # --------------------------------------------------------
    # 3. EXECUTE QUERY
    # --------------------------------------------------------

    result = await db.execute(statement)


    # --------------------------------------------------------
    # 4. BUILD RESPONSE
    # --------------------------------------------------------

    recipe_ingredients = []

    for recipe_ingredient, ingredient_name in result.all():

        recipe_ingredients.append(
            RecipeIngredientDetailResponse(
                id=recipe_ingredient.id,
                recipe_id=recipe_ingredient.recipe_id,
                ingredient_id=recipe_ingredient.ingredient_id,
                ingredient_name=ingredient_name,
                amount=recipe_ingredient.amount,
                unit=recipe_ingredient.unit,
                preparation=recipe_ingredient.preparation,
            )
        )


    # --------------------------------------------------------
    # 5. RETURN INGREDIENTS
    # --------------------------------------------------------

    return recipe_ingredients


# ============================================================
# UPDATE RECIPE INGREDIENT
# PUT /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}
# ============================================================

@router.put(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    response_model=RecipeIngredientResponse,
    status_code=status.HTTP_200_OK,
)
async def update_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    ingredient_data: RecipeIngredientUpdate,
    db: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # 1. FIND RECIPE INGREDIENT
    # --------------------------------------------------------

    statement = select(RecipeIngredient).where(
        RecipeIngredient.id == recipe_ingredient_id,
        RecipeIngredient.recipe_id == recipe_id,
    )

    result = await db.execute(statement)

    recipe_ingredient = result.scalar_one_or_none()


    # --------------------------------------------------------
    # 2. CHECK IF RELATIONSHIP EXISTS
    # --------------------------------------------------------

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )


    # --------------------------------------------------------
    # 3. UPDATE AMOUNT
    # --------------------------------------------------------

    if ingredient_data.amount is not None:
        recipe_ingredient.amount = ingredient_data.amount


    # --------------------------------------------------------
    # 4. UPDATE UNIT
    # --------------------------------------------------------

    if ingredient_data.unit is not None:
        recipe_ingredient.unit = ingredient_data.unit


    # --------------------------------------------------------
    # 5. UPDATE PREPARATION
    # --------------------------------------------------------

    if ingredient_data.preparation is not None:
        recipe_ingredient.preparation = (
            ingredient_data.preparation
        )


    # --------------------------------------------------------
    # 6. COMMIT CHANGES
    # --------------------------------------------------------

    await db.commit()


    # --------------------------------------------------------
    # 7. REFRESH
    # --------------------------------------------------------

    await db.refresh(recipe_ingredient)


    # --------------------------------------------------------
    # 8. RETURN UPDATED RECORD
    # --------------------------------------------------------

    return recipe_ingredient



@router.get(
    "",
    response_model=list[RecipeResponse]
)
async def get_recipes(
    search: Optional[str] = Query(
        default=None,
        description="Search recipes by name or description"
    ),

    ingredient: Optional[str] = Query(
        default=None,
        description="Filter recipes by ingredient name"
    ),

    category: Optional[str] = Query(
        default=None,
        description="Filter recipes by category name"
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of recipes to return"
    ),

    offset: int = Query(
        default=0,
        ge=0,
        description="Number of recipes to skip"
    ),

    sort: Optional[str] = Query(
        default=None,
        description="Sort by name or created_at. Use - for descending order."
    ),

    session: AsyncSession = Depends(get_session)
):
    """
    List recipes with:

    - search
    - ingredient filtering
    - category filtering
    - pagination
    - sorting
    """

    # ---------------------------------------------------------
    # START WITH THE RECIPE TABLE
    # ---------------------------------------------------------

    query = select(Recipe)

    # ---------------------------------------------------------
    # SEARCH BY RECIPE NAME OR DESCRIPTION
    # ---------------------------------------------------------

    if search:
        search_term = f"%{search}%"

        query = query.where(
            Recipe.name.ilike(search_term)
            | Recipe.description.ilike(search_term)
        )

    # ---------------------------------------------------------
    # FILTER BY INGREDIENT
    # ---------------------------------------------------------

    if ingredient:
        query = (
            query
            .join(
                RecipeIngredient,
                RecipeIngredient.recipe_id == Recipe.id
            )
            .join(
                Ingredient,
                Ingredient.id == RecipeIngredient.ingredient_id
            )
            .where(
                Ingredient.name.ilike(f"%{ingredient}%")
            )
        )

    # ---------------------------------------------------------
    # FILTER BY CATEGORY
    # ---------------------------------------------------------

    if category:
        query = (
            query
            .join(
                Category,
                Category.id == Recipe.category_id
            )
            .where(
                Category.name.ilike(f"%{category}%")
            )
        )

    # ---------------------------------------------------------
    # SORTING
    # ---------------------------------------------------------

    if sort:

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

    # ---------------------------------------------------------
    # PAGINATION
    # ---------------------------------------------------------

    query = query.limit(limit).offset(offset)

    # ---------------------------------------------------------
    # EXECUTE ASYNC QUERY
    # ---------------------------------------------------------

    result = await session.execute(query)

    # ---------------------------------------------------------
    # GET RECIPE OBJECTS
    # ---------------------------------------------------------

    recipes = result.scalars().unique().all()

    return recipes