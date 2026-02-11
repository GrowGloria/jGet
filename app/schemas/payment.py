from datetime import datetime
import uuid

from pydantic import BaseModel, Field, model_validator

from app.models.enums import PaymentStatus
from app.schemas.common import BaseSchema


class PaymentCreateRequest(BaseModel):
    amount_cents: int = Field(gt=0)
    currency: str = "EUR"
    provider: str | None = None
    provider_payment_id: str | None = None
    student_id: uuid.UUID
    lesson_id: uuid.UUID


class PaymentOut(BaseSchema):
    id: uuid.UUID
    parent_user_id: uuid.UUID
    student_id: uuid.UUID | None = None
    group_id: uuid.UUID | None = None
    lesson_id: uuid.UUID | None = None
    amount_cents: int
    currency: str
    provider: str | None = None
    provider_payment_id: str | None = None
    status: PaymentStatus
    created_at: datetime
    paid_at: datetime | None = None


class PaymentWebhookRequest(BaseModel):
    provider_payment_id: str
    status: PaymentStatus


class PaymentsPage(BaseModel):
    items: list[PaymentOut]
    next_cursor: str | None = None
