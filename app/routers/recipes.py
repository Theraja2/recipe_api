from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies.database import get_session
from app.models.recipe import Recipe

from app.schemas.recipe import (
    RecipeCreate,
    RecipeDetailResponse,
    RecipeResponse,
    RecipeUpdate,
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