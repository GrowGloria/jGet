from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import BadRequest
from app.core.pagination import decode_cursor, encode_cursor
from app.models.material import Material


async def list_materials(session: AsyncSession, group_id, limit: int, cursor: str | None):
    limit = max(1, min(limit, 50))
    stmt = (
        select(Material)
        .where(Material.group_id == group_id)
        .order_by(desc(Material.created_at), desc(Material.id))
        .limit(limit)
    )
    if cursor:
        try:
            created_at, item_id = decode_cursor(cursor)
        except Exception as exc:
            raise BadRequest("CURSOR_INVALID", "Invalid cursor") from exc
        stmt = stmt.where(
            (Material.created_at < created_at)
            | ((Material.created_at == created_at) & (Material.id < item_id))
        )
    result = await session.execute(stmt)
    items = result.scalars().all()

    next_cursor = None
    if len(items) == limit:
        last = items[-1]
        next_cursor = encode_cursor(last.created_at, last.id)

    return items, next_cursor


async def create_material(session: AsyncSession, material: Material) -> Material:
    session.add(material)
    await session.commit()
    return material


async def get_material(session: AsyncSession, material_id):
    result = await session.execute(select(Material).where(Material.id == material_id))
    return result.scalar_one_or_none()
