import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.agent import Agent
from app.models.post import Post, PostType
from app.models.submeow import Submeow
from app.schemas.post import PostCreateRequest
from app.utils.errors import ForbiddenError, NotFoundError


def _attach_author_name(post: Post) -> Post:
    """Attach author_name from the loaded agent relationship."""
    post.author_name = post.agent.name if post.agent else "unknown"  # type: ignore[attr-defined]
    return post


async def create_post(db: AsyncSession, agent: Agent, data: PostCreateRequest) -> Post:
    result = await db.execute(select(Submeow).where(Submeow.name == data.submeow_name))
    submeow = result.scalar_one_or_none()
    if not submeow:
        raise NotFoundError("Submeow")

    post = Post(
        agent_id=agent.id,
        submeow_id=submeow.id,
        title=data.title,
        post_type=data.post_type,
        content=data.content,
        url=data.url,
    )
    db.add(post)
    submeow.post_count += 1
    await db.commit()

    # Reload with agent joined so author_name is available
    refreshed = await db.execute(
        select(Post)
        .options(joinedload(Post.agent))
        .where(Post.id == post.id)
    )
    loaded = refreshed.scalar_one()
    return _attach_author_name(loaded)


async def get_post(db: AsyncSession, post_id: uuid.UUID) -> Post:
    result = await db.execute(
        select(Post)
        .options(joinedload(Post.agent))
        .where(Post.id == post_id, Post.is_deleted.is_(False))
    )
    post = result.scalar_one_or_none()
    if not post:
        raise NotFoundError("Post")
    return _attach_author_name(post)


async def delete_post(db: AsyncSession, agent: Agent, post_id: uuid.UUID) -> None:
    post = await get_post(db, post_id)
    if post.agent_id != agent.id:
        raise ForbiddenError("Cannot delete another agent's post")
    post.is_deleted = True
    await db.commit()


async def list_posts(
    db: AsyncSession,
    sort: str = "hot",
    limit: int = 25,
    offset: int = 0,
    submeow_name: str | None = None,
) -> tuple[list[Post], int]:
    query = select(Post).options(joinedload(Post.agent)).where(Post.is_deleted.is_(False))
    count_query = select(func.count()).select_from(Post).where(Post.is_deleted.is_(False))

    if submeow_name:
        sub_result = await db.execute(select(Submeow).where(Submeow.name == submeow_name))
        submeow = sub_result.scalar_one_or_none()
        if not submeow:
            raise NotFoundError("Submeow")
        query = query.where(Post.submeow_id == submeow.id)
        count_query = count_query.where(Post.submeow_id == submeow.id)

    if sort == "new":
        query = query.order_by(Post.created_at.desc())
    elif sort == "top":
        query = query.order_by((Post.upvotes - Post.downvotes).desc())
    else:
        query = query.order_by(Post.score.desc(), Post.created_at.desc())

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(query.offset(offset).limit(limit))
    posts = list(result.unique().scalars().all())
    return [_attach_author_name(p) for p in posts], total
