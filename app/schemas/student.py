from datetime import date, datetime
import uuid

from pydantic import BaseModel

from app.schemas.common import BaseSchema


class StudentCreate(BaseModel):
    group_id: uuid.UUID
    first_name: str
    last_name: str
    father_name: str | None = None
    birthdate: date | None = None
    is_active: bool = True


class StudentOut(BaseSchema):
    id: uuid.UUID
    parent_user_id: uuid.UUID
    group_id: uuid.UUID
    first_name: str
    last_name: str
    father_name: str | None = None
    birthdate: date | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
