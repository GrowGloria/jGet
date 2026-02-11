from datetime import datetime, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device_token import DeviceToken


async def register_device_token(
    session: AsyncSession,
    user_id: uuid.UUID,
    token: str,
    platform: str | None,
) -> DeviceToken:
    stmt = insert(DeviceToken).values(
        user_id=user_id,
        token=token,
        platform=platform,
        revoked_at=None,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "token"],
        set_={"platform": platform, "revoked_at": None},
    ).returning(DeviceToken.id)
    result = await session.execute(stmt)
    token_id = result.scalar_one()
    await session.commit()
    return await session.get(DeviceToken, token_id)


async def revoke_device_token(session: AsyncSession, user_id: uuid.UUID, token_id: uuid.UUID) -> DeviceToken | None:
    result = await session.execute(
        select(DeviceToken).where(DeviceToken.id == token_id, DeviceToken.user_id == user_id)
    )
    token = result.scalar_one_or_none()
    if not token:
        return None
    token.revoked_at = datetime.now(timezone.utc)
    await session.commit()
    return token
