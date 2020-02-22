from starlette.testclient import TestClient


def test_root_page(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.template.name == "root.html"
    assert "request" in response.context
