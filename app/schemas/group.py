from datetime import datetime
import uuid

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class GroupCreate(BaseModel):
    name: str
    course_title: str | None = None
    course_description: str | None = None
    default_teacher_name: str | None = None
    capacity: int | None = None
    is_active: bool = True
    schedule_json: list[dict] = Field(default_factory=list)


class GroupUpdate(BaseModel):
    name: str | None = None
    course_title: str | None = None
    course_description: str | None = None
    default_teacher_name: str | None = None
    capacity: int | None = None
    is_active: bool | None = None
    schedule_json: list[dict] | None = None


class GroupOut(BaseSchema):
    id: uuid.UUID
    name: str
    course_title: str | None = None
    course_description: str | None = None
    default_teacher_name: str | None = None
    capacity: int | None = None
    is_active: bool
    schedule_json: list[dict]
    created_at: datetime
    updated_at: datetime
