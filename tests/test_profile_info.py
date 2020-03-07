from starlette.testclient import TestClient


def test_profile_info(logged_user, client: TestClient):
    """ Check profile endpoint is accessible by access token. """
    username, access_token = logged_user

    response = client.get("auth/profile", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, dict)
    assert result["username"] == username
