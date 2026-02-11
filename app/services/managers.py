import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.models.manager import Manager


async def list_managers(session: AsyncSession) -> list[Manager]:
    result = await session.execute(select(Manager).order_by(Manager.created_at.desc()))
    return result.scalars().all()


async def upsert_manager(
    session: AsyncSession,
    manager_id: uuid.UUID | None,
    first_name: str,
    last_name: str,
    father_name: str | None,
    telegram_url: str | None,
    whatsapp_url: str | None,
) -> Manager:
    manager: Manager | None = None
    if manager_id:
        manager = await session.get(Manager, manager_id)
        if not manager:
            raise NotFound("MANAGER_NOT_FOUND", "Manager not found")
        manager.first_name = first_name
        manager.last_name = last_name
        manager.father_name = father_name
        manager.telegram_url = telegram_url
        manager.whatsapp_url = whatsapp_url
    else:
        manager = Manager(
            first_name=first_name,
            last_name=last_name,
            father_name=father_name,
            telegram_url=telegram_url,
            whatsapp_url=whatsapp_url,
        )
        session.add(manager)

    await session.commit()
    return manager
