# Recipe API Contract

## Authentication

POST /auth/register
POST /auth/login
POST /auth/refresh

## Recipes

POST /recipes
GET /recipes
GET /recipes/{id}
PUT /recipes/{id}
DELETE /recipes/{id}
GET /recipes/public

## Recipe Ingredients

POST /recipes/{recipe_id}/ingredients
GET /recipes/{recipe_id}/ingredients
PUT /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}
DELETE /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

## Search

GET /recipes?search=pasta

GET /recipes?ingredient=tomato

GET /recipes?category=dinner

GET /recipes?search=chicken&category=dinner

GET /recipes?ingredient=chicken&ingredient=rice

GET /recipes?category=breakfast&max_time=30

## Authentication Rules

Access token expires after 15 minutes.

Refresh token expires after 7 days.

Authentication uses OAuth2 Password Bearer
with JWT tokens.

Passwords are hashed before storage.