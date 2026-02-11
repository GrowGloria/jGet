import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.core.db import get_session
from app.schemas.group import GroupCreate, GroupOut, GroupUpdate
from app.services.groups import create_group, list_groups, update_group

router = APIRouter(tags=["groups"])


@router.get("/groups", response_model=list[GroupOut])
async def list_groups_route(session: AsyncSession = Depends(get_session)):
    return await list_groups(session)


@router.post("/groups", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
async def create_group_route(
    payload: GroupCreate,
    user=Depends(require_admin()),
    session: AsyncSession = Depends(get_session),
):
    return await create_group(
        session,
        payload.name,
        payload.course_title,
        payload.course_description,
        payload.default_teacher_name,
        payload.capacity,
        payload.is_active,
        payload.schedule_json,
    )


@router.patch("/groups/{group_id}", response_model=GroupOut)
async def update_group_route(
    group_id: uuid.UUID,
    payload: GroupUpdate,
    user=Depends(require_admin()),
    session: AsyncSession = Depends(get_session),
):
    return await update_group(
        session,
        group_id,
        payload.name,
        payload.course_title,
        payload.course_description,
        payload.default_teacher_name,
        payload.capacity,
        payload.is_active,
        payload.schedule_json,
    )
