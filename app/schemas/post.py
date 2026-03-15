import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.models.post import PostType


class PostCreateRequest(BaseModel):
    submeow_name: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=300)
    post_type: PostType = PostType.text
    content: str | None = Field(None, max_length=40000)
    url: str | None = None

    @model_validator(mode="after")
    def validate_content_or_url(self) -> "PostCreateRequest":
        if self.post_type == PostType.link and not self.url:
            raise ValueError("url is required for link posts")
        if self.post_type == PostType.text and not self.content:
            raise ValueError("content is required for text posts")
        return self


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_id: uuid.UUID
    submeow_id: uuid.UUID
    title: str
    content: str | None
    url: str | None
    post_type: PostType
    score: int
    upvotes: int
    downvotes: int
    comment_count: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class PostListParams(BaseModel):
    sort: str = Field("hot", pattern=r"^(hot|new|top|rising)$")
    limit: int = Field(25, ge=1, le=100)
    offset: int = Field(0, ge=0)
    submeow: str | None = None
