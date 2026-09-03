# Recipe API Database Design

## Tables

1. users
2. categories
3. recipes
4. ingredients
5. recipe_ingredients
6. recipe_steps

## Relationships

User 1:N Recipe

Category 1:N Recipe

Recipe 1:N RecipeIngredient

Ingredient 1:N RecipeIngredient

Recipe 1:N RecipeStep

## RecipeIngredient

RecipeIngredient is the association table between
Recipe and Ingredient.

It stores:

- amount
- unit
- preparation

because these values depend on how an ingredient
is used in a particular recipe.

## RecipeStep

RecipeStep stores ordered recipe instructions.

Fields:

- id
- recipe_id
- step_number
- instruction