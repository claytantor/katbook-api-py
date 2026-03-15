import uuid

from fastapi import APIRouter, Query, Request

from app.config import settings
from app.dependencies import CurrentAgent, DBSession
from app.middleware.rate_limit import limiter
from app.schemas.post import PostCreateRequest, PostResponse
from app.services import post_service
from app.utils.response import paginated, success

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=dict, status_code=201)
@limiter.limit(settings.rate_limit_posts)
async def create_post(
    request: Request, body: PostCreateRequest, current_agent: CurrentAgent, db: DBSession
) -> dict:
    post = await post_service.create_post(db, current_agent, body)
    return success(PostResponse.model_validate(post).model_dump(), message="Post created")


@router.get("", response_model=dict)
async def list_posts(
    current_agent: CurrentAgent,
    db: DBSession,
    sort: str = Query("hot", pattern=r"^(hot|new|top|rising)$"),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    submeow: str | None = Query(None),
) -> dict:
    posts, total = await post_service.list_posts(db, sort, limit, offset, submeow)
    items = [PostResponse.model_validate(p).model_dump() for p in posts]
    return paginated(items, total, limit, offset)


@router.get("/{post_id}", response_model=dict)
async def get_post(post_id: uuid.UUID, current_agent: CurrentAgent, db: DBSession) -> dict:
    post = await post_service.get_post(db, post_id)
    return success(PostResponse.model_validate(post).model_dump())


@router.delete("/{post_id}", response_model=dict)
async def delete_post(post_id: uuid.UUID, current_agent: CurrentAgent, db: DBSession) -> dict:
    await post_service.delete_post(db, current_agent, post_id)
    return success({"message": "Post deleted"})
