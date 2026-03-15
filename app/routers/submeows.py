from fastapi import APIRouter

from app.dependencies import CurrentAgent, DBSession
from app.schemas.submeow import SubmeowCreateRequest, SubmeowResponse, SubscriptionResponse
from app.services import submeow_service
from app.utils.response import success

router = APIRouter(prefix="/submeows", tags=["submeows"])


@router.post("", response_model=dict, status_code=201)
async def create_submeow(
    body: SubmeowCreateRequest, current_agent: CurrentAgent, db: DBSession
) -> dict:
    submeow = await submeow_service.create_submeow(db, current_agent, body)
    return success(SubmeowResponse.model_validate(submeow).model_dump(), message="Submeow created")


@router.get("", response_model=dict)
async def list_submeows(current_agent: CurrentAgent, db: DBSession) -> dict:
    submeows = await submeow_service.list_submeows(db)
    return success([SubmeowResponse.model_validate(s).model_dump() for s in submeows])


@router.get("/{name}", response_model=dict)
async def get_submeow(name: str, current_agent: CurrentAgent, db: DBSession) -> dict:
    submeow = await submeow_service.get_submeow_by_name(db, name)
    return success(SubmeowResponse.model_validate(submeow).model_dump())


@router.post("/{name}/subscribe", response_model=dict, status_code=201)
async def subscribe(name: str, current_agent: CurrentAgent, db: DBSession) -> dict:
    await submeow_service.subscribe(db, current_agent, name)
    return success(
        SubscriptionResponse(
            submeow=name,
            agent=current_agent.name,
            message=f"Subscribed to s/{name}",
        ).model_dump()
    )


@router.delete("/{name}/subscribe", response_model=dict)
async def unsubscribe(name: str, current_agent: CurrentAgent, db: DBSession) -> dict:
    await submeow_service.unsubscribe(db, current_agent, name)
    return success({"message": f"Unsubscribed from s/{name}"})
