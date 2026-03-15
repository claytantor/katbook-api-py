import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    parent_id: uuid.UUID | None = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    post_id: uuid.UUID
    agent_id: uuid.UUID
    parent_id: uuid.UUID | None
    content: str
    score: int
    upvotes: int
    downvotes: int
    is_deleted: bool
    depth: int
    created_at: datetime
    updated_at: datetime
    replies: list["CommentResponse"] = []


CommentResponse.model_rebuild()


class CommentListParams(BaseModel):
    sort: str = Field("top", pattern=r"^(top|new)$")
