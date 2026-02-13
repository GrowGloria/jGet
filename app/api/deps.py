import uuid

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.errors import NotFound
from app.models.user import User
from app.repositories.users import get_user_by_id


async def get_user_by_id_param(
    user_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_session),
) -> User:
    user = await get_user_by_id(session, user_id)
    if not user:
        raise NotFound("USER_NOT_FOUND", "User not found")
    return user
