import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as container:
        yield container


@pytest.fixture(scope="session")
def database_url(postgres_container):
    url = postgres_container.get_connection_url()
    async_url = url.replace("postgresql://", "postgresql+asyncpg://")
    os.environ["DATABASE_URL"] = async_url
    return async_url


@pytest.fixture(scope="session")
def migrated(database_url):
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    return True


@pytest.fixture
async def session(database_url, migrated):
    engine = create_async_engine(database_url, echo=False)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def app_instance(database_url, migrated):
    from app.main import create_app

    return create_app()


@pytest.fixture
async def client(app_instance, session):
    from app.core.db import get_session
    from httpx import AsyncClient

    async def override_get_session():
        yield session

    app_instance.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(app=app_instance, base_url="http://test") as client:
        yield client
