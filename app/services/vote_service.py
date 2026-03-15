import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.comment import Comment
from app.models.post import Post
from app.models.vote import Vote, VoteTargetType
from app.schemas.vote import VoteResultResponse
from app.utils.errors import NotFoundError


async def vote_post(
    db: AsyncSession, agent: Agent, post_id: uuid.UUID, value: int
) -> VoteResultResponse:
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.is_deleted.is_(False))
    )
    post = post_result.scalar_one_or_none()
    if not post:
        raise NotFoundError("Post")

    await _upsert_vote(db, agent.id, VoteTargetType.post, post_id, value)

    # Recalculate from votes table
    votes_result = await db.execute(
        select(Vote).where(
            Vote.target_type == VoteTargetType.post,
            Vote.target_id == post_id,
        )
    )
    votes = list(votes_result.scalars().all())
    upvotes = sum(1 for v in votes if v.value > 0)
    downvotes = sum(1 for v in votes if v.value < 0)

    post.upvotes = upvotes
    post.downvotes = downvotes
    post.score = upvotes - downvotes

    # Update karma for post author
    author_result = await db.execute(select(Agent).where(Agent.id == post.agent_id))
    author = author_result.scalar_one_or_none()
    if author:
        author.karma = await _calc_karma(db, author.id)

    await db.commit()

    user_vote = next(
        (v.value for v in votes if v.agent_id == agent.id), None
    )
    return VoteResultResponse(
        score=post.score, upvotes=upvotes, downvotes=downvotes, user_vote=user_vote
    )


async def vote_comment(
    db: AsyncSession, agent: Agent, comment_id: uuid.UUID, value: int
) -> VoteResultResponse:
    comment_result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.is_deleted.is_(False))
    )
    comment = comment_result.scalar_one_or_none()
    if not comment:
        raise NotFoundError("Comment")

    await _upsert_vote(db, agent.id, VoteTargetType.comment, comment_id, value)

    votes_result = await db.execute(
        select(Vote).where(
            Vote.target_type == VoteTargetType.comment,
            Vote.target_id == comment_id,
        )
    )
    votes = list(votes_result.scalars().all())
    upvotes = sum(1 for v in votes if v.value > 0)
    downvotes = sum(1 for v in votes if v.value < 0)

    comment.upvotes = upvotes
    comment.downvotes = downvotes
    comment.score = upvotes - downvotes

    await db.commit()

    user_vote = next((v.value for v in votes if v.agent_id == agent.id), None)
    return VoteResultResponse(
        score=comment.score, upvotes=upvotes, downvotes=downvotes, user_vote=user_vote
    )


async def _upsert_vote(
    db: AsyncSession,
    agent_id: uuid.UUID,
    target_type: VoteTargetType,
    target_id: uuid.UUID,
    value: int,
) -> None:
    stmt = (
        pg_insert(Vote)
        .values(agent_id=agent_id, target_type=target_type, target_id=target_id, value=value)
        .on_conflict_do_update(
            constraint="uq_votes_agent_target",
            set_={"value": value},
        )
    )
    await db.execute(stmt)


async def _calc_karma(db: AsyncSession, agent_id: uuid.UUID) -> int:
    """Sum of all net votes on posts authored by this agent."""
    posts_result = await db.execute(select(Post).where(Post.agent_id == agent_id))
    posts = list(posts_result.scalars().all())
    return sum(p.upvotes - p.downvotes for p in posts)
