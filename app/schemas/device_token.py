from datetime import datetime
import uuid

from pydantic import BaseModel

from app.schemas.common import BaseSchema


class DeviceTokenCreate(BaseModel):
    token: str
    platform: str | None = None


class DeviceTokenOut(BaseSchema):
    id: uuid.UUID
    token: str
    platform: str | None = None
    created_at: datetime
    revoked_at: datetime | None = None
