from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.agent import Agent
from app.utils.security import get_api_key_prefix, verify_api_key_hash

bearer = HTTPBearer(auto_error=False)


async def verify_api_key(db: AsyncSession, raw_key: str) -> Agent | None:
    """Look up agent by key prefix then verify the full key hash."""
    prefix = get_api_key_prefix(raw_key)
    result = await db.execute(
        select(Agent).where(Agent.api_key_prefix == prefix)
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        return None
    if not verify_api_key_hash(raw_key, agent.api_key_hash):
        return None
    return agent


async def get_current_agent(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer),
    db: AsyncSession = Depends(get_db),
) -> Agent:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    agent = await verify_api_key(db, credentials.credentials)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return agent
