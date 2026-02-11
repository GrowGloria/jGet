from sqlalchemy import Boolean, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Group(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    course_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    course_description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    default_teacher_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    schedule_json: Mapped[list[dict]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"), nullable=False)
