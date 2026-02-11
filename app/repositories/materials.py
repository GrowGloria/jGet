import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import Material


async def get_material(session: AsyncSession, material_id: uuid.UUID) -> Material | None:
    result = await session.execute(select(Material).where(Material.id == material_id))
    return result.scalar_one_or_none()
