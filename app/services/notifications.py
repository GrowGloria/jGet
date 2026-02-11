from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import BadRequest
from app.core.pagination import decode_cursor, encode_cursor
from app.models.lesson import Lesson
from app.models.notification import Notification
from app.models.student import Student


async def list_notifications(session: AsyncSession, user_id: uuid.UUID, limit: int, cursor: str | None):
    limit = max(1, min(limit, 50))
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .limit(limit)
    )
    if cursor:
        try:
            created_at, item_id = decode_cursor(cursor)
        except Exception as exc:
            raise BadRequest("CURSOR_INVALID", "Invalid cursor") from exc
        stmt = stmt.where(
            (Notification.created_at < created_at)
            | ((Notification.created_at == created_at) & (Notification.id < item_id))
        )

    result = await session.execute(stmt)
    items = result.scalars().all()

    next_cursor = None
    if len(items) == limit:
        last = items[-1]
        next_cursor = encode_cursor(last.created_at, last.id)

    return items, next_cursor


async def mark_read(session: AsyncSession, user_id: uuid.UUID, notification_id: uuid.UUID) -> Notification | None:
    result = await session.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        return None
    notification.status = "read"
    notification.read_at = datetime.now(timezone.utc)
    await session.commit()
    return notification


async def enqueue_lesson_reminders(session: AsyncSession) -> int:
    now = datetime.now(timezone.utc)
    window_start = now + timedelta(hours=23)
    window_end = now + timedelta(hours=25)

    lessons_result = await session.execute(
        select(Lesson).where(Lesson.starts_at >= window_start, Lesson.starts_at <= window_end)
    )
    lessons = lessons_result.scalars().all()

    created = 0
    for lesson in lessons:
        parent_rows = await session.execute(
            select(Student.parent_user_id).where(Student.group_id == lesson.group_id).distinct()
        )
        user_ids = [row[0] for row in parent_rows.all()]
        if not user_ids:
            continue

        existing = await session.execute(
            select(Notification.user_id)
            .where(
                Notification.user_id.in_(user_ids),
                Notification.type == "lesson_reminder",
                Notification.payload["lesson_id"].astext == str(lesson.id),
            )
        )
        existing_user_ids = {row[0] for row in existing.all()}

        for user_id in user_ids:
            if user_id in existing_user_ids:
                continue
            session.add(
                Notification(
                    user_id=user_id,
                    type="lesson_reminder",
                    title="Lesson reminder",
                    body="Lesson starts soon",
                    payload={"lesson_id": str(lesson.id), "group_id": str(lesson.group_id)},
                    status="queued",
                    scheduled_at=now,
                )
            )
            created += 1

    await session.commit()
    return created
