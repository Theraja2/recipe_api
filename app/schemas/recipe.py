from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.recipe_ingredient import (
    RecipeIngredientDetailResponse
)

from app.schemas.recipe_step import (
    RecipeStepCreate,
    RecipeStepResponse,
)


class RecipeCreate(BaseModel):
    name: str
    description: str | None = None
    category_id: int
    is_public: bool = False

    prep_minutes: int | None = Field(
        default=None,
        ge=0
    )

    cook_minutes: int | None = Field(
        default=None,
        ge=0
    )

    steps: list[RecipeStepCreate] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "string",
                "description": "string",
                "category_id": 0,
                "is_public": False,
                "prep_minutes": 0,
                "cook_minutes": 0,
                "steps": [
                    {
                        "step_number": 1,
                        "instruction": "string"
                    }
                ]
            }
        }
    )


class RecipeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    is_public: bool | None = None

    prep_minutes: int | None = Field(
        default=None,
        ge=0
    )

    cook_minutes: int | None = Field(
        default=None,
        ge=0
    )

    steps: list[RecipeStepCreate] | None = None


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category_id: int
    owner_id: int
    is_public: bool

    prep_minutes: int | None
    cook_minutes: int | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class RecipeDetailResponse(RecipeResponse):
    ingredients: list[RecipeIngredientDetailResponse] = Field(
        default_factory=list
    )

    steps: list[RecipeStepResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )