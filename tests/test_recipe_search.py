import pytest

from app.models.ingredient import Ingredient
from tests.conftest import TestSessionLocal


# ============================================================
# HELPER: CREATE USER AND LOGIN
# ============================================================

async def create_test_user_and_login(client, username, email):
    user_data = {
        "username": username,
        "email": email,
        "password": "Password123!",
    }

    register_response = await client.post(
        "/auth/register",
        json=user_data,
    )

    assert register_response.status_code in (200, 201)

    login_response = await client.post(
        "/auth/login",
        data={
            "username": username,
            "password": "Password123!",
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data

    return data["access_token"]


# ============================================================
# HELPER: CREATE CATEGORY
# ============================================================
async def create_test_category(client, token, category_name):
    response = await client.post(
        "/categories",
        json={
            "name": category_name,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]



# ============================================================
# HELPER: CREATE RECIPE
# ============================================================

async def create_test_recipe(
    client,
    token,
    category_id,
    name,
    description,
):
    recipe_data = {
        "name": name,
        "description": description,
        "category_id": category_id,
        "is_public": True,
        "prep_minutes": 10,
        "cook_minutes": 20,
    }

    response = await client.post(
        "/recipes",
        json=recipe_data,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data

    return data["id"]


# ============================================================
# HELPER: CREATE INGREDIENT
# ============================================================

async def create_test_ingredient(name):
    async with TestSessionLocal() as session:
        ingredient = Ingredient(name=name)

        session.add(ingredient)

        await session.commit()

        await session.refresh(ingredient)

        return ingredient.id


# ============================================================
# HELPER: ADD INGREDIENT TO RECIPE
# ============================================================

async def add_ingredient_to_recipe(
    client,
    recipe_id,
    ingredient_id,
):
    response = await client.post(
        f"/recipes/{recipe_id}/ingredients",
        json={
            "ingredient_id": ingredient_id,
            "amount": 2,
            "unit": "cups",
            "preparation": "washed",
        },
    )

    assert response.status_code == 201


# ============================================================
# TEST 1: SEARCH BY RECIPE NAME
# ============================================================

@pytest.mark.asyncio
async def test_search_recipes_by_name(client):

    token = await create_test_user_and_login(
        client,
        "searchuser1",
        "searchuser1@example.com",
    )

    category_id = await create_test_category(
        client,
        token,
        "Search Category",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Jollof Rice",
        "A delicious Nigerian rice recipe.",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Chicken Soup",
        "A warm chicken soup.",
    )

    response = await client.get(
        "/recipes",
        params={
            "search": "Jollof",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Jollof Rice"


# ============================================================
# TEST 2: SEARCH BY DESCRIPTION
# ============================================================

@pytest.mark.asyncio
async def test_search_recipes_by_description(client):

    token = await create_test_user_and_login(
        client,
        "searchuser2",
        "searchuser2@example.com",
    )

    category_id = await create_test_category(
        client,
        token,
        "Description Category",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Rice Recipe",
        "This recipe contains tomatoes and peppers.",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Chicken Recipe",
        "This recipe contains chicken.",
    )

    response = await client.get(
        "/recipes",
        params={
            "search": "tomatoes",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Rice Recipe"


# ============================================================
# TEST 3: FILTER BY INGREDIENT
# ============================================================

@pytest.mark.asyncio
async def test_filter_recipes_by_ingredient(client):

    token = await create_test_user_and_login(
        client,
        "searchuser3",
        "searchuser3@example.com",
    )

    category_id = await create_test_category(
        client,
        token,
        "Ingredient Filter Category",
    )

    rice_recipe_id = await create_test_recipe(
        client,
        token,
        category_id,
        "Rice Dish",
        "Recipe containing rice.",
    )

    chicken_recipe_id = await create_test_recipe(
        client,
        token,
        category_id,
        "Chicken Dish",
        "Recipe containing chicken.",
    )

    rice_id = await create_test_ingredient("Rice")

    chicken_id = await create_test_ingredient("Chicken")

    await add_ingredient_to_recipe(
        client,
        rice_recipe_id,
        rice_id,
    )

    await add_ingredient_to_recipe(
        client,
        chicken_recipe_id,
        chicken_id,
    )

    response = await client.get(
        "/recipes",
        params={
            "ingredient": "Rice",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Rice Dish"


# ============================================================
# TEST 4: FILTER BY CATEGORY
# ============================================================

@pytest.mark.asyncio
async def test_filter_recipes_by_category(client):

    token = await create_test_user_and_login(
        client,
        "searchuser4",
        "searchuser4@example.com",
    )

    breakfast_id = await create_test_category(
        client,
        token,
        "Breakfast",
    )

    dinner_id = await create_test_category(
        client,
        token,
        "Dinner",
    )

    await create_test_recipe(
        client,
        token,
        breakfast_id,
        "Pancakes",
        "Breakfast pancakes.",
    )

    await create_test_recipe(
        client,
        token,
        dinner_id,
        "Jollof Rice",
        "Dinner rice.",
    )

    response = await client.get(
        "/recipes",
        params={
            "category": "Dinner",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Jollof Rice"


# ============================================================
# TEST 5: COMBINE SEARCH AND CATEGORY
# ============================================================

@pytest.mark.asyncio
async def test_search_and_category_together(client):

    token = await create_test_user_and_login(
        client,
        "searchuser5",
        "searchuser5@example.com",
    )

    dinner_id = await create_test_category(
        client,
        token,
        "Dinner",
    )

    breakfast_id = await create_test_category(
        client,
        token,
        "Breakfast",
    )

    await create_test_recipe(
        client,
        token,
        dinner_id,
        "Chicken Dinner",
        "Chicken recipe for dinner.",
    )

    await create_test_recipe(
        client,
        token,
        breakfast_id,
        "Chicken Breakfast",
        "Chicken recipe for breakfast.",
    )

    response = await client.get(
        "/recipes",
        params={
            "search": "Chicken",
            "category": "Dinner",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Chicken Dinner"


# ============================================================
# TEST 6: PAGINATION WITH LIMIT
# ============================================================

@pytest.mark.asyncio
async def test_recipe_pagination_limit(client):

    token = await create_test_user_and_login(
        client,
        "searchuser6",
        "searchuser6@example.com",
    )

    category_id = await create_test_category(
        client,
        token,
        "Pagination Category",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Recipe One",
        "First recipe.",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Recipe Two",
        "Second recipe.",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Recipe Three",
        "Third recipe.",
    )

    response = await client.get(
        "/recipes",
        params={
            "limit": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


# ============================================================
# TEST 7: PAGINATION WITH OFFSET
# ============================================================

@pytest.mark.asyncio
async def test_recipe_pagination_offset(client):

    token = await create_test_user_and_login(
        client,
        "searchuser7",
        "searchuser7@example.com",
    )

    category_id = await create_test_category(
        client,
        token,
        "Offset Category",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Recipe One",
        "First recipe.",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Recipe Two",
        "Second recipe.",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Recipe Three",
        "Third recipe.",
    )

    response = await client.get(
        "/recipes",
        params={
            "limit": 2,
            "offset": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


# ============================================================
# TEST 8: SORT BY NAME ASCENDING
# ============================================================

@pytest.mark.asyncio
async def test_sort_recipes_by_name_ascending(client):

    token = await create_test_user_and_login(
        client,
        "searchuser8",
        "searchuser8@example.com",
    )

    category_id = await create_test_category(
        client,
        token,
        "Sorting Category",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Zebra Recipe",
        "Z recipe.",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Apple Recipe",
        "A recipe.",
    )

    response = await client.get(
        "/recipes",
        params={
            "sort": "name",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["name"] == "Apple Recipe"
    assert data[1]["name"] == "Zebra Recipe"


# ============================================================
# TEST 9: SORT BY NAME DESCENDING
# ============================================================

@pytest.mark.asyncio
async def test_sort_recipes_by_name_descending(client):

    token = await create_test_user_and_login(
        client,
        "searchuser9",
        "searchuser9@example.com",
    )

    category_id = await create_test_category(
        client,
        token,
        "Descending Category",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Apple Recipe",
        "A recipe.",
    )

    await create_test_recipe(
        client,
        token,
        category_id,
        "Zebra Recipe",
        "Z recipe.",
    )

    response = await client.get(
        "/recipes",
        params={
            "sort": "-name",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data[0]["name"] == "Zebra Recipe"
    assert data[1]["name"] == "Apple Recipe"