import os
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from cyberbox import const
from cyberbox.app import create_app

CYBERBOX_TEST_DB_URL = "CYBERBOX_TEST_DB_URL"


@pytest.fixture(scope="session")
def database_url():
    """
    Some tests require database. For example, provide url like this:
        export CYBERBOX_TEST_DB_URL="postgresql://testuser:testpass@localhost:6432/cyberbox-test"
    """
    url = os.environ.get(CYBERBOX_TEST_DB_URL)
    if url is None:
        msg = f"This test requires url to database in {CYBERBOX_TEST_DB_URL!r} environment variable"
        pytest.skip(msg)

    return url


@pytest.fixture(scope="session")
def create_config(tmp_path_factory, database_url) -> Path:
    configs_dir = tmp_path_factory.mktemp("configs")
    config = configs_dir / "config-test.yaml"
    config.write_text(
        f"""
environment: 'test'
database:
    url: "{database_url}"
"""
    )
    return config


@pytest.fixture()
def test_config(create_config: Path, monkeypatch):
    monkeypatch.setenv(const.CONFIG_ENV_NAME, str(create_config))


@pytest.fixture()
def app(test_config):
    return create_app()


@pytest.fixture()
def client(app):
    # yield client to enable testing startup and shutdown events:
    # https://fastapi.tiangolo.com/advanced/testing-events/
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def logged_user(client: TestClient):
    """ Login with known user produces access token. """
    username = "qwe"
    response = client.post("/auth/login", data=dict(username=username, password="123"))
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, dict)
    assert set(result.keys()) == {"token_type", "access_token"}
    assert result["token_type"] == "bearer"

    access_token = result["access_token"]
    assert isinstance(access_token, str)

    return username, access_token
