import pytest


@pytest.mark.asyncio
async def test_register_user(client):

    response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_duplicate_registration(client):

    user_data = {
        "username": "duplicateuser",
        "email": "duplicate@example.com",
        "password": "Password123!",
    }

    first_response = await client.post(
        "/auth/register",
        json=user_data,
    )

    assert first_response.status_code in (200, 201)

    second_response = await client.post(
        "/auth/register",
        json=user_data,
    )

    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_login(client):

    user_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "Password123!",
    }

    register_response = await client.post(
        "/auth/register",
        json=user_data,
    )

    assert register_response.status_code in (200, 201)

    response = await client.post(
        "/auth/login",
        data={
            "username": "loginuser",
            "password": "Password123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_invalid_login(client):

    user_data = {
        "username": "invalidlogin",
        "email": "invalid@example.com",
        "password": "Password123!",
    }

    await client.post(
        "/auth/register",
        json=user_data,
    )

    response = await client.post(
        "/auth/login",
        data={
            "username": "invalidlogin",
            "password": "WrongPassword!",
        },
    )

    assert response.status_code == 401