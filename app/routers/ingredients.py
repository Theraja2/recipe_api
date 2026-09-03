from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient


router = APIRouter(
    prefix="/recipes",
    tags=["Recipe Ingredients"]
)


@router.delete(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an ingredient relationship from a recipe.

    This deletes the RecipeIngredient record only.
    The global Ingredient remains in the database.
    """

    # ---------------------------------------------------------
    # 1. Find the RecipeIngredient
    # ---------------------------------------------------------

    result = await session.execute(
        select(RecipeIngredient).where(
            RecipeIngredient.id == recipe_ingredient_id,
            RecipeIngredient.recipe_id == recipe_id
        )
    )

    recipe_ingredient = result.scalar_one_or_none()

    # ---------------------------------------------------------
    # 2. Check whether the relationship exists
    # ---------------------------------------------------------

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found"
        )

    # ---------------------------------------------------------
    # 3. Delete the RecipeIngredient relationship
    # ---------------------------------------------------------

    await session.delete(recipe_ingredient)

    # ---------------------------------------------------------
    # 4. Save the deletion
    # ---------------------------------------------------------

    await session.commit()

    # ---------------------------------------------------------
    # 5. 204 No Content means no response body
    # ---------------------------------------------------------

    return None