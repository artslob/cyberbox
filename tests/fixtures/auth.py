import pytest
from httpx import AsyncClient


async def login_as(username: str, client: AsyncClient) -> tuple:
    response = await client.post("/auth/login", data=dict(username=username, password="123"))
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, dict)
    assert set(result.keys()) == {"token_type", "access_token"}
    assert result["token_type"] == "bearer"

    access_token = result["access_token"]
    assert isinstance(access_token, str)

    headers = {"Authorization": f"Bearer {access_token}"}

    return username, access_token, headers


@pytest.fixture()
async def logged_user(create_users, client: AsyncClient):
    """ Login with known user produces access token. """
    return await login_as("test_user", client)


@pytest.fixture()
async def active_user(create_users, client: AsyncClient):
    return await login_as("active_user", client)
