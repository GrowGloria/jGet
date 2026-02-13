from datetime import datetime, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Conflict, Forbidden, NotFound, Unauthorized
from app.core.security import hash_password, verify_password
from app.models.group import Group
from app.models.student import Student
from app.models.user import User
from app.repositories.users import get_user_by_email_or_phone, get_user_by_email_or_phone_any


async def register_parent(
    session: AsyncSession,
    email: str | None,
    phone: str,
    password: str,
    first_name: str,
    last_name: str,
    father_name: str | None,
    timezone_str: str | None,
    avatar_url: str | None,
    child_first_name: str,
    child_last_name: str,
    child_father_name: str | None,
    child_class: str,
    group_number: str,
) -> User:
    group = await _resolve_group(session, group_number)

    if email:
        existing = await get_user_by_email_or_phone(session, email, None)
        if existing:
            raise Conflict("AUTH_EMAIL_IN_USE", "Email already in use")
    if phone:
        existing = await get_user_by_email_or_phone(session, None, phone)
        if existing:
            raise Conflict("AUTH_PHONE_IN_USE", "Phone already in use")

    user = User(
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        user_type="parent",
        first_name=first_name,
        last_name=last_name,
        father_name=father_name,
        avatar_url=avatar_url,
        timezone=timezone_str or "Europe/Vienna",
        settings_json={},
        push_enabled=True,
    )
    session.add(user)
    await session.flush()

    student = Student(
        parent_user_id=user.id,
        group_id=group.id,
        first_name=child_first_name,
        last_name=child_last_name,
        father_name=child_father_name,
        school_class=child_class,
        group_number=group_number,
        is_active=True,
    )
    session.add(student)

    await session.commit()
    return user


async def login(
    session: AsyncSession,
    email: str | None,
    phone: str | None,
    password: str,
) -> User:
    user = await get_user_by_email_or_phone(session, email, phone)
    if not user:
        raise Forbidden("AUTH_USER_NOT_FOUND", "User not found")
    if not user.password_hash:
        raise Unauthorized("AUTH_INVALID_CREDENTIALS", "Invalid credentials")
    if not verify_password(password, user.password_hash):
        raise Unauthorized("AUTH_INVALID_CREDENTIALS", "Invalid credentials")

    user.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return user


async def check_user_exists(session: AsyncSession, email: str | None, phone: str | None) -> User:
    user = await get_user_by_email_or_phone_any(session, email, phone)
    if not user:
        raise Forbidden("AUTH_USER_NOT_FOUND", "User not found")
    return user


async def _resolve_group(session: AsyncSession, group_number: str) -> Group:
    try:
        group_id = uuid.UUID(group_number)
    except ValueError:
        group_id = None

    group = None
    if group_id:
        group = await session.get(Group, group_id)
    if not group:
        result = await session.execute(select(Group).where(Group.name == group_number))
        group = result.scalars().first()
    if not group:
        raise NotFound("GROUP_NOT_FOUND", "Group not found")
    return group
