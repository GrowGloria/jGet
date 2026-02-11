from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.core.db import get_session
from app.services.lessons import generate_lessons
from app.services.notifications import enqueue_lesson_reminders

router = APIRouter(tags=["admin_jobs"])


@router.post("/admin/jobs/generate-lessons")
async def generate_lessons_job(
    days: int = 30,
    user=Depends(require_admin()),
    session: AsyncSession = Depends(get_session),
):
    created = await generate_lessons(session, days=days, actor_user_id=user.id)
    return {"created": created}


@router.post("/admin/jobs/enqueue-reminders")
async def enqueue_reminders_job(
    user=Depends(require_admin()),
    session: AsyncSession = Depends(get_session),
):
    created = await enqueue_lesson_reminders(session)
    return {"created": created}
