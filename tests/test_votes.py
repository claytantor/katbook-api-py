import pytest
from httpx import AsyncClient


@pytest.fixture
async def voteable_post(client: AsyncClient, auth_headers: dict) -> str:
    await client.post(
        "/api/v1/submeows",
        json={"name": "votesub", "display_name": "Vote Sub"},
        headers=auth_headers,
    )
    resp = await client.post(
        "/api/v1/posts",
        json={"submeow_name": "votesub", "title": "Vote on me", "post_type": "text", "content": "x"},
        headers=auth_headers,
    )
    return resp.json()["data"]["id"]


@pytest.mark.asyncio
async def test_upvote_post(client: AsyncClient, auth_headers: dict, voteable_post: str) -> None:
    resp = await client.post(f"/api/v1/posts/{voteable_post}/upvote", headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["upvotes"] == 1
    assert data["user_vote"] == 1


@pytest.mark.asyncio
async def test_downvote_post(client: AsyncClient, auth_headers: dict, voteable_post: str) -> None:
    resp = await client.post(f"/api/v1/posts/{voteable_post}/downvote", headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["downvotes"] == 1
    assert data["user_vote"] == -1


@pytest.mark.asyncio
async def test_upvote_comment(client: AsyncClient, auth_headers: dict, voteable_post: str) -> None:
    comment_resp = await client.post(
        f"/api/v1/posts/{voteable_post}/comments",
        json={"content": "Nice"},
        headers=auth_headers,
    )
    comment_id = comment_resp.json()["data"]["id"]

    resp = await client.post(f"/api/v1/comments/{comment_id}/upvote", headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["data"]["upvotes"] == 1
