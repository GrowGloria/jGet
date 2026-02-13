import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.errors import BadRequest, NotFound
from app.models.material import Material
from app.schemas.material import (
    MaterialCreate,
    MaterialOut,
    MaterialShortOut,
    MaterialsPage,
    MaterialsShortPage,
)
from app.services.materials import create_material, get_material, list_materials

router = APIRouter(tags=["materials"])


@router.get("/materials/short", response_model=MaterialsShortPage)
async def list_materials_short(
    group_id: uuid.UUID | None = None,
    limit: int = 20,
    cursor: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    if not group_id:
        raise BadRequest("GROUP_ID_REQUIRED", "group_id is required")
    items, next_cursor = await list_materials(session, group_id, limit, cursor)
    short_items = [
        MaterialShortOut(
            id=item.id,
            group_id=item.group_id,
            title=item.title,
            type=item.type,
            created_at=item.created_at,
        )
        for item in items
    ]
    return MaterialsShortPage(items=short_items, next_cursor=next_cursor)


@router.get("/materials", response_model=MaterialsPage)
async def list_materials_route(
    group_id: uuid.UUID | None = None,
    limit: int = 20,
    cursor: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    if not group_id:
        raise BadRequest("GROUP_ID_REQUIRED", "group_id is required")
    items, next_cursor = await list_materials(session, group_id, limit, cursor)
    return MaterialsPage(items=items, next_cursor=next_cursor)


@router.post("/materials", response_model=MaterialOut, status_code=status.HTTP_201_CREATED)
async def create_material_route(
    payload: MaterialCreate,
    session: AsyncSession = Depends(get_session),
):
    material = Material(
        group_id=payload.group_id,
        title=payload.title,
        body_text=payload.body_text,
        type=payload.type,
        link_url=payload.link_url,
        is_published=payload.is_published,
    )
    return await create_material(session, material)


@router.get("/materials/{material_id}", response_model=MaterialOut)
async def material_detail(material_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    material = await get_material(session, material_id)
    if not material:
        raise NotFound("MATERIAL_NOT_FOUND", "Material not found")
    return material
