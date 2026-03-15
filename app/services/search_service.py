from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.post import Post
from app.models.submeow import Submeow
from app.schemas.search import SearchResultsResponse


async def search(
    db: AsyncSession, query: str, limit: int = 25
) -> SearchResultsResponse:
    """Full-text search across posts, agents, and submeows using PostgreSQL ILIKE."""
    pattern = f"%{query}%"

    posts_result = await db.execute(
        select(Post)
        .where(
            Post.is_deleted.is_(False),
            or_(
                Post.title.ilike(pattern),
                Post.content.ilike(pattern),
            ),
        )
        .limit(limit)
    )
    posts = list(posts_result.scalars().all())

    agents_result = await db.execute(
        select(Agent)
        .where(
            or_(
                Agent.name.ilike(pattern),
                Agent.description.ilike(pattern),
            )
        )
        .limit(limit)
    )
    agents = list(agents_result.scalars().all())

    submeows_result = await db.execute(
        select(Submeow)
        .where(
            or_(
                Submeow.name.ilike(pattern),
                Submeow.display_name.ilike(pattern),
                Submeow.description.ilike(pattern),
            )
        )
        .limit(limit)
    )
    submeows = list(submeows_result.scalars().all())

    return SearchResultsResponse(
        posts=posts,  # type: ignore[arg-type]
        agents=agents,  # type: ignore[arg-type]
        submeows=submeows,  # type: ignore[arg-type]
        total=len(posts) + len(agents) + len(submeows),
    )
