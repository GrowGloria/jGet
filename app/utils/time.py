from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.settings import settings


def now_tz() -> datetime:
    return datetime.now(ZoneInfo(settings.TIMEZONE))
