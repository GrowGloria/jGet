from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    APP_NAME: str = "jGet"
    ENV: str = "local"
    DEBUG: bool = False

    API_PREFIX: str = ""

    DATABASE_URL: str = "postgresql+asyncpg://app:app@localhost:5432/app"

    JWT_SECRET: str = "change-me"
    ACCESS_TTL: int = 1800  # seconds
    REFRESH_TTL: int = 2592000  # seconds
    JWT_ALGORITHM: str = "HS256"

    TIMEZONE: str = "Europe/Vienna"
    UPLOAD_DIR: str = "./uploads"

    LOG_LEVEL: str = "INFO"

    ALLOWED_ORIGINS: list[str] = ["*"]

    NOTIFICATION_REMINDER_WINDOW_HOURS: int = 24


settings = Settings()
