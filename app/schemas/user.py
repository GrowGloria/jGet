from datetime import datetime
import uuid

from app.schemas.common import BaseSchema


class UserMeResponse(BaseSchema):
    id: uuid.UUID
    email: str | None = None
    phone: str | None = None
    user_type: str
    first_name: str | None = None
    last_name: str | None = None
    father_name: str | None = None
    avatar_url: str | None = None
    timezone: str | None = None
    settings_json: dict | None = None
    push_enabled: bool
    created_at: datetime
    updated_at: datetime
