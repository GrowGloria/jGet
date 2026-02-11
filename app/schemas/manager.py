from datetime import datetime
import uuid

from pydantic import BaseModel

from app.schemas.common import BaseSchema


class ManagerUpsert(BaseModel):
    id: uuid.UUID | None = None
    first_name: str
    last_name: str
    father_name: str | None = None
    telegram_url: str | None = None
    whatsapp_url: str | None = None


class ManagerOut(BaseSchema):
    id: uuid.UUID
    first_name: str
    last_name: str
    father_name: str | None = None
    telegram_url: str | None = None
    whatsapp_url: str | None = None
    created_at: datetime
