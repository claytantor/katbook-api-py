from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_agent
from app.models.agent import Agent

# Convenience type aliases for use in route signatures
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentAgent = Annotated[Agent, Depends(get_current_agent)]
