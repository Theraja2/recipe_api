from pydantic import BaseModel, ConfigDict, Field


class RecipeStepBase(BaseModel):
    step_number: int = Field(gt=0)
    instruction: str


class RecipeStepCreate(RecipeStepBase):
    pass


class RecipeStepUpdate(BaseModel):
    step_number: int | None = Field(default=None, gt=0)
    instruction: str | None = None


class RecipeStepResponse(RecipeStepBase):
    id: int
    recipe_id: int

    model_config = ConfigDict(from_attributes=True)