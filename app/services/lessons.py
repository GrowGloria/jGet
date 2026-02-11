from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import BadRequest, Forbidden, NotFound
from app.core.pagination import decode_cursor, encode_cursor
from app.core.settings import settings
from app.models.group import Group
from app.models.lesson import Lesson, LessonParticipation
from app.models.student import Student
from app.models.user import User


def _parse_schedule_item(item: dict) -> tuple[int, time, int, str | None] | None:
    try:
        weekday = int(item.get("weekday"))
        start_time_str = item.get("start_time")
        duration_minutes = int(item.get("duration_minutes"))
    except (TypeError, ValueError):
        return None

    if weekday < 1 or weekday > 7 or duration_minutes <= 0 or not start_time_str:
        return None
    try:
        start_time = time.fromisoformat(start_time_str)
    except ValueError:
        return None

    cabinet_text = item.get("cabinet_text")
    return weekday, start_time, duration_minutes, cabinet_text


async def generate_lessons(session: AsyncSession, days: int = 30, actor_user_id: uuid.UUID | None = None) -> int:
    tz = ZoneInfo(settings.TIMEZONE)
    today = datetime.now(tz).date()
    end_date = today + timedelta(days=days)

    groups_result = await session.execute(select(Group).where(Group.is_active.is_(True)))
    groups = groups_result.scalars().all()

    rows: list[dict] = []
    for group in groups:
        if not isinstance(group.schedule_json, list):
            continue
        for item in group.schedule_json:
            if not isinstance(item, dict):
                continue
            parsed = _parse_schedule_item(item)
            if not parsed:
                continue
            weekday, start_time, duration_minutes, cabinet_text = parsed

            days_ahead = (weekday - today.isoweekday()) % 7
            current = today + timedelta(days=days_ahead)

            while current <= end_date:
                starts_at = datetime.combine(current, start_time, tzinfo=tz)
                ends_at = starts_at + timedelta(minutes=duration_minutes)
                rows.append(
                    {
                        "group_id": group.id,
                        "teacher_name": group.default_teacher_name,
                        "cabinet_text": cabinet_text,
                        "starts_at": starts_at,
                        "ends_at": ends_at,
                        "status": "scheduled",
                    }
                )
                current += timedelta(days=7)

    if not rows:
        return 0

    stmt = (
        insert(Lesson.__table__)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["group_id", "starts_at"])
        .returning(Lesson.id)
    )
    result = await session.execute(stmt)
    inserted = result.all()
    await session.commit()
    return len(inserted)


async def list_parent_lessons(
    session: AsyncSession,
    user_id: uuid.UUID,
    limit: int,
    cursor: str | None,
):
    limit = max(1, min(limit, 50))

    stmt = (
        select(Lesson)
        .join(Student, Student.group_id == Lesson.group_id)
        .where(Student.parent_user_id == user_id)
        .distinct()
        .order_by(Lesson.starts_at.desc(), Lesson.id.desc())
        .limit(limit)
    )

    if cursor:
        try:
            starts_at, lesson_id = decode_cursor(cursor)
        except Exception as exc:
            raise BadRequest("CURSOR_INVALID", "Invalid cursor") from exc
        stmt = stmt.where(
            (Lesson.starts_at < starts_at) | ((Lesson.starts_at == starts_at) & (Lesson.id < lesson_id))
        )

    result = await session.execute(stmt)
    lessons = result.scalars().all()

    if not lessons:
        return [], None

    lesson_ids = [lesson.id for lesson in lessons]

    rows = await session.execute(
        select(
            Lesson.id,
            Student.id,
            Student.first_name,
            Student.last_name,
            Student.father_name,
            LessonParticipation.will_go,
        )
        .join(Student, Student.group_id == Lesson.group_id)
        .outerjoin(
            LessonParticipation,
            (LessonParticipation.lesson_id == Lesson.id) & (LessonParticipation.student_id == Student.id),
        )
        .where(Student.parent_user_id == user_id, Lesson.id.in_(lesson_ids))
    )

    students_map: dict[uuid.UUID, list[dict]] = {}
    for lesson_id, student_id, first_name, last_name, father_name, will_go in rows.all():
        students_map.setdefault(lesson_id, []).append(
            {
                "student_id": student_id,
                "first_name": first_name,
                "last_name": last_name,
                "father_name": father_name,
                "will_go": will_go,
            }
        )

    items = []
    for lesson in lessons:
        items.append(
            {
                "id": lesson.id,
                "group_id": lesson.group_id,
                "starts_at": lesson.starts_at,
                "ends_at": lesson.ends_at,
                "topic": lesson.topic,
                "teacher_name": lesson.teacher_name,
                "cabinet_text": lesson.cabinet_text,
                "status": lesson.status,
                "students": students_map.get(lesson.id, []),
            }
        )

    next_cursor = None
    if len(lessons) == limit:
        last = lessons[-1]
        next_cursor = encode_cursor(last.starts_at, last.id)

    return items, next_cursor


