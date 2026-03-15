import pytest
from httpx import AsyncClient


@pytest.fixture
async def seeded(client: AsyncClient, auth_headers: dict) -> None:
    await client.post(
        "/api/v1/submeows",
        json={"name": "searchsub", "display_name": "Search Sub", "description": "searchable community"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/posts",
        json={
            "submeow_name": "searchsub",
            "title": "Unique searchable title XYZ",
            "post_type": "text",
            "content": "Some body text",
        },
        headers=auth_headers,
    )


@pytest.mark.asyncio
async def test_search_posts(client: AsyncClient, auth_headers: dict, seeded: None) -> None:
    resp = await client.get("/api/v1/search?q=XYZ", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["posts"]) >= 1


@pytest.mark.asyncio
async def test_search_submeows(client: AsyncClient, auth_headers: dict, seeded: None) -> None:
    resp = await client.get("/api/v1/search?q=searchsub", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["submeows"]) >= 1


@pytest.mark.asyncio
async def test_search_no_results(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.get("/api/v1/search?q=zzznoresults999", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] == 0
