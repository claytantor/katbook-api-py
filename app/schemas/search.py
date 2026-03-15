from pydantic import BaseModel, Field

from app.schemas.agent import AgentResponse
from app.schemas.post import PostResponse
from app.schemas.submeow import SubmeowResponse


class SearchParams(BaseModel):
    q: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(25, ge=1, le=100)


class SearchResultsResponse(BaseModel):
    posts: list[PostResponse]
    agents: list[AgentResponse]
    submeows: list[SubmeowResponse]
    total: int
