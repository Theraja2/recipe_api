from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.recipe import Recipe
    from app.models.ingredient import Ingredient


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # ========================================================
    # RECIPE FOREIGN KEY
    # ========================================================

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id"),
        nullable=False,
    )

    # ========================================================
    # INGREDIENT FOREIGN KEY
    # ========================================================

    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id"),
        nullable=False,
    )

    # ========================================================
    # AMOUNT
    # ========================================================

    amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # ========================================================
    # UNIT
    # ========================================================

    unit: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # ========================================================
    # PREPARATION
    # ========================================================

    preparation: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ========================================================
    # RELATIONSHIP → RECIPE
    # ========================================================

    recipe: Mapped["Recipe"] = relationship("Recipe",
        back_populates="ingredients"
    )

    # ========================================================
    # RELATIONSHIP → INGREDIENT
    # ========================================================

    ingredient: Mapped["Ingredient"] = relationship("Ingredient",
        back_populates="recipe_ingredients"
    )