import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):

    response = await client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Welcome to the Recipe API"