import base64
import json

import pytest
from starlette.testclient import TestClient


def decode_base64_dict_from_str(string: str) -> dict:
    missing_padding = len(string) % 4
    string += "=" * (4 - missing_padding)
    decoded_str = base64.b64decode(string).decode("utf-8")
    dictionary = json.loads(decoded_str)
    assert isinstance(dictionary, dict)
    return dictionary


@pytest.mark.parametrize("username", ["qwe", "test"])
def test_login(client: TestClient, username):
    response = client.post("/auth/login", data=dict(username=username, password="123"))
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, dict)
    assert set(result.keys()) == {"token_type", "access_token"}
    assert result["token_type"] == "bearer"

    access_token = result["access_token"]
    assert isinstance(access_token, str)

    parts = access_token.split(".")
    assert len(parts) == 3

    header = decode_base64_dict_from_str(parts[0])
    payload = decode_base64_dict_from_str(parts[1])

    assert header == {"alg": "HS256", "typ": "JWT"}
    assert set(payload.keys()) == {"sub", "exp"}
    assert payload["sub"] == username
