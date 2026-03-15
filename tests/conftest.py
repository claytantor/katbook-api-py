import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models.base import Base

TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/katbook_test"


@pytest.fixture(scope="session")
async def engine():
    test_engine = create_async_engine(TEST_DATABASE_URL)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def db(engine):
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db: AsyncSession):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def registered_agent(client: AsyncClient) -> dict:
    """Register and return an agent with its api_key."""
    resp = await client.post(
        "/api/v1/agents/register",
        json={"name": "testagent", "description": "Test agent"},
    )
    assert resp.status_code == 201
    return resp.json()["data"]


@pytest.fixture
def auth_headers(registered_agent: dict) -> dict:
    return {"Authorization": f"Bearer {registered_agent['api_key']}"}
