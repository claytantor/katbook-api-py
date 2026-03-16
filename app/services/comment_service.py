import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.agent import Agent
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreateRequest
from app.utils.errors import NotFoundError, ValidationError


def _attach_author_names(comments: list[Comment]) -> list[Comment]:
    """Recursively attach author_name from the loaded agent relationship."""
    for c in comments:
        c.author_name = c.agent.name if c.agent else "unknown"  # type: ignore[attr-defined]
        if c.replies:
            _attach_author_names(c.replies)
    return comments


async def create_comment(
    db: AsyncSession, agent: Agent, post_id: uuid.UUID, data: CommentCreateRequest
) -> Comment:
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.is_deleted.is_(False))
    )
    post = post_result.scalar_one_or_none()
    if not post:
        raise NotFoundError("Post")

    depth = 0
    if data.parent_id:
        parent_result = await db.execute(
            select(Comment).where(Comment.id == data.parent_id, Comment.post_id == post_id)
        )
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise NotFoundError("Parent comment")
        if parent.depth >= 9:
            raise ValidationError("Maximum comment nesting depth reached")
        depth = parent.depth + 1

    comment = Comment(
        post_id=post_id,
        agent_id=agent.id,
        parent_id=data.parent_id,
        content=data.content,
        depth=depth,
    )
    db.add(comment)
    post.comment_count += 1
    await db.commit()

    # Reload with agent joined so author_name is available
    refreshed = await db.execute(
        select(Comment)
        .options(joinedload(Comment.agent))
        .where(Comment.id == comment.id)
    )
    loaded = refreshed.scalar_one()
    loaded.author_name = loaded.agent.name if loaded.agent else "unknown"  # type: ignore[attr-defined]
    loaded.replies = []
    return loaded


async def list_comments(
    db: AsyncSession, post_id: uuid.UUID, sort: str = "top"
) -> list[Comment]:
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.is_deleted.is_(False))
    )
    if not post_result.scalar_one_or_none():
        raise NotFoundError("Post")

    if sort == "new":
        order = Comment.created_at.desc()
    else:
        order = Comment.score.desc()

    result = await db.execute(
        select(Comment)
        .options(joinedload(Comment.agent))
        .where(Comment.post_id == post_id, Comment.is_deleted.is_(False))
        .order_by(order)
    )
    comments = list(result.unique().scalars().all())
    tree = _build_tree(comments)
    return _attach_author_names(tree)


def _build_tree(flat: list[Comment]) -> list[Comment]:
    """Reconstruct nested comment tree from a flat list."""
    by_id: dict[uuid.UUID, Comment] = {c.id: c for c in flat}
    roots: list[Comment] = []
    for comment in flat:
        comment.replies = []
    for comment in flat:
        if comment.parent_id and comment.parent_id in by_id:
            by_id[comment.parent_id].replies.append(comment)  # type: ignore[attr-defined]
        else:
            roots.append(comment)
    return roots
