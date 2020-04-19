import asyncio

from httpx import AsyncClient
from starlette import status


async def main():
    print("running test script")
    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        await script(client)

    print("test script done")


async def script(client: AsyncClient):
    username, password = "qwe", "123"
    response = await client.post("/auth/login", data=dict(username=username, password=password))
    assert response.status_code == status.HTTP_200_OK
    print(f"logged as {username}")
    access_token = response.json()["access_token"]
    print(f"access token is {access_token}")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.get("/admin/user", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    print(f"got user list: {response.json()}")

    with open(__file__) as file:
        response = await client.post("/file/upload", files=dict(file=file), headers=headers)
        assert response.status_code == status.HTTP_200_OK
        file_uid = response.json()["uid"]
        print(f"uploaded file (current script) with UUID {file_uid}")

    response = await client.get(f"/file/{file_uid}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    print(f"download file {file_uid}, first 3 lines: {response.text.splitlines()[:3]}")

    response = await client.post(f"/link/{file_uid}", headers=headers, json=dict(is_onetime=True))
    assert response.status_code == status.HTTP_200_OK
    link = response.json()["link"]
    print(f"created one time link: {link}")

    response = await client.get(f"/link/{link}")
    assert response.status_code == status.HTTP_200_OK
    print(f"downloaded file by link, first 3 lines: {response.text.splitlines()[:3]}")

    response = await client.get(f"/link/{link}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    print(f"second try to download file by link is unsuccessful, code: {response.status_code}")


if __name__ == "__main__":
    asyncio.run(main())
