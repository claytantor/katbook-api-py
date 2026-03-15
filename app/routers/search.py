from fastapi import APIRouter, Query

from app.dependencies import CurrentAgent, DBSession
from app.services import search_service
from app.utils.response import success

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=dict)
async def search(
    current_agent: CurrentAgent,
    db: DBSession,
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(25, ge=1, le=100),
) -> dict:
    results = await search_service.search(db, q, limit)
    return success(results.model_dump())
