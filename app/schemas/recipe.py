from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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