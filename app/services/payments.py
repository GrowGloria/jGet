from datetime import datetime, timezone
import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import BadRequest, Forbidden, NotFound
from app.core.pagination import decode_cursor, encode_cursor
from app.models.lesson import Lesson
from app.models.payment import Payment
from app.models.student import Student


async def create_payment(
    session: AsyncSession,
    user_id: uuid.UUID,
    amount_cents: int,
    currency: str,
    provider: str | None,
    provider_payment_id: str | None,
    student_id: uuid.UUID,
    lesson_id: uuid.UUID,
) -> Payment:
    student = await session.get(Student, student_id)
    if not student or student.parent_user_id != user_id:
        raise Forbidden("FORBIDDEN", "Student does not belong to parent")

    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        raise NotFound("LESSON_NOT_FOUND", "Lesson not found")
    if lesson.group_id != student.group_id:
        raise BadRequest("LESSON_NOT_IN_CHILD_GROUP", "Lesson not in child group")

    payment = Payment(
        parent_user_id=user_id,
        student_id=student_id,
        group_id=student.group_id,
        lesson_id=lesson_id,
        amount_cents=amount_cents,
        currency=currency,
        provider=provider,
        provider_payment_id=provider_payment_id,
        status="pending",
    )
    session.add(payment)
    await session.commit()
    return payment


async def handle_webhook(session: AsyncSession, provider: str, payload) -> Payment:
    result = await session.execute(
        select(Payment).where(Payment.provider == provider, Payment.provider_payment_id == payload.provider_payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise NotFound("PAYMENT_NOT_FOUND", "Payment not found")

    payment.status = payload.status
    if payload.status == "paid":
        payment.paid_at = datetime.now(timezone.utc)
    await session.commit()
    return payment


async def list_payments(session: AsyncSession, user_id: uuid.UUID, limit: int, cursor: str | None):
    limit = max(1, min(limit, 50))
    stmt = (
        select(Payment)
        .where(Payment.parent_user_id == user_id)
        .order_by(desc(Payment.created_at), desc(Payment.id))
        .limit(limit)
    )
    if cursor:
        try:
            created_at, item_id = decode_cursor(cursor)
        except Exception as exc:
            raise BadRequest("CURSOR_INVALID", "Invalid cursor") from exc
        stmt = stmt.where(
            (Payment.created_at < created_at) | ((Payment.created_at == created_at) & (Payment.id < item_id))
        )

    result = await session.execute(stmt)
    items = result.scalars().all()

    next_cursor = None
    if len(items) == limit:
        last = items[-1]
        next_cursor = encode_cursor(last.created_at, last.id)

    return items, next_cursor
