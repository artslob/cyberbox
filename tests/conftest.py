import pytest
from starlette.testclient import TestClient

from cyberbox.app import create_app


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    # yield client to enable testing startup and shutdown events:
    # https://fastapi.tiangolo.com/advanced/testing-events/
    with TestClient(app) as client:
        yield client
