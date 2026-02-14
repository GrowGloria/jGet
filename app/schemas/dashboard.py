from datetime import date

from pydantic import BaseModel


class DashboardRange(BaseModel):
    from_date: date
    to_date: date
    days: int
    timezone: str


class DashboardTotals(BaseModel):
    users: int
    users_admin: int
    users_parent: int
    groups: int
    students: int
    lessons: int
    lesson_participations: int
    materials: int
    notifications: int
    payments: int
    device_tokens: int
    managers: int


class DashboardWeek(BaseModel):
    users_created: int
    groups_created: int
    students_created: int
    lessons_created: int
    lessons_starting: int
    lesson_participations_updated: int
    materials_created: int
    notifications_created: int
    payments_created: int
    payments_amount_cents: int
    payments_paid: int
    payments_paid_amount_cents: int
    device_tokens_created: int
    managers_created: int


class DashboardTableRow(BaseModel):
    date: date
    count: int | None = None
    created: int | None = None
    starting: int | None = None
    amount_cents: int | None = None
    paid_count: int | None = None
    paid_amount_cents: int | None = None


class DashboardTable(BaseModel):
    name: str
    rows: list[DashboardTableRow]


class DashboardResponse(BaseModel):
    range: DashboardRange
    totals: DashboardTotals
    week: DashboardWeek
    tables: list[DashboardTable]
