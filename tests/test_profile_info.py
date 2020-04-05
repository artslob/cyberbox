import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.asyncio
async def test_profile_info(logged_user, client: AsyncClient):
    """ Check profile endpoint is accessible by access token. """
    username, access_token, headers = logged_user

    response = await client.get("auth/profile", headers=headers)
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, dict)
    assert result["username"] == username


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, expected_details",
    [
        [None, {"detail": "Not authenticated"}],
        [{"Authorization": f"Bearer 123"}, {"detail": "Could not validate access token"}],
    ],
)
async def test_profile_info_unknown_user(client: AsyncClient, headers: dict, expected_details):
    """ Profile is unreachable without valid authorization info. """
    response = await client.get("auth/profile", headers=headers)
    assert response.status_code == 401
    assert response.json() == expected_details


@pytest.mark.asyncio
async def test_profile_info_disabled_user(client: AsyncClient, disabled_user):
    username, access_token, headers = disabled_user

    response = await client.get("auth/profile", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is disabled"}
