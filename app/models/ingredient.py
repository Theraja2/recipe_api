from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.recipe_ingredient import RecipeIngredient


class Ingredient(Base):
    __tablename__ = "ingredients"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # ========================================================
    # INGREDIENT NAME
    # ========================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # ========================================================
    # INGREDIENT → RECIPE INGREDIENTS
    # ONE INGREDIENT CAN APPEAR IN MANY RECIPES
    # ========================================================

    recipe_ingredients: Mapped[
        list["RecipeIngredient"]
    ] = relationship("RecipeIngredient",
        back_populates="ingredient"
    )