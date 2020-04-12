from uuid import uuid4

import arrow
import pytest
from databases import Database
from httpx import AsyncClient

from cyberbox import orm
from cyberbox.routes.auth import crypt_context


@pytest.fixture()
async def create_users(db: Database):
    hashed_password = crypt_context.hash("123")
    values = [
        dict(
            uid=uuid4(),
            username=username,
            disabled=disabled,
            hashed_password=hashed_password,
            created=arrow.utcnow().datetime,
            is_admin=is_admin,
        )
        for username, disabled, is_admin in [
            ("test_user", False, False),
            ("disabled_user", True, False),
            ("active_user", False, False),
            ("admin_user", False, True),
        ]
    ]
    await db.execute_many(orm.User.insert(), values)


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


@pytest.fixture()
async def disabled_user(create_users, client: AsyncClient):
    return await login_as("disabled_user", client)


@pytest.fixture()
async def admin_user(create_users, client: AsyncClient):
    return await login_as("admin_user", client)
