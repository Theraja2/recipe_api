import pytest

from app.models.ingredient import Ingredient
from tests.conftest import TestSessionLocal


async def create_test_user_and_login(client):
    user_data = {
        "username": "recipeingredientuser",
        "email": "recipeingredientuser@example.com",
        "password": "Password123!",
    }

    # Register
    register_response = await client.post(
        "/auth/register",
        json=user_data,
    )

    assert register_response.status_code in (200, 201)

    # Login
    login_response = await client.post(
        "/auth/login",
        data={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data

    return data["access_token"]


async def create_test_category(client, token):
    response = await client.post(
    "/categories",
    json={
        "name": "Breakfast",
    },
    headers={
        "Authorization": f"Bearer {token}",
    },
)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data

    return data["id"]


async def create_test_recipe(client, token, category_id):
    recipe_data = {
        "name": "Ingredient Test Recipe",
        "description": "Recipe used for ingredient relationship testing.",
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


async def create_test_ingredient():
    async with TestSessionLocal() as session:
        ingredient = Ingredient(
            name="Rice"
        )

        session.add(ingredient)

        await session.commit()
        await session.refresh(ingredient)

        return ingredient.id


@pytest.mark.asyncio
async def test_add_recipe_ingredient(client):
    token = await create_test_user_and_login(client)

    category_id = await create_test_category(
        client,
        token,
    )

    recipe_id = await create_test_recipe(
        client,
        token,
        category_id,
    )

    ingredient_id = await create_test_ingredient()

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

    data = response.json()

    assert "id" in data
    assert data["recipe_id"] == recipe_id
    assert data["ingredient_id"] == ingredient_id
    assert data["amount"] == 2
    assert data["unit"] == "cups"
    assert data["preparation"] == "washed"


@pytest.mark.asyncio
async def test_list_recipe_ingredients(client):
    token = await create_test_user_and_login(client)

    category_id = await create_test_category(
        client,
        token,
    )

    recipe_id = await create_test_recipe(
        client,
        token,
        category_id,
    )

    ingredient_id = await create_test_ingredient()

    # Add ingredient to recipe
    add_response = await client.post(
        f"/recipes/{recipe_id}/ingredients",
        json={
            "ingredient_id": ingredient_id,
            "amount": 2,
            "unit": "cups",
            "preparation": "washed",
        },
    )

    assert add_response.status_code == 201

    # Get recipe ingredients
    response = await client.get(
        f"/recipes/{recipe_id}/ingredients"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1

    ingredient = data[0]

    assert ingredient["recipe_id"] == recipe_id
    assert ingredient["ingredient_id"] == ingredient_id
    assert ingredient["ingredient_name"] == "Rice"
    assert ingredient["amount"] == 2
    assert ingredient["unit"] == "cups"
    assert ingredient["preparation"] == "washed"


@pytest.mark.asyncio
async def test_update_recipe_ingredient(client):
    token = await create_test_user_and_login(client)

    category_id = await create_test_category(
        client,
        token,
    )

    recipe_id = await create_test_recipe(
        client,
        token,
        category_id,
    )

    ingredient_id = await create_test_ingredient()

    # Add ingredient
    add_response = await client.post(
        f"/recipes/{recipe_id}/ingredients",
        json={
            "ingredient_id": ingredient_id,
            "amount": 2,
            "unit": "cups",
            "preparation": "washed",
        },
    )

    assert add_response.status_code == 201

    recipe_ingredient = add_response.json()

    recipe_ingredient_id = recipe_ingredient["id"]

    # Update ingredient relationship
    response = await client.put(
        f"/recipes/{recipe_id}/ingredients/{recipe_ingredient_id}",
        json={
            "amount": 3,
            "unit": "tablespoons",
            "preparation": "finely washed",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == recipe_ingredient_id
    assert data["recipe_id"] == recipe_id
    assert data["ingredient_id"] == ingredient_id
    assert data["amount"] == 3
    assert data["unit"] == "tablespoons"
    assert data["preparation"] == "finely washed"


@pytest.mark.asyncio
async def test_delete_recipe_ingredient(client):
    token = await create_test_user_and_login(client)

    category_id = await create_test_category(
        client,
        token,
    )

    recipe_id = await create_test_recipe(
        client,
        token,
        category_id,
    )

    ingredient_id = await create_test_ingredient()

    # Add ingredient
    add_response = await client.post(
        f"/recipes/{recipe_id}/ingredients",
        json={
            "ingredient_id": ingredient_id,
            "amount": 2,
            "unit": "cups",
            "preparation": "washed",
        },
    )

    assert add_response.status_code == 201

    recipe_ingredient_id = add_response.json()["id"]

    # Delete relationship
    response = await client.delete(
        f"/recipes/{recipe_id}/ingredients/{recipe_ingredient_id}"
    )

    assert response.status_code == 204

    # Verify that the relationship no longer exists
    get_response = await client.get(
        f"/recipes/{recipe_id}/ingredients"
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data == []


@pytest.mark.asyncio
async def test_delete_nonexistent_recipe_ingredient(client):
    token = await create_test_user_and_login(client)

    category_id = await create_test_category(
        client,
        token,
    )

    recipe_id = await create_test_recipe(
        client,
        token,
        category_id,
    )

    response = await client.delete(
        f"/recipes/{recipe_id}/ingredients/99999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Recipe ingredient not found"