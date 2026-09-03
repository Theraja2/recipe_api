from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.recipe import Recipe


class RecipeStep(Base):
    __tablename__ = "recipe_steps"

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
    # STEP NUMBER
    # ========================================================

    step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # ========================================================
    # INSTRUCTION
    # ========================================================

    instruction: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # ========================================================
    # RECIPE → STEPS
    # ========================================================

    recipe: Mapped["Recipe"] = relationship("Recipe",
        back_populates="steps"
    )