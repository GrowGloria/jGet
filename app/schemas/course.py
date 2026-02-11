import uuid

from app.schemas.common import BaseSchema


class UserCourseOut(BaseSchema):
    group_id: uuid.UUID
    group_name: str
    course_title: str | None = None
    course_description: str | None = None
