import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_submeow(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.post(
        "/api/v1/submeows",
        json={"name": "pythonistas", "display_name": "Pythonistas", "description": "All things Python"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "pythonistas"


@pytest.mark.asyncio
async def test_duplicate_submeow(client: AsyncClient, auth_headers: dict) -> None:
    await client.post(
        "/api/v1/submeows",
        json={"name": "dupsub", "display_name": "Dup"},
        headers=auth_headers,
    )
    resp = await client.post(
        "/api/v1/submeows",
        json={"name": "dupsub", "display_name": "Dup"},
        headers=auth_headers,
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_submeows(client: AsyncClient, auth_headers: dict) -> None:
    await client.post(
        "/api/v1/submeows",
        json={"name": "listsub", "display_name": "List Sub"},
        headers=auth_headers,
    )
    resp = await client.get("/api/v1/submeows", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)


@pytest.mark.asyncio
async def test_subscribe_unsubscribe(client: AsyncClient, auth_headers: dict) -> None:
    await client.post(
        "/api/v1/submeows",
        json={"name": "subscribable", "display_name": "Subscribable"},
        headers=auth_headers,
    )

    sub_resp = await client.post("/api/v1/submeows/subscribable/subscribe", headers=auth_headers)
    assert sub_resp.status_code == 201

    unsub_resp = await client.delete("/api/v1/submeows/subscribable/subscribe", headers=auth_headers)
    assert unsub_resp.status_code == 200
