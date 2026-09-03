from pydantic import BaseModel, ConfigDict


class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    amount: float | None = None
    unit: str | None = None
    preparation: str | None = None


class RecipeIngredientCreate(RecipeIngredientBase):
    pass


class RecipeIngredientUpdate(BaseModel):
    amount: float | None = None
    unit: str | None = None
    preparation: str | None = None


class RecipeIngredientResponse(RecipeIngredientBase):
    id: int
    recipe_id: int

    model_config = ConfigDict(
        from_attributes=True
    )


class RecipeIngredientDetailResponse(BaseModel):
    id: int
    recipe_id: int
    ingredient_id: int
    ingredient_name: str
    amount: float | None = None
    unit: str | None = None
    preparation: str | None = None