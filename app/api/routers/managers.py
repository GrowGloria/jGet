from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.db import get_session
from app.schemas.manager import ManagerOut, ManagerUpsert
from app.services.managers import list_managers, upsert_manager

router = APIRouter(tags=["managers"])


@router.get("/managers", response_model=list[ManagerOut])
async def list_managers_route(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await list_managers(session)


@router.post("/managers", response_model=ManagerOut, status_code=status.HTTP_201_CREATED)
async def upsert_manager_route(
    payload: ManagerUpsert,
    user=Depends(require_admin()),
    session: AsyncSession = Depends(get_session),
):
    return await upsert_manager(
        session,
        payload.id,
        payload.first_name,
        payload.last_name,
        payload.father_name,
        payload.telegram_url,
        payload.whatsapp_url,
    )
