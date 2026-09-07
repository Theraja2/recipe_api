import pytest_asyncio

from httpx import ASGITransport, AsyncClient

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.main import app

# ------------------------------------------------------------
# IMPORT BOTH POSSIBLE DATABASE DEPENDENCIES
# ------------------------------------------------------------

from app.dependencies.database import get_session as dependencies_get_session
from app.database.database import get_session as database_get_session


# ------------------------------------------------------------
# TEST DATABASE
# ------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)


TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ------------------------------------------------------------
# CREATE TEST DATABASE
# ------------------------------------------------------------

@pytest_asyncio.fixture(
    scope="function",
    autouse=True,
)
async def setup_database():

    async with test_engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.drop_all
        )


# ------------------------------------------------------------
# TEST DATABASE SESSION
# ------------------------------------------------------------

async def override_get_session():

    async with TestSessionLocal() as session:
        yield session


# ------------------------------------------------------------
# OVERRIDE BOTH DATABASE DEPENDENCIES
# ------------------------------------------------------------

app.dependency_overrides[
    dependencies_get_session
] = override_get_session

app.dependency_overrides[
    database_get_session
] = override_get_session


# ------------------------------------------------------------
# HTTPX CLIENT
# ------------------------------------------------------------

@pytest_asyncio.fixture
async def client():

    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:

        yield test_client