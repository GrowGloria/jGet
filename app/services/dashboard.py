from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.models.device_token import DeviceToken
from app.models.group import Group
from app.models.lesson import Lesson, LessonParticipation
from app.models.manager import Manager
from app.models.material import Material
from app.models.notification import Notification
from app.models.payment import Payment
from app.models.student import Student
from app.models.user import User
from app.schemas.dashboard import (
    DashboardRange,
    DashboardResponse,
    DashboardTable,
    DashboardTableRow,
    DashboardTotals,
    DashboardWeek,
)


def _date_list(start_date: date, end_date: date) -> list[date]:
    days: list[date] = []
    current = start_date
    while current <= end_date:
        days.append(current)
        current += timedelta(days=1)
    return days


def _rows_count(dates: list[date], count_map: dict[date, int]) -> list[DashboardTableRow]:
    return [DashboardTableRow(date=day, count=int(count_map.get(day, 0))) for day in dates]


async def _daily_count(
    session: AsyncSession,
    column,
    start_at: datetime,
    end_at: datetime,
):
    result = await session.execute(
        select(
            func.date_trunc("day", column).label("day"),
            func.count().label("count"),
        )
        .where(column >= start_at, column < end_at)
        .group_by("day")
        .order_by("day")
    )
    return {row.day.date(): int(row.count) for row in result.all()}


async def _total_count(session: AsyncSession, model):
    return int((await session.execute(select(func.count()).select_from(model))).scalar_one())


