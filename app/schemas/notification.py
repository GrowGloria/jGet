from datetime import datetime
import uuid

from pydantic import BaseModel

from app.models.enums import NotificationStatus
from app.schemas.common import BaseSchema


class NotificationOut(BaseSchema):
    id: uuid.UUID
    type: str
    title: str | None = None
    body: str | None = None
    payload: dict
    status: NotificationStatus
    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    read_at: datetime | None = None
    created_at: datetime


class NotificationsPage(BaseModel):
    items: list[NotificationOut]
    next_cursor: str | None = None
