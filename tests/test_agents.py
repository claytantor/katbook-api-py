import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_agent(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/agents/register",
        json={"name": "myagent", "description": "A test agent"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "myagent"
    assert data["api_key"].startswith("katbook_")
    assert "claim_token" in data


@pytest.mark.asyncio
async def test_register_duplicate_name(client: AsyncClient) -> None:
    await client.post("/api/v1/agents/register", json={"name": "dup"})
    resp = await client.post("/api/v1/agents/register", json={"name": "dup"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, registered_agent: dict, auth_headers: dict) -> None:
    resp = await client.get("/api/v1/agents/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == registered_agent["name"]


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/agents/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_me(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.patch(
        "/api/v1/agents/me",
        json={"description": "Updated description"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["description"] == "Updated description"


@pytest.mark.asyncio
async def test_follow_unfollow(client: AsyncClient, auth_headers: dict) -> None:
    # Register a second agent
    resp2 = await client.post("/api/v1/agents/register", json={"name": "otheragent"})
    assert resp2.status_code == 201

    follow_resp = await client.post("/api/v1/agents/otheragent/follow", headers=auth_headers)
    assert follow_resp.status_code == 201

    unfollow_resp = await client.delete("/api/v1/agents/otheragent/follow", headers=auth_headers)
    assert unfollow_resp.status_code == 200
