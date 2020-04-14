import os
from pathlib import Path

import httpx
import pytest
import sqlalchemy
from asgi_lifespan import LifespanManager

from cyberbox import const, orm
from cyberbox.app import create_app
from cyberbox.const import CYBERBOX_TEST_DB_URL

pytest_plugins = ["tests.fixtures.auth", "tests.fixtures.data", "tests.fixtures.files"]


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
    jwt:
        secret_key: '3256963ad0ec2ea3ef70b5ca2a6e1c95595cf489ff2930f900f1b3493eaf1a0f'
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
    orm.metadata.create_all(engine)
    yield
    orm.metadata.drop_all(engine)


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
