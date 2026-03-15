import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_feed_empty(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.get("/api/v1/feed", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_feed_with_subscription(client: AsyncClient, auth_headers: dict) -> None:
    await client.post(
        "/api/v1/submeows",
        json={"name": "feedsub", "display_name": "Feed Sub"},
        headers=auth_headers,
    )
    await client.post("/api/v1/submeows/feedsub/subscribe", headers=auth_headers)
    await client.post(
        "/api/v1/posts",
        json={"submeow_name": "feedsub", "title": "Feed Post", "post_type": "text", "content": "x"},
        headers=auth_headers,
    )

    resp = await client.get("/api/v1/feed", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_feed_sort_modes(client: AsyncClient, auth_headers: dict) -> None:
    for sort in ["hot", "new", "top", "rising"]:
        resp = await client.get(f"/api/v1/feed?sort={sort}", headers=auth_headers)
        assert resp.status_code == 200
