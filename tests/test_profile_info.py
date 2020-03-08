import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_profile_info(logged_user, client: AsyncClient):
    """ Check profile endpoint is accessible by access token. """
    username, access_token = logged_user

    response = await client.get("auth/profile", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, dict)
    assert result["username"] == username
