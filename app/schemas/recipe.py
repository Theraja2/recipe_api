from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.recipe_ingredient import RecipeIngredientResponse
from app.schemas.recipe_step import RecipeStepResponse


class RecipeBase(BaseModel):
    name: str
    description: str | None = None
    category_id: int


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None


class RecipeResponse(RecipeBase):
    id: int
    created_at: datetime
    description: Optional[str] = None
    category_id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecipeDetailResponse(RecipeResponse):
    ingredients: list[RecipeIngredientResponse] = Field(
        default_factory=list
    )
    steps: list[RecipeStepResponse] = Field(
        default_factory=list
    )