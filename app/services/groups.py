import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Forbidden, NotFound
from app.models.group import Group
from app.models.student import Student
from app.models.user import User


async def list_groups(session: AsyncSession) -> list[Group]:
    result = await session.execute(select(Group).order_by(Group.created_at.desc()))
    return result.scalars().all()


async def create_group(
    session: AsyncSession,
    name: str,
    course_title: str | None,
    course_description: str | None,
    default_teacher_name: str | None,
    capacity: int | None,
    is_active: bool,
    schedule_json: list[dict],
) -> Group:
    group = Group(
        name=name,
        course_title=course_title,
        course_description=course_description,
        default_teacher_name=default_teacher_name,
        capacity=capacity,
        is_active=is_active,
        schedule_json=schedule_json,
    )
    session.add(group)
    await session.commit()
    return group


async def update_group(
    session: AsyncSession,
    group_id: uuid.UUID,
    name: str | None,
    course_title: str | None,
    course_description: str | None,
    default_teacher_name: str | None,
    capacity: int | None,
    is_active: bool | None,
    schedule_json: list[dict] | None,
) -> Group:
    group = await session.get(Group, group_id)
    if not group:
        raise NotFound("GROUP_NOT_FOUND", "Group not found")

    if name is not None:
        group.name = name
    if course_title is not None:
        group.course_title = course_title
    if course_description is not None:
        group.course_description = course_description
    if default_teacher_name is not None:
        group.default_teacher_name = default_teacher_name
    if capacity is not None:
        group.capacity = capacity
    if is_active is not None:
        group.is_active = is_active
    if schedule_json is not None:
        group.schedule_json = schedule_json

    await session.commit()
    return group


async def list_user_courses(session: AsyncSession, user: User) -> list[dict]:
    if user.user_type == "admin":
        stmt = select(Group)
    elif user.user_type == "parent":
        stmt = (
            select(Group)
            .join(Student, Student.group_id == Group.id)
            .where(Student.parent_user_id == user.id)
            .distinct()
        )
    else:
        raise Forbidden("FORBIDDEN", "Forbidden")

    result = await session.execute(stmt.order_by(Group.name.asc()))
    groups = result.scalars().all()
    return [
        {
            "group_id": group.id,
            "group_name": group.name,
            "course_title": group.course_title,
            "course_description": group.course_description,
        }
        for group in groups
    ]
