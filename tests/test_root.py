import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_page(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
