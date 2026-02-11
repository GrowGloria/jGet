import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


async def get_payment(session: AsyncSession, payment_id: uuid.UUID) -> Payment | None:
    result = await session.execute(select(Payment).where(Payment.id == payment_id))
    return result.scalar_one_or_none()


async def get_payment_by_provider_id(session: AsyncSession, provider_payment_id: str) -> Payment | None:
    result = await session.execute(select(Payment).where(Payment.provider_payment_id == provider_payment_id))
    return result.scalar_one_or_none()
