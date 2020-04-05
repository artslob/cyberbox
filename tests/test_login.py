import base64
import json

import arrow
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize("data", [dict(), dict(username="", password=""), None])
async def test_empty_user_login(client: AsyncClient, data):
    """ Login without credentials failed. """
    response = await client.post("/auth/login", data=data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"loc": ["body", "username"], "msg": "field required", "type": "value_error.missing"},
            {"loc": ["body", "password"], "msg": "field required", "type": "value_error.missing"},
        ]
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data", [dict(username="not-existing", password="123"), dict(username=" ", password=" ")],
)
async def test_not_existing_user_login(client: AsyncClient, data):
    """ Login as unknown user failed. """
    response = await client.post("/auth/login", data=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect user or password"}


@pytest.mark.asyncio
async def test_disabled_user_login(create_users, client: AsyncClient):
    """ Check that disabled user can get access token. """
    response = await client.post("/auth/login", data=dict(username="disabled_user", password="123"))
    assert response.status_code == 200
    assert "access_token" in response.json()


def decode_base64_dict_from_str(string: str) -> dict:
    missing_padding = len(string) % 4
    string += "=" * (4 - missing_padding)
    decoded_str = base64.b64decode(string).decode("utf-8")
    dictionary = json.loads(decoded_str)
    assert isinstance(dictionary, dict)
    return dictionary


def test_access_token(logged_user):
    """ Check access token fields. """
    username, access_token, headers = logged_user

    parts = access_token.split(".")
    assert len(parts) == 3

    header = decode_base64_dict_from_str(parts[0])
    payload = decode_base64_dict_from_str(parts[1])

    assert header == {"alg": "HS256", "typ": "JWT"}
    assert set(payload.keys()) == {"sub", "exp", "iat"}
    assert payload["sub"] == username

    now = arrow.utcnow()

    exp = payload["exp"]
    assert isinstance(exp, int)
    assert now.shift(minutes=59).timestamp <= exp <= now.shift(minutes=61).timestamp

    iat = payload["iat"]
    assert isinstance(iat, int)
    assert now.shift(minutes=-1).timestamp <= iat <= now.shift(minutes=1).timestamp