def _lessons_query_for_user(user: User):
    if user.user_type == "admin":
        return select(Lesson)
    if user.user_type == "parent":
        return (
            select(Lesson)
            .join(Student, Student.group_id == Lesson.group_id)
            .where(Student.parent_user_id == user.id)
            .distinct()
        )
    raise Forbidden("FORBIDDEN", "Forbidden")


def _lesson_list_item(lesson: Lesson) -> dict:
    return {
        "id": lesson.id,
        "group_id": lesson.group_id,
        "teacher_name": lesson.teacher_name,
        "cabinet_text": lesson.cabinet_text,
        "starts_at": lesson.starts_at,
        "ends_at": lesson.ends_at,
        "topic": lesson.topic,
        "plan_text": lesson.plan_text,
        "status": lesson.status,
    }


def _apply_cursor_desc(stmt, cursor: str | None):
    if not cursor:
        return stmt
    try:
        starts_at, lesson_id = decode_cursor(cursor)
    except Exception as exc:
        raise BadRequest("CURSOR_INVALID", "Invalid cursor") from exc
    return stmt.where((Lesson.starts_at < starts_at) | ((Lesson.starts_at == starts_at) & (Lesson.id < lesson_id)))


def _apply_cursor_asc(stmt, cursor: str | None):
    if not cursor:
        return stmt
    try:
        starts_at, lesson_id = decode_cursor(cursor)
    except Exception as exc:
        raise BadRequest("CURSOR_INVALID", "Invalid cursor") from exc
    return stmt.where((Lesson.starts_at > starts_at) | ((Lesson.starts_at == starts_at) & (Lesson.id > lesson_id)))


async def list_lessons_for_user(
    session: AsyncSession,
    user: User,
    limit: int,
    cursor: str | None,
):
    limit = max(1, min(limit, 50))
    stmt = _lessons_query_for_user(user).order_by(Lesson.starts_at.desc(), Lesson.id.desc()).limit(limit)
    stmt = _apply_cursor_desc(stmt, cursor)

    result = await session.execute(stmt)
    lessons = result.scalars().all()

    items = [_lesson_list_item(lesson) for lesson in lessons]

    next_cursor = None
    if len(lessons) == limit:
        last = lessons[-1]
        next_cursor = encode_cursor(last.starts_at, last.id)

    return items, next_cursor


async def list_lessons_in_range(
    session: AsyncSession,
    user: User,
    start_at: datetime,
    end_at: datetime,
    limit: int,
    cursor: str | None,
    max_limit: int,
):
    limit = max(1, min(limit, max_limit))
    stmt = (
        _lessons_query_for_user(user)
        .where(Lesson.starts_at >= start_at, Lesson.starts_at < end_at)
        .order_by(Lesson.starts_at.asc(), Lesson.id.asc())
        .limit(limit)
    )
    stmt = _apply_cursor_asc(stmt, cursor)

    result = await session.execute(stmt)
    lessons = result.scalars().all()
    items = [_lesson_list_item(lesson) for lesson in lessons]

    next_cursor = None
    if len(lessons) == limit:
        last = lessons[-1]
        next_cursor = encode_cursor(last.starts_at, last.id)

    return items, next_cursor


async def get_lesson_for_user(session: AsyncSession, user: User, lesson_id: uuid.UUID) -> Lesson:
    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        raise NotFound("LESSON_NOT_FOUND", "Lesson not found")

    if user.user_type == "admin":
        return lesson
    if user.user_type != "parent":
        raise Forbidden("FORBIDDEN", "Forbidden")

    result = await session.execute(
        select(Student.id).where(Student.parent_user_id == user.id, Student.group_id == lesson.group_id).limit(1)
    )
    if not result.scalar_one_or_none():
        raise Forbidden("FORBIDDEN", "Forbidden")
    return lesson


async def upsert_will_go(
    session: AsyncSession,
    user_id: uuid.UUID,
    lesson_id: uuid.UUID,
    student_id: uuid.UUID,
    will_go: bool | None,
) -> LessonParticipation:
    student = await session.get(Student, student_id)
    if not student or student.parent_user_id != user_id:
        raise Forbidden("FORBIDDEN", "Student does not belong to parent")

    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        raise NotFound("LESSON_NOT_FOUND", "Lesson not found")
    if student.group_id != lesson.group_id:
        raise BadRequest("LESSON_NOT_IN_CHILD_GROUP", "Lesson not in child group")

    stmt = insert(LessonParticipation).values(
        lesson_id=lesson_id,
        student_id=student_id,
        will_go=will_go,
        updated_at=datetime.now(timezone.utc),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["lesson_id", "student_id"],
        set_={
            "will_go": will_go,
            "updated_at": datetime.now(timezone.utc),
        },
    ).returning(LessonParticipation.lesson_id, LessonParticipation.student_id)

    await session.execute(stmt)
    await session.commit()

    return await session.get(LessonParticipation, (lesson_id, student_id))
