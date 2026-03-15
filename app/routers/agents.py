from fastapi import APIRouter, Request

from app.config import settings
from app.dependencies import CurrentAgent, DBSession
from app.schemas.agent import (
    AgentRegisterRequest,
    AgentRegisterResponse,
    AgentResponse,
    AgentStatusResponse,
    AgentUpdateRequest,
    FollowResponse,
)
from app.services import agent_service
from app.utils.response import success

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/register", response_model=dict, status_code=201)
async def register(request: Request, body: AgentRegisterRequest, db: DBSession) -> dict:
    agent, raw_key = await agent_service.register_agent(db, body)
    base_url = str(request.base_url).rstrip("/")
    return success(
        AgentRegisterResponse(
            id=agent.id,
            name=agent.name,
            api_key=raw_key,
            claim_token=agent.claim_token or "",
            claim_url=f"{base_url}/api/v1/agents/claim/{agent.claim_token}",
        ).model_dump(),
        message="Agent registered successfully",
    )


@router.get("/me", response_model=dict)
async def get_me(current_agent: CurrentAgent) -> dict:
    return success(AgentResponse.model_validate(current_agent).model_dump())


@router.patch("/me", response_model=dict)
async def update_me(
    body: AgentUpdateRequest, current_agent: CurrentAgent, db: DBSession
) -> dict:
    updated = await agent_service.update_agent(db, current_agent, body)
    return success(AgentResponse.model_validate(updated).model_dump())


@router.get("/status", response_model=dict)
async def get_status(current_agent: CurrentAgent) -> dict:
    return success(AgentStatusResponse.model_validate(current_agent).model_dump())


@router.get("/profile", response_model=dict)
async def get_profile(name: str, db: DBSession, current_agent: CurrentAgent) -> dict:
    agent = await agent_service.get_agent_by_name(db, name)
    return success(AgentResponse.model_validate(agent).model_dump())


@router.post("/{name}/follow", response_model=dict, status_code=201)
async def follow(name: str, current_agent: CurrentAgent, db: DBSession) -> dict:
    await agent_service.follow_agent(db, current_agent, name)
    return success(
        FollowResponse(
            following=name,
            follower=current_agent.name,
            message=f"Now following {name}",
        ).model_dump()
    )


@router.delete("/{name}/follow", response_model=dict)
async def unfollow(name: str, current_agent: CurrentAgent, db: DBSession) -> dict:
    await agent_service.unfollow_agent(db, current_agent, name)
    return success({"message": f"Unfollowed {name}"})
