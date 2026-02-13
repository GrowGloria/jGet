from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_user_by_id_param
from app.core.db import get_session
from app.schemas.payment import PaymentCreateRequest, PaymentOut, PaymentWebhookRequest, PaymentsPage
from app.services.payments import create_payment, handle_webhook, list_payments

router = APIRouter(tags=["payments"])


@router.post("/payments/create", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def create_payment_route(
    payload: PaymentCreateRequest,
    user=Depends(get_user_by_id_param),
    session: AsyncSession = Depends(get_session),
):
    return await create_payment(
        session,
        user.id,
        payload.amount_cents,
        payload.currency,
        payload.provider,
        payload.provider_payment_id,
        payload.student_id,
        payload.lesson_id,
    )


@router.post("/payments/webhook/{provider}")
async def webhook(provider: str, payload: PaymentWebhookRequest, session: AsyncSession = Depends(get_session)):
    payment = await handle_webhook(session, provider, payload)
    return {"id": payment.id, "status": payment.status}


@router.get("/payments", response_model=PaymentsPage)
async def list_payments_route(
    limit: int = 20,
    cursor: str | None = None,
    user=Depends(get_user_by_id_param),
    session: AsyncSession = Depends(get_session),
):
    items, next_cursor = await list_payments(session, user.id, limit, cursor)
    return PaymentsPage(items=items, next_cursor=next_cursor)
