import pytest


# ============================================================
# TEST HELPERS
# ============================================================


async def create_test_user_and_login(client):
    """Create a test user and return an authentication token."""

    user_data = {
        "username": "recipeuser",
        "email": "recipeuser@example.com",
        "password": "Password123!",
    }

    # --------------------------------------------------------
    # Register user
    # --------------------------------------------------------

    register_response = await client.post(
        "/auth/register",
        json=user_data,
    )

    assert register_response.status_code in (200, 201)

    # --------------------------------------------------------
    # Login user
    # --------------------------------------------------------

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
    """Create a test category using the authenticated user."""

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
    assert data["name"] == "Breakfast"

    return data["id"]


# ============================================================
# CREATE RECIPE
# POST /recipes
# ============================================================


@pytest.mark.asyncio
async def test_create_recipe(client):
    """Test POST /recipes."""

    token = await create_test_user_and_login(client)

    category_id = await create_test_category(
        client,
        token
    )

    response = await client.post(
        "/recipes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Jollof Rice",
            "description": "A simple Nigerian jollof rice recipe.",
            "category_id": category_id,
            "is_public": True,
            "prep_minutes": 15,
            "cook_minutes": 45,
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["name"] == "Jollof Rice"
    assert data["description"] == (
        "A simple Nigerian jollof rice recipe."
    )
    assert data["category_id"] == category_id
    assert data["is_public"] is True
    assert data["prep_minutes"] == 15
    assert data["cook_minutes"] == 45

    assert "id" in data
    assert "owner_id" in data


# ============================================================
# GET ALL RECIPES
# GET /recipes
# ============================================================


@pytest.mark.asyncio
async def test_get_recipes(client):
    """Test GET /recipes."""

    token = await create_test_user_and_login(client)

    category_id = await create_test_category(
        client,
        token
    )

    create_response = await client.post(
        "/recipes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Fried Rice",
            "description": "A fried rice recipe.",
            "category_id": category_id,
            "is_public": True,
            "prep_minutes": 20,
            "cook_minutes": 30,
        },
    )

    assert create_response.status_code in (200, 201)

    response = await client.get(
        "/recipes",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    assert any(
        recipe["name"] == "Fried Rice"
        for recipe in data
    )


# ============================================================
# GET RECIPE BY ID
# GET /recipes/{recipe_id}
# ============================================================


@pytest.mark.asyncio
async def test_get_recipe_by_id(client):
    """Test GET /recipes/{recipe_id}."""

    token = await create_test_user_and_login(client)

    category_id = await create_test_category(
        client,
        token
    )

    create_response = await client.post(
        "/recipes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Pancakes",
            "description": "Simple pancakes.",
            "category_id": category_id,
            "is_public": True,
            "prep_minutes": 10,
            "cook_minutes": 15,
        },
    )

    assert create_response.status_code in (200, 201)

    created_recipe = create_response.json()

    recipe_id = created_recipe["id"]

    response = await client.get(
        f"/recipes/{recipe_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == recipe_id
    assert data["name"] == "Pancakes"


# ============================================================
# UPDATE RECIPE
# PUT /recipes/{recipe_id}
# ============================================================


@pytest.mark.asyncio
async def test_update_recipe(client):
    """Test PUT /recipes/{recipe_id}."""

    token = await create_test_user_and_login(client)

    category_id = await create_test_category(
        client,
        token
    )

    create_response = await client.post(
        "/recipes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Old Recipe Name",
            "description": "Old description.",
            "category_id": category_id,
            "is_public": False,
            "prep_minutes": 10,
            "cook_minutes": 20,
        },
    )

    assert create_response.status_code in (200, 201)

    recipe_id = create_response.json()["id"]

    response = await client.put(
        f"/recipes/{recipe_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Updated Recipe Name",
            "description": "Updated description.",
            "is_public": True,
            "prep_minutes": 15,
            "cook_minutes": 25,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == recipe_id
    assert data["name"] == "Updated Recipe Name"
    assert data["description"] == "Updated description."
    assert data["is_public"] is True
    assert data["prep_minutes"] == 15
    assert data["cook_minutes"] == 25


# ============================================================
# DELETE RECIPE
# DELETE /recipes/{recipe_id}
# ============================================================


@pytest.mark.asyncio
async def test_delete_recipe(client):
    """Test DELETE /recipes/{recipe_id}."""

    token = await create_test_user_and_login(client)

    category_id = await create_test_category(
        client,
        token
    )

    create_response = await client.post(
        "/recipes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Recipe To Delete",
            "description": "This recipe will be deleted.",
            "category_id": category_id,
            "is_public": False,
            "prep_minutes": 5,
            "cook_minutes": 10,
        },
    )

    assert create_response.status_code in (200, 201)

    recipe_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/recipes/{recipe_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert delete_response.status_code in (200, 204)

    get_response = await client.get(
        f"/recipes/{recipe_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert get_response.status_code == 404

