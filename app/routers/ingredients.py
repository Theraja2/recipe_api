from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.models.ingredient import Ingredient
from app.schemas.ingredient import (
    IngredientCreate,
    IngredientResponse,
)


router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredients"],
)


@router.post(
    "",
    response_model=IngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ingredient(
    ingredient_data: IngredientCreate,
    session: AsyncSession = Depends(get_session),
):
    # ---------------------------------------------------------
    # 1. Check whether the ingredient already exists
    # ---------------------------------------------------------

    result = await session.execute(
        select(Ingredient).where(
            Ingredient.name == ingredient_data.name
        )
    )

    existing_ingredient = result.scalar_one_or_none()

    # ---------------------------------------------------------
    # 2. Prevent duplicate ingredients
    # ---------------------------------------------------------

    if existing_ingredient:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ingredient already exists",
        )

    # ---------------------------------------------------------
    # 3. Create the Ingredient
    # ---------------------------------------------------------

    ingredient = Ingredient(
        name=ingredient_data.name
    )

    # ---------------------------------------------------------
    # 4. Add to database
    # ---------------------------------------------------------

    session.add(ingredient)

    # ---------------------------------------------------------
    # 5. Save
    # ---------------------------------------------------------

    await session.commit()

    # ---------------------------------------------------------
    # 6. Load generated ID
    # ---------------------------------------------------------

    await session.refresh(ingredient)

    return ingredient