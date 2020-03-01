import base64
import json

from starlette.testclient import TestClient


def test_not_existing_user_login(client: TestClient):
    """ Login as unknown user failed. """
    response = client.post("/auth/login", data=dict(username="not-existing", password="123"))
    assert response.status_code == 401


def decode_base64_dict_from_str(string: str) -> dict:
    missing_padding = len(string) % 4
    string += "=" * (4 - missing_padding)
    decoded_str = base64.b64decode(string).decode("utf-8")
    dictionary = json.loads(decoded_str)
    assert isinstance(dictionary, dict)
    return dictionary


def test_access_token(logged_user):
    """ Check access token fields. """
    username, access_token = logged_user

    parts = access_token.split(".")
    assert len(parts) == 3

    header = decode_base64_dict_from_str(parts[0])
    payload = decode_base64_dict_from_str(parts[1])

    assert header == {"alg": "HS256", "typ": "JWT"}
    assert set(payload.keys()) == {"sub", "exp"}
    assert payload["sub"] == username


def test_profile_info(logged_user, client: TestClient):
    """ Check profile endpoint is accessible by access token. """
    username, access_token = logged_user

    response = client.get("auth/profile", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, dict)
    assert result["username"] == username
