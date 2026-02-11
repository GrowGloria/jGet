from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.manager import Manager


async def list_managers(session: AsyncSession):
    result = await session.execute(select(Manager).order_by(Manager.created_at.desc()))
    return result.scalars().all()
