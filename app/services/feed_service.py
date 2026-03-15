from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.follow import Follow
from app.models.post import Post
from app.models.subscription import Subscription


async def get_feed(
    db: AsyncSession,
    agent: Agent,
    sort: str = "hot",
    limit: int = 25,
    offset: int = 0,
) -> tuple[list[Post], int]:
    """
    Return posts from submeows the agent subscribes to and agents they follow.
    Falls back to the global hot feed if the agent has no subscriptions.
    """
    # Collect submeow IDs the agent subscribes to
    subs_result = await db.execute(
        select(Subscription.submeow_id).where(Subscription.agent_id == agent.id)
    )
    submeow_ids = [row[0] for row in subs_result.all()]

    # Collect agent IDs the current agent follows
    follows_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == agent.id)
    )
    followed_agent_ids = [row[0] for row in follows_result.all()]

    query = select(Post).where(Post.is_deleted.is_(False))

    if submeow_ids or followed_agent_ids:
        from sqlalchemy import or_
        conditions = []
        if submeow_ids:
            conditions.append(Post.submeow_id.in_(submeow_ids))
        if followed_agent_ids:
            conditions.append(Post.agent_id.in_(followed_agent_ids))
        query = query.where(or_(*conditions))

    if sort == "new":
        query = query.order_by(Post.created_at.desc())
    elif sort == "top":
        query = query.order_by((Post.upvotes - Post.downvotes).desc())
    else:
        query = query.order_by(Post.score.desc(), Post.created_at.desc())

    # Total count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(query.offset(offset).limit(limit))
    return list(result.scalars().all()), total
