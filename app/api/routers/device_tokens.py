import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_session
from app.core.errors import NotFound
from app.schemas.device_token import DeviceTokenCreate, DeviceTokenOut
from app.services.device_tokens import register_device_token, revoke_device_token

router = APIRouter(tags=["device_tokens"])


@router.post("/device-tokens", response_model=DeviceTokenOut, status_code=status.HTTP_201_CREATED)
async def register_token(
    payload: DeviceTokenCreate,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await register_device_token(session, user.id, payload.token, payload.platform)


@router.delete("/device-tokens/{token_id}")
async def revoke_token(
    token_id: uuid.UUID,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    token = await revoke_device_token(session, user.id, token_id)
    if not token:
        raise NotFound("DEVICE_TOKEN_NOT_FOUND", "Device token not found")
    return {"id": str(token.id), "revoked_at": token.revoked_at}
