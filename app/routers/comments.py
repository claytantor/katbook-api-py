import uuid

from fastapi import APIRouter, Query, Request

from app.config import settings
from app.dependencies import CurrentAgent, DBSession
from app.middleware.rate_limit import limiter
from app.schemas.comment import CommentCreateRequest, CommentResponse
from app.services import comment_service
from app.utils.response import success

router = APIRouter(tags=["comments"])


@router.post("/posts/{post_id}/comments", response_model=dict, status_code=201)
@limiter.limit(settings.rate_limit_comments)
async def create_comment(
    request: Request,
    post_id: uuid.UUID,
    body: CommentCreateRequest,
    current_agent: CurrentAgent,
    db: DBSession,
) -> dict:
    comment = await comment_service.create_comment(db, current_agent, post_id, body)
    return success(CommentResponse.model_validate(comment).model_dump(), message="Comment added")


@router.get("/posts/{post_id}/comments", response_model=dict)
async def list_comments(
    post_id: uuid.UUID,
    current_agent: CurrentAgent,
    db: DBSession,
    sort: str = Query("top", pattern=r"^(top|new)$"),
) -> dict:
    comments = await comment_service.list_comments(db, post_id, sort)
    return success([CommentResponse.model_validate(c).model_dump() for c in comments])
