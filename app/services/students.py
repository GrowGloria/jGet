import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.models.group import Group
from app.models.student import Student


async def list_parent_students(session: AsyncSession, user_id: uuid.UUID) -> list[Student]:
    result = await session.execute(select(Student).where(Student.parent_user_id == user_id))
    return result.scalars().all()


async def create_student(
    session: AsyncSession,
    user_id: uuid.UUID,
    group_id: uuid.UUID,
    first_name: str,
    last_name: str,
    father_name: str | None,
    birthdate,
    is_active: bool,
) -> Student:
    group = await session.get(Group, group_id)
    if not group:
        raise NotFound("GROUP_NOT_FOUND", "Group not found")

    student = Student(
        parent_user_id=user_id,
        group_id=group_id,
        first_name=first_name,
        last_name=last_name,
        father_name=father_name,
        birthdate=birthdate,
        is_active=is_active,
    )
    session.add(student)
    await session.commit()
    return student
