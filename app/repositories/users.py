import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user_by_email_or_phone(session: AsyncSession, email: str | None, phone: str | None) -> User | None:
    if email:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    if phone:
        result = await session.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()
    return None


async def get_user_by_email_or_phone_any(session: AsyncSession, email: str | None, phone: str | None) -> User | None:
    if email and phone:
        result = await session.execute(select(User).where((User.email == email) | (User.phone == phone)))
        return result.scalars().first()
    return await get_user_by_email_or_phone(session, email, phone)


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
