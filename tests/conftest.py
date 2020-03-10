import os
from pathlib import Path

import httpx
import pytest
import sqlalchemy
from asgi_lifespan import LifespanManager

from cyberbox import const
from cyberbox.app import create_app
from cyberbox.models import metadata

pytest_plugins = ["tests.fixtures.auth", "tests.fixtures.data"]

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


@pytest.fixture()
def files_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("files_dir")


@pytest.fixture()
def create_config(tmp_path, database_url: str, files_dir: Path) -> Path:
    config = tmp_path / "config-test.yaml"
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
