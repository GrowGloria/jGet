from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    APP_NAME: str = "jGet"
    ENV: str = "local"
    DEBUG: bool = False

    API_PREFIX: str = ""

    DATABASE_URL: str = "postgresql+asyncpg://app:app@localhost:5432/app"

    TIMEZONE: str = "Europe/Vienna"
    UPLOAD_DIR: str = "./uploads"

    LOG_LEVEL: str = "INFO"

    ALLOWED_ORIGINS: list[str] = ["*"]

    NOTIFICATION_REMINDER_WINDOW_HOURS: int = 24


settings = Settings()
