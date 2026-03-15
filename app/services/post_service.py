import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.post import Post, PostType
from app.models.submeow import Submeow
from app.schemas.post import PostCreateRequest
from app.utils.errors import ForbiddenError, NotFoundError


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
    await db.refresh(post)
    return post


async def get_post(db: AsyncSession, post_id: uuid.UUID) -> Post:
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.is_deleted.is_(False))
    )
    post = result.scalar_one_or_none()
    if not post:
        raise NotFoundError("Post")
    return post


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
    query = select(Post).where(Post.is_deleted.is_(False))
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
        # hot and rising — both use created_at desc as a proxy; real scoring in service layer
        query = query.order_by(Post.score.desc(), Post.created_at.desc())

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(query.offset(offset).limit(limit))
    return list(result.scalars().all()), total
