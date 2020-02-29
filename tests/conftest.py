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
environment: 'dev'
database:
    url: "{database_url}"
"""
    )
    return config


@pytest.fixture()
def test_config(create_config, monkeypatch):
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
