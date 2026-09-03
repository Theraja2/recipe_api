from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.recipe_ingredient import RecipeIngredient
    from app.models.recipe_step import RecipeStep


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    category: Mapped["Category"] = relationship("Category",
        back_populates="recipes"
    )

    ingredients: Mapped[list["RecipeIngredient"]] = relationship("RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )

    steps: Mapped[list["RecipeStep"]] = relationship("RecipeStep",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )