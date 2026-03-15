import pytest
from httpx import AsyncClient


@pytest.fixture
async def post_id(client: AsyncClient, auth_headers: dict) -> str:
    sub = await client.post(
        "/api/v1/submeows",
        json={"name": "commentsub", "display_name": "Comment Sub"},
        headers=auth_headers,
    )
    p = await client.post(
        "/api/v1/posts",
        json={"submeow_name": "commentsub", "title": "Post for comments", "post_type": "text", "content": "x"},
        headers=auth_headers,
    )
    return p.json()["data"]["id"]


@pytest.mark.asyncio
async def test_add_comment(client: AsyncClient, auth_headers: dict, post_id: str) -> None:
    resp = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "Great post!"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["content"] == "Great post!"


@pytest.mark.asyncio
async def test_reply_to_comment(client: AsyncClient, auth_headers: dict, post_id: str) -> None:
    parent = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "Parent comment"},
        headers=auth_headers,
    )
    parent_id = parent.json()["data"]["id"]

    reply = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "Reply", "parent_id": parent_id},
        headers=auth_headers,
    )
    assert reply.status_code == 201
    assert reply.json()["data"]["depth"] == 1


@pytest.mark.asyncio
async def test_list_comments(client: AsyncClient, auth_headers: dict, post_id: str) -> None:
    await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "Comment A"},
        headers=auth_headers,
    )
    resp = await client.get(f"/api/v1/posts/{post_id}/comments", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)
