import os
from pathlib import Path

import httpx
import pytest
import sqlalchemy
from asgi_lifespan import LifespanManager
from databases import Database
from httpx import AsyncClient

from cyberbox import const
from cyberbox.app import create_app
from cyberbox.models import metadata, users

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
def create_config(tmp_path_factory, database_url: str) -> Path:
    configs_dir = tmp_path_factory.mktemp("configs")
    files_dir = tmp_path_factory.mktemp("files-dir")
    config = configs_dir / "config-test.yaml"
    config.write_text(
        f"""
    environment: 'test'
    database:
        url: "{database_url}"
        force_rollback: true
    files_dir: {files_dir}
    """
    )
    return config


@pytest.fixture()
def test_config(create_config: Path, monkeypatch):
    monkeypatch.setenv(const.CONFIG_ENV_NAME, str(create_config))


@pytest.fixture(scope="session")
def create_test_database(database_url: str):
    engine = sqlalchemy.create_engine(database_url)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)


@pytest.fixture()
async def app(test_config, create_test_database):
    app = create_app()
    # to enable startup and shutdown events
    async with LifespanManager(app):
        yield app


@pytest.fixture()
def db(app):
    return app.state.db


@pytest.fixture()
async def httpx_client(app):
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture()
def client(httpx_client):
    return httpx_client


@pytest.fixture()
async def create_user(db: Database):
    username = "qwe"
    await db.execute_many(
        users.insert(),
        [
            dict(
                uid="b3b4a8a3-d179-4f10-808d-12980175beb0",
                username=username,
                disabled=False,
                hashed_password="$2b$12$WCRPaoVwPNmhUXHmHoAkDOrsy4oFnfp/Ozts/iEVoaL2onpsrfZEO",
            )
        ],
    )
    return username


@pytest.fixture()
async def logged_user(create_user: str, client: AsyncClient):
    """ Login with known user produces access token. """
    username = create_user
    response = await client.post("/auth/login", data=dict(username=username, password="123"))
    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, dict)
    assert set(result.keys()) == {"token_type", "access_token"}
    assert result["token_type"] == "bearer"

    access_token = result["access_token"]
    assert isinstance(access_token, str)

    return username, access_token
