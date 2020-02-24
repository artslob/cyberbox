import os

import pytest
from starlette.testclient import TestClient

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
        pytest.skip(
            f"This test requires url to database in {CYBERBOX_TEST_DB_URL!r} environment variable"
        )

    return url


@pytest.fixture(scope="session")
def app(database_url):
    return create_app(database_url=database_url)


@pytest.fixture()
def client(app):
    # yield client to enable testing startup and shutdown events:
    # https://fastapi.tiangolo.com/advanced/testing-events/
    with TestClient(app) as client:
        yield client
