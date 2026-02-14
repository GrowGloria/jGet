from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import build_weekly_dashboard

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/weekly", response_model=DashboardResponse)
async def weekly_dashboard(session: AsyncSession = Depends(get_session)):
    return await build_weekly_dashboard(session)
