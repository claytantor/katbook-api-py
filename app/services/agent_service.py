import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.follow import Follow
from app.schemas.agent import AgentRegisterRequest, AgentUpdateRequest
from app.utils.errors import ConflictError, NotFoundError
from app.utils.security import (
    generate_api_key,
    generate_claim_token,
    get_api_key_prefix,
    hash_api_key,
)


async def register_agent(db: AsyncSession, data: AgentRegisterRequest) -> tuple[Agent, str]:
    """Register a new agent. Returns (agent, raw_api_key)."""
    existing = await db.execute(select(Agent).where(Agent.name == data.name))
    if existing.scalar_one_or_none():
        raise ConflictError(f"Agent name '{data.name}' is already taken")

    raw_key = generate_api_key()
    agent = Agent(
        name=data.name,
        description=data.description,
        api_key_hash=hash_api_key(raw_key),
        api_key_prefix=get_api_key_prefix(raw_key),
        claim_token=generate_claim_token(),
        is_claimed=False,
        is_verified=False,
        karma=0,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent, raw_key


async def get_agent_by_name(db: AsyncSession, name: str) -> Agent:
    result = await db.execute(select(Agent).where(Agent.name == name))
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundError("Agent")
    return agent


async def update_agent(db: AsyncSession, agent: Agent, data: AgentUpdateRequest) -> Agent:
    if data.description is not None:
        agent.description = data.description
    await db.commit()
    await db.refresh(agent)
    return agent


async def follow_agent(db: AsyncSession, follower: Agent, target_name: str) -> None:
    target = await get_agent_by_name(db, target_name)
    if target.id == follower.id:
        raise ConflictError("Cannot follow yourself")

    existing = await db.execute(
        select(Follow).where(
            Follow.follower_id == follower.id,
            Follow.following_id == target.id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError("Already following this agent")

    db.add(Follow(follower_id=follower.id, following_id=target.id))
    await db.commit()


async def unfollow_agent(db: AsyncSession, follower: Agent, target_name: str) -> None:
    target = await get_agent_by_name(db, target_name)
    result = await db.execute(
        select(Follow).where(
            Follow.follower_id == follower.id,
            Follow.following_id == target.id,
        )
    )
    follow = result.scalar_one_or_none()
    if not follow:
        raise NotFoundError("Follow relationship")
    await db.delete(follow)
    await db.commit()
