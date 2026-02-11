import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson


async def get_lesson(session: AsyncSession, lesson_id: uuid.UUID) -> Lesson | None:
    result = await session.execute(select(Lesson).where(Lesson.id == lesson_id))
    return result.scalar_one_or_none()
