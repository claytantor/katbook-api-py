import uuid

from fastapi import APIRouter

from app.dependencies import CurrentAgent, DBSession
from app.schemas.vote import VoteResultResponse
from app.services import vote_service
from app.utils.response import success

router = APIRouter(tags=["votes"])


@router.post("/posts/{post_id}/upvote", response_model=dict, status_code=201)
async def upvote_post(post_id: uuid.UUID, current_agent: CurrentAgent, db: DBSession) -> dict:
    result = await vote_service.vote_post(db, current_agent, post_id, value=1)
    return success(result.model_dump())


@router.post("/posts/{post_id}/downvote", response_model=dict, status_code=201)
async def downvote_post(post_id: uuid.UUID, current_agent: CurrentAgent, db: DBSession) -> dict:
    result = await vote_service.vote_post(db, current_agent, post_id, value=-1)
    return success(result.model_dump())


@router.post("/comments/{comment_id}/upvote", response_model=dict, status_code=201)
async def upvote_comment(
    comment_id: uuid.UUID, current_agent: CurrentAgent, db: DBSession
) -> dict:
    result = await vote_service.vote_comment(db, current_agent, comment_id, value=1)
    return success(result.model_dump())
