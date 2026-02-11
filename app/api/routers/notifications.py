import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_session
from app.core.errors import NotFound
from app.schemas.notification import NotificationOut, NotificationsPage
from app.services.notifications import list_notifications, mark_read

router = APIRouter(tags=["notifications"])


@router.get("/notifications", response_model=NotificationsPage)
async def list_notifications_route(
    limit: int = 20,
    cursor: str | None = None,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    items, next_cursor = await list_notifications(session, user.id, limit, cursor)
    return NotificationsPage(items=items, next_cursor=next_cursor)


@router.post("/notifications/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: uuid.UUID,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    notification = await mark_read(session, user.id, notification_id)
    if not notification:
        raise NotFound("NOTIFICATION_NOT_FOUND", "Notification not found")
    return notification
