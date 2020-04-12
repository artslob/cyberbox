import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.asyncio
async def test_not_logged_user(client: AsyncClient):
    response = await client.get("/admin/user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_usual_user(client: AsyncClient, logged_user):
    username, access_token, headers = logged_user
    response = await client.get("/admin/user", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "you must be admin to access this endpoint"}


@pytest.mark.asyncio
async def test_admin_user_user_list(client: AsyncClient, admin_user):
    username, access_token, headers = admin_user
    response = await client.get("/admin/user", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    items = json.pop("items")
    for i in items:
        i.pop("created")
        i.pop("uid")
    assert items == [
        {"disabled": False, "is_admin": False, "username": "test_user"},
        {"disabled": True, "is_admin": False, "username": "disabled_user"},
        {"disabled": False, "is_admin": False, "username": "active_user"},
        {"disabled": False, "is_admin": True, "username": "admin_user"},
    ]
    assert json == {
        "has_next": False,
        "has_previous": False,
        "next_page_number": None,
        "pages": 1,
        "previous_page_number": None,
        "total": 4,
    }
