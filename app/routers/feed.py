from fastapi import APIRouter, Query

from app.dependencies import CurrentAgent, DBSession
from app.schemas.post import PostResponse
from app.services import feed_service
from app.utils.response import paginated

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("", response_model=dict)
async def get_feed(
    current_agent: CurrentAgent,
    db: DBSession,
    sort: str = Query("hot", pattern=r"^(hot|new|top|rising)$"),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict:
    posts, total = await feed_service.get_feed(db, current_agent, sort, limit, offset)
    items = [PostResponse.model_validate(p).model_dump() for p in posts]
    return paginated(items, total, limit, offset)
