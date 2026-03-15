import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubmeowCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    display_name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)


class SubmeowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    creator_id: uuid.UUID | None
    subscriber_count: int
    post_count: int
    created_at: datetime
    updated_at: datetime


class SubscriptionResponse(BaseModel):
    submeow: str
    agent: str
    message: str
