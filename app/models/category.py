from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.recipe import Recipe


class Category(Base):
    __tablename__ = "categories"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # ========================================================
    # CATEGORY NAME
    # ========================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # ========================================================
    # RELATIONSHIP WITH RECIPES
    # ========================================================

    recipes: Mapped[list["Recipe"]] = relationship("Recipe",
        back_populates="category"
    )