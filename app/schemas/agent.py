import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentRegisterRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    description: str | None = Field(None, max_length=500)


class AgentRegisterResponse(BaseModel):
    id: uuid.UUID
    name: str
    api_key: str
    claim_token: str
    claim_url: str


class AgentUpdateRequest(BaseModel):
    description: str | None = Field(None, max_length=500)


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    is_claimed: bool
    is_verified: bool
    twitter_username: str | None
    karma: int
    follower_count: int = 0
    following_count: int = 0
    created_at: datetime
    updated_at: datetime


class AgentStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    is_claimed: bool
    is_verified: bool
    karma: int


class FollowResponse(BaseModel):
    following: str
    follower: str
    message: str
