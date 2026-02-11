from datetime import datetime
import uuid

from pydantic import BaseModel

from app.schemas.common import BaseSchema


class LessonListItem(BaseSchema):
    id: uuid.UUID
    group_id: uuid.UUID
    teacher_name: str | None = None
    cabinet_text: str | None = None
    starts_at: datetime
    ends_at: datetime
    topic: str | None = None
    plan_text: str | None = None
    status: str


class LessonListPage(BaseModel):
    items: list[LessonListItem]
    next_cursor: str | None = None


class LessonDetailOut(BaseSchema):
    id: uuid.UUID
    title: str | None = None
    description: str | None = None
    starts_at: datetime
    duration_minutes: int
    teacher_name: str | None = None
    cabinet_text: str | None = None


class WillGoRequest(BaseModel):
    student_id: uuid.UUID
    will_go: bool | None = None
