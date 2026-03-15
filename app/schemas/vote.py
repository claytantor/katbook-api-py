import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.vote import VoteTargetType


class VoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_id: uuid.UUID
    target_type: VoteTargetType
    target_id: uuid.UUID
    value: int
    created_at: datetime


class VoteResultResponse(BaseModel):
    score: int
    upvotes: int
    downvotes: int
    user_vote: int | None
