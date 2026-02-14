from datetime import date, datetime, time, timedelta
import uuid
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_user_by_id_param
from app.core.db import get_session
from app.core.errors import BadRequest
from app.core.settings import settings
from app.schemas.lesson import (
    LessonCreate,
    LessonDetailOut,
    LessonListPage,
    LessonOut,
    LessonUpdate,
    WillGoRequest,
)
from app.services.lessons import (
    create_lesson,
    get_lesson_for_user,
    list_lessons_for_user,
    list_lessons_in_range,
    update_lesson,
    upsert_will_go,
)
from app.utils.time import now_tz

router = APIRouter(tags=["lessons"])


@router.get("/lessons", response_model=LessonListPage)
async def list_lessons(
    limit: int = 20,
    cursor: str | None = None,
    user=Depends(get_user_by_id_param),
    session: AsyncSession = Depends(get_session),
):
    items, next_cursor = await list_lessons_for_user(session, user, limit, cursor)
    return LessonListPage(items=items, next_cursor=next_cursor)


@router.post("/lessons", response_model=LessonOut, status_code=201)
async def create_lesson_route(payload: LessonCreate, session: AsyncSession = Depends(get_session)):
    return await create_lesson(
        session,
        payload.group_id,
        payload.starts_at,
        payload.ends_at,
        payload.topic,
        payload.plan_text,
        payload.teacher_name,
        payload.cabinet_text,
        payload.status,
    )


@router.get("/lessons/month", response_model=LessonListPage)
async def list_lessons_month(
    year: int | None = None,
    month: int | None = None,
    limit: int = 100,
    cursor: str | None = None,
    user=Depends(get_user_by_id_param),
    session: AsyncSession = Depends(get_session),
):
    now = now_tz()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    if month < 1 or month > 12:
        raise BadRequest("MONTH_INVALID", "Invalid month")

    tz = now.tzinfo or ZoneInfo(settings.TIMEZONE)
    start_at = datetime(year, month, 1, tzinfo=tz)
    if month == 12:
        end_at = datetime(year + 1, 1, 1, tzinfo=tz)
    else:
        end_at = datetime(year, month + 1, 1, tzinfo=tz)

    items, next_cursor = await list_lessons_in_range(
        session,
        user,
        start_at,
        end_at,
        limit,
        cursor,
        max_limit=100,
    )
    return LessonListPage(items=items, next_cursor=next_cursor)


@router.get("/lessons/range", response_model=LessonListPage)
async def list_lessons_range(
    from_date: date = Query(alias="from"),
    to_date: date = Query(alias="to"),
    limit: int = 50,
    cursor: str | None = None,
    user=Depends(get_user_by_id_param),
    session: AsyncSession = Depends(get_session),
):
    if from_date > to_date:
        raise BadRequest("DATE_RANGE_INVALID", "Invalid date range")

    tz = ZoneInfo(settings.TIMEZONE)
    start_at = datetime.combine(from_date, time.min, tzinfo=tz)
    end_at = datetime.combine(to_date + timedelta(days=1), time.min, tzinfo=tz)

    items, next_cursor = await list_lessons_in_range(
        session,
        user,
        start_at,
        end_at,
        limit,
        cursor,
        max_limit=50,
    )
    return LessonListPage(items=items, next_cursor=next_cursor)


@router.patch("/lessons/{lesson_id}", response_model=LessonOut)
async def update_lesson_route(
    lesson_id: uuid.UUID,
    payload: LessonUpdate,
    session: AsyncSession = Depends(get_session),
):
    data = payload.model_dump(exclude_unset=True)
    return await update_lesson(session, lesson_id, data)


@router.get("/lessons/{lesson_id}", response_model=LessonDetailOut)
async def get_lesson(
    lesson_id: uuid.UUID,
    user=Depends(get_user_by_id_param),
    session: AsyncSession = Depends(get_session),
):
    lesson = await get_lesson_for_user(session, user, lesson_id)
    duration_minutes = int((lesson.ends_at - lesson.starts_at).total_seconds() / 60)
    return LessonDetailOut(
        id=lesson.id,
        title=lesson.topic,
        description=lesson.plan_text,
        starts_at=lesson.starts_at,
        duration_minutes=duration_minutes,
        teacher_name=lesson.teacher_name,
        cabinet_text=lesson.cabinet_text,
    )


@router.post("/lessons/{lesson_id}/will-go")
async def will_go(
    lesson_id: uuid.UUID,
    payload: WillGoRequest,
    user=Depends(get_user_by_id_param),
    session: AsyncSession = Depends(get_session),
):
    part = await upsert_will_go(session, user.id, lesson_id, payload.student_id, payload.will_go)
    return {"lesson_id": str(part.lesson_id), "student_id": str(part.student_id), "will_go": part.will_go}
