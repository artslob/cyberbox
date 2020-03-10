import pytest
from httpx import AsyncClient


@pytest.fixture()
async def logged_user(create_users, client: AsyncClient):
    """ Login with known user produces access token. """
    username = "test_user"
    response = await client.post("/auth/login", data=dict(username=username, password="123"))
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, dict)
    assert set(result.keys()) == {"token_type", "access_token"}
    assert result["token_type"] == "bearer"

    access_token = result["access_token"]
    assert isinstance(access_token, str)

    return username, access_token
