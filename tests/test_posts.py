import pytest
from httpx import AsyncClient


@pytest.fixture
async def submeow(client: AsyncClient, auth_headers: dict) -> dict:
    resp = await client.post(
        "/api/v1/submeows",
        json={"name": "testsubmeow", "display_name": "Test Submeow"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["data"]


@pytest.mark.asyncio
async def test_create_text_post(client: AsyncClient, auth_headers: dict, submeow: dict) -> None:
    resp = await client.post(
        "/api/v1/posts",
        json={
            "submeow_name": submeow["name"],
            "title": "Hello World",
            "post_type": "text",
            "content": "This is the body.",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["title"] == "Hello World"
    assert data["post_type"] == "text"


@pytest.mark.asyncio
async def test_create_link_post(client: AsyncClient, auth_headers: dict, submeow: dict) -> None:
    resp = await client.post(
        "/api/v1/posts",
        json={
            "submeow_name": submeow["name"],
            "title": "A link post",
            "post_type": "link",
            "url": "https://example.com",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["post_type"] == "link"


@pytest.mark.asyncio
async def test_list_posts(client: AsyncClient, auth_headers: dict, submeow: dict) -> None:
    await client.post(
        "/api/v1/posts",
        json={"submeow_name": submeow["name"], "title": "Post 1", "post_type": "text", "content": "x"},
        headers=auth_headers,
    )
    resp = await client.get("/api/v1/posts", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_get_post(client: AsyncClient, auth_headers: dict, submeow: dict) -> None:
    create_resp = await client.post(
        "/api/v1/posts",
        json={"submeow_name": submeow["name"], "title": "Single Post", "post_type": "text", "content": "x"},
        headers=auth_headers,
    )
    post_id = create_resp.json()["data"]["id"]
    resp = await client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == post_id


@pytest.mark.asyncio
async def test_delete_post(client: AsyncClient, auth_headers: dict, submeow: dict) -> None:
    create_resp = await client.post(
        "/api/v1/posts",
        json={"submeow_name": submeow["name"], "title": "Delete Me", "post_type": "text", "content": "x"},
        headers=auth_headers,
    )
    post_id = create_resp.json()["data"]["id"]
    del_resp = await client.delete(f"/api/v1/posts/{post_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    get_resp = await client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
    assert get_resp.status_code == 404
