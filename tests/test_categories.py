import pytest


async def create_test_user_and_login(client):
    response = await client.post(
        "/auth/register",
        json={
            "username": "categoryuser",
            "email": "categoryuser@example.com",
            "password": "password123",
        },
    )

    # Registration may already exist if this helper is reused.
    assert response.status_code in (201, 400, 409)

    login_response = await client.post(
        "/auth/login",
        data={
            "username": "categoryuser",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_category(client):
    token = await create_test_user_and_login(client)

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

    assert data["name"] == "Breakfast"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_categories(client):
    token = await create_test_user_and_login(client)

    # Create a category first
    create_response = await client.post(
        "/categories",
        json={
            "name": "Lunch",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert create_response.status_code == 201

    # Get categories
    response = await client.get("/categories")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    category_names = [category["name"] for category in data]

    assert "Lunch" in category_names

