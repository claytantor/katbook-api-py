from pydantic import BaseModel, Field


class FeedParams(BaseModel):
    sort: str = Field("hot", pattern=r"^(hot|new|top|rising)$")
    limit: int = Field(25, ge=1, le=100)
    offset: int = Field(0, ge=0)
