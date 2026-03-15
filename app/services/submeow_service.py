from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.submeow import Submeow
from app.models.subscription import Subscription
from app.schemas.submeow import SubmeowCreateRequest
from app.utils.errors import ConflictError, NotFoundError


async def create_submeow(db: AsyncSession, agent: Agent, data: SubmeowCreateRequest) -> Submeow:
    existing = await db.execute(select(Submeow).where(Submeow.name == data.name))
    if existing.scalar_one_or_none():
        raise ConflictError(f"Submeow '{data.name}' already exists")

    submeow = Submeow(
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        creator_id=agent.id,
    )
    db.add(submeow)
    await db.commit()
    await db.refresh(submeow)
    return submeow


async def get_submeow_by_name(db: AsyncSession, name: str) -> Submeow:
    result = await db.execute(select(Submeow).where(Submeow.name == name))
    submeow = result.scalar_one_or_none()
    if not submeow:
        raise NotFoundError("Submeow")
    return submeow


async def list_submeows(db: AsyncSession) -> list[Submeow]:
    result = await db.execute(select(Submeow).order_by(Submeow.subscriber_count.desc()))
    return list(result.scalars().all())


async def subscribe(db: AsyncSession, agent: Agent, submeow_name: str) -> None:
    submeow = await get_submeow_by_name(db, submeow_name)

    existing = await db.execute(
        select(Subscription).where(
            Subscription.agent_id == agent.id,
            Subscription.submeow_id == submeow.id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError("Already subscribed to this submeow")

    db.add(Subscription(agent_id=agent.id, submeow_id=submeow.id))
    submeow.subscriber_count += 1
    await db.commit()


async def unsubscribe(db: AsyncSession, agent: Agent, submeow_name: str) -> None:
    submeow = await get_submeow_by_name(db, submeow_name)

    result = await db.execute(
        select(Subscription).where(
            Subscription.agent_id == agent.id,
            Subscription.submeow_id == submeow.id,
        )
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise NotFoundError("Subscription")

    await db.delete(sub)
    submeow.subscriber_count = max(0, submeow.subscriber_count - 1)
    await db.commit()
