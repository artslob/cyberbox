from uuid import uuid4

import pytest
from databases import Database
from httpx import AsyncClient
from starlette import status

from cyberbox import orm


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


@pytest.mark.asyncio
async def test_user_update(client: AsyncClient, admin_user, logged_user, db: Database):
    """ Check admin can change attributes of users. """
    logged_username, _, _ = logged_user
    username, access_token, headers = admin_user

    query = orm.User.select().where(orm.User.c.username == logged_username)
    logged_uid = (await db.fetch_one(query))["uid"]

    json = dict(is_admin=True, disabled=True)
    response = await client.put(f"/admin/user/{logged_uid}", headers=headers, json=json)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is None

    query = (
        orm.User.select()
        .where(orm.User.c.username == logged_username)
        .where(orm.User.c.is_admin.is_(True))
        .where(orm.User.c.disabled.is_(True))
    )
    assert (await db.fetch_one(query))["uid"] == logged_uid


@pytest.mark.asyncio
async def test_user_update_404(client: AsyncClient, admin_user):
    username, access_token, headers = admin_user

    json = dict(is_admin=True, disabled=True)
    response = await client.put(f"/admin/user/{uuid4()}", headers=headers, json=json)
    assert response.status_code == status.HTTP_404_NOT_FOUND
