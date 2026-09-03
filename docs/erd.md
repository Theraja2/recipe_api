# Recipe API — Entity Relationship Design

## Tables

- users
- categories
- recipes
- ingredients
- recipe_ingredients
- recipe_steps

## Relationships

### User → Recipe
One User can own many Recipes.

### Category → Recipe
One Category can contain many Recipes.

### Recipe → RecipeStep
One Recipe can have many RecipeSteps.

### Recipe → RecipeIngredient
One Recipe can have many RecipeIngredient records.

### Ingredient → RecipeIngredient
One Ingredient can appear in many RecipeIngredient records.

## Foreign Keys

recipes.category_id → categories.id

recipes.owner_id → users.id

recipe_steps.recipe_id → recipes.id

recipe_ingredients.recipe_id → recipes.id

recipe_ingredients.ingredient_id → ingredients.id

## RecipeIngredient

RecipeIngredient is the association table
between Recipe and Ingredient.

It stores:

- amount
- unit
- preparation

because these values depend on how an ingredient
is used in a particular recipe.

## RecipeStep

RecipeStep stores ordered instructions using:

- recipe_id
- step_number
- instruction