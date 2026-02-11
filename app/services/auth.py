from datetime import datetime, timezone
import uuid

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Conflict, Forbidden, Unauthorized
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.core.settings import settings
from app.models.user import User
from app.repositories.users import get_user_by_email_or_phone, get_user_by_email_or_phone_any, get_user_by_id


def _token_pair(user_id: uuid.UUID) -> tuple[str, str, int, int]:
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    return access_token, refresh_token, settings.ACCESS_TTL, settings.REFRESH_TTL


async def register_parent(
    session: AsyncSession,
    email: str | None,
    phone: str | None,
    password: str,
    first_name: str | None,
    last_name: str | None,
    father_name: str | None,
    timezone_str: str | None,
    avatar_url: str | None,
) -> tuple[User, str, str, int, int]:
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

    access_token, refresh_token, access_ttl, refresh_ttl = _token_pair(user.id)
    await session.commit()
    return user, access_token, refresh_token, access_ttl, refresh_ttl


async def login(
    session: AsyncSession,
    email: str | None,
    phone: str | None,
    password: str,
) -> tuple[User, str, str, int, int]:
    user = await get_user_by_email_or_phone(session, email, phone)
    if not user or not user.password_hash:
        raise Unauthorized("AUTH_INVALID_CREDENTIALS", "Invalid credentials")
    if not verify_password(password, user.password_hash):
        raise Unauthorized("AUTH_INVALID_CREDENTIALS", "Invalid credentials")

    user.updated_at = datetime.now(timezone.utc)
    access_token, refresh_token, access_ttl, refresh_ttl = _token_pair(user.id)
    await session.commit()
    return user, access_token, refresh_token, access_ttl, refresh_ttl


async def refresh_tokens(session: AsyncSession, refresh_token: str) -> tuple[User, str, str, int, int]:
    try:
        payload = decode_token(refresh_token)
    except JWTError as exc:
        raise Unauthorized("AUTH_INVALID_TOKEN", "Invalid token") from exc

    if payload.get("type") != "refresh":
        raise Unauthorized("AUTH_INVALID_TOKEN", "Invalid token")

    user_id = uuid.UUID(payload.get("sub"))
    user = await get_user_by_id(session, user_id)
    if not user:
        raise Unauthorized("AUTH_INVALID_TOKEN", "Invalid token")

    access_token, new_refresh_token, access_ttl, refresh_ttl = _token_pair(user.id)
    return user, access_token, new_refresh_token, access_ttl, refresh_ttl


async def check_user_exists(session: AsyncSession, email: str | None, phone: str | None) -> User:
    user = await get_user_by_email_or_phone_any(session, email, phone)
    if not user:
        raise Forbidden("AUTH_USER_NOT_FOUND", "User not found")
    return user
