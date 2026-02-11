import uuid

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.errors import Forbidden, Unauthorized
from app.core.security import decode_token
from app.models.user import User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not credentials:
        raise Unauthorized("AUTH_MISSING_TOKEN", "Missing token")

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise Unauthorized("AUTH_INVALID_TOKEN", "Invalid token")

    if payload.get("type") != "access":
        raise Unauthorized("AUTH_INVALID_TOKEN", "Invalid token")

    user_id = uuid.UUID(payload.get("sub"))
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise Unauthorized("AUTH_INVALID_TOKEN", "Invalid token")

    request.state.user_id = user.id
    return user


def require_user_type(*user_types: str):
    async def _dependency(user: User = Depends(get_current_user)) -> User:
        if user.user_type not in user_types:
            raise Forbidden("FORBIDDEN", "Forbidden")
        return user

    return _dependency


def require_admin():
    return require_user_type("admin")


def require_parent():
    return require_user_type("parent")
