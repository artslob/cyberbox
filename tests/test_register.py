import pytest
from databases import Database
from httpx import AsyncClient
from sqlalchemy import func, select

from cyberbox import orm

username_short = {
    "detail": [
        {
            "ctx": {"limit_value": 3},
            "loc": ["body", "username"],
            "msg": "ensure this value has at least 3 characters",
            "type": "value_error.any_str.min_length",
        }
    ]
}

short_pass = {
    "detail": [
        {
            "ctx": {"limit_value": 3},
            "loc": ["body", "password2"],
            "msg": "ensure this value has at least 3 characters",
            "type": "value_error.any_str.min_length",
        }
    ]
}

pass_not_equal = {"detail": "submitted passwords are not equal"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data, expected_status, expected_count, expected_json",
    [
        [dict(username="test", password1="zz321", password2="zz321"), 200, 1, None],
        [dict(username="te", password1="zz321", password2="zz321"), 422, 0, username_short],
        [dict(username="test", password1="zz321", password2="zz"), 422, 0, short_pass],
        [dict(username="test", password1="123321", password2="qweasd"), 400, 0, pass_not_equal],
    ],
)
async def test_register(
    client: AsyncClient, db: Database, data: dict, expected_status, expected_count, expected_json
):
    response = await client.post("/auth/register", data=data)
    assert response.status_code == expected_status
    assert response.json() == expected_json
    assert await db.execute(select([func.count()]).select_from(orm.User)) == expected_count


@pytest.mark.asyncio
async def test_register_with_existing_username(client: AsyncClient, db: Database, logged_user):
    username, access_token, headers = logged_user
    data = dict(username=username, password1="123", password2="123")
    response = await client.post("/auth/register", data=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "user with username 'test_user' already exists"}