async def build_weekly_dashboard(session: AsyncSession, days: int = 7) -> DashboardResponse:
    tz = ZoneInfo(settings.TIMEZONE)
    today = datetime.now(tz).date()
    start_date = today - timedelta(days=days - 1)
    start_at = datetime.combine(start_date, time.min, tzinfo=tz)
    end_at = datetime.combine(today + timedelta(days=1), time.min, tzinfo=tz)

    date_list = _date_list(start_date, today)

    # Totals
    totals_users = await _total_count(session, User)
    totals_groups = await _total_count(session, Group)
    totals_students = await _total_count(session, Student)
    totals_lessons = await _total_count(session, Lesson)
    totals_lesson_parts = await _total_count(session, LessonParticipation)
    totals_materials = await _total_count(session, Material)
    totals_notifications = await _total_count(session, Notification)
    totals_payments = await _total_count(session, Payment)
    totals_device_tokens = await _total_count(session, DeviceToken)
    totals_managers = await _total_count(session, Manager)

    user_type_rows = await session.execute(
        select(User.user_type, func.count()).group_by(User.user_type)
    )
    users_by_type = {row[0]: int(row[1]) for row in user_type_rows.all()}

    # Weekly counts
    users_week = await _daily_count(session, User.created_at, start_at, end_at)
    groups_week = await _daily_count(session, Group.created_at, start_at, end_at)
    students_week = await _daily_count(session, Student.created_at, start_at, end_at)
    lessons_created_week = await _daily_count(session, Lesson.created_at, start_at, end_at)
    lessons_starting_week = await _daily_count(session, Lesson.starts_at, start_at, end_at)
    lesson_parts_week = await _daily_count(session, LessonParticipation.updated_at, start_at, end_at)
    materials_week = await _daily_count(session, Material.created_at, start_at, end_at)
    notifications_week = await _daily_count(session, Notification.created_at, start_at, end_at)
    payments_week = await _daily_count(session, Payment.created_at, start_at, end_at)
    device_tokens_week = await _daily_count(session, DeviceToken.created_at, start_at, end_at)
    managers_week = await _daily_count(session, Manager.created_at, start_at, end_at)

    payments_agg = await session.execute(
        select(
            func.date_trunc("day", Payment.created_at).label("day"),
            func.count().label("count"),
            func.coalesce(func.sum(Payment.amount_cents), 0).label("amount_cents"),
            func.coalesce(
                func.sum(case((Payment.status == "paid", 1), else_=0)), 0
            ).label("paid_count"),
            func.coalesce(
                func.sum(
                    case((Payment.status == "paid", Payment.amount_cents), else_=0)
                ),
                0,
            ).label("paid_amount_cents"),
        )
        .where(Payment.created_at >= start_at, Payment.created_at < end_at)
        .group_by("day")
        .order_by("day")
    )
    payments_by_day: dict[date, dict[str, int]] = {}
    for row in payments_agg.all():
        payments_by_day[row.day.date()] = {
            "count": int(row.count),
            "amount_cents": int(row.amount_cents),
            "paid_count": int(row.paid_count),
            "paid_amount_cents": int(row.paid_amount_cents),
        }

    # Weekly totals (derived from daily maps)
    week = DashboardWeek(
        users_created=sum(users_week.values()),
        groups_created=sum(groups_week.values()),
        students_created=sum(students_week.values()),
        lessons_created=sum(lessons_created_week.values()),
        lessons_starting=sum(lessons_starting_week.values()),
        lesson_participations_updated=sum(lesson_parts_week.values()),
        materials_created=sum(materials_week.values()),
        notifications_created=sum(notifications_week.values()),
        payments_created=sum(payments_week.values()),
        payments_amount_cents=sum(item["amount_cents"] for item in payments_by_day.values()),
        payments_paid=sum(item["paid_count"] for item in payments_by_day.values()),
        payments_paid_amount_cents=sum(item["paid_amount_cents"] for item in payments_by_day.values()),
        device_tokens_created=sum(device_tokens_week.values()),
        managers_created=sum(managers_week.values()),
    )

    tables: list[DashboardTable] = [
        DashboardTable(name="users_by_day", rows=_rows_count(date_list, users_week)),
        DashboardTable(name="groups_by_day", rows=_rows_count(date_list, groups_week)),
        DashboardTable(name="students_by_day", rows=_rows_count(date_list, students_week)),
        DashboardTable(
            name="lessons_by_day",
            rows=[
                DashboardTableRow(
                    date=day,
                    created=int(lessons_created_week.get(day, 0)),
                    starting=int(lessons_starting_week.get(day, 0)),
                )
                for day in date_list
            ],
        ),
        DashboardTable(
            name="lesson_participations_by_day",
            rows=_rows_count(date_list, lesson_parts_week),
        ),
        DashboardTable(name="materials_by_day", rows=_rows_count(date_list, materials_week)),
        DashboardTable(name="notifications_by_day", rows=_rows_count(date_list, notifications_week)),
        DashboardTable(
            name="payments_by_day",
            rows=[
                DashboardTableRow(
                    date=day,
                    count=int(payments_by_day.get(day, {}).get("count", 0)),
                    amount_cents=int(payments_by_day.get(day, {}).get("amount_cents", 0)),
                    paid_count=int(payments_by_day.get(day, {}).get("paid_count", 0)),
                    paid_amount_cents=int(payments_by_day.get(day, {}).get("paid_amount_cents", 0)),
                )
                for day in date_list
            ],
        ),
        DashboardTable(name="device_tokens_by_day", rows=_rows_count(date_list, device_tokens_week)),
        DashboardTable(name="managers_by_day", rows=_rows_count(date_list, managers_week)),
    ]

    return DashboardResponse(
        range=DashboardRange(
            from_date=start_date,
            to_date=today,
            days=days,
            timezone=settings.TIMEZONE,
        ),
        totals=DashboardTotals(
            users=totals_users,
            users_admin=int(users_by_type.get("admin", 0)),
            users_parent=int(users_by_type.get("parent", 0)),
            groups=totals_groups,
            students=totals_students,
            lessons=totals_lessons,
            lesson_participations=totals_lesson_parts,
            materials=totals_materials,
            notifications=totals_notifications,
            payments=totals_payments,
            device_tokens=totals_device_tokens,
            managers=totals_managers,
        ),
        week=week,
        tables=tables,
    )
