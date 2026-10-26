# backend/tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Используем тестовую БД (SQLite в памяти – быстро, но для async нужен асинхронный драйвер)
# Проще использовать PostgreSQL, но можно создать отдельную БД для тестов.
# Для упрощения используем тот же PostgreSQL, но с отдельной базой "test_urlshortener".
# Предварительно создайте базу test_urlshortener.

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost/test_urlshortener"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
async def test_engine():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(test_engine):
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
async def client(db_session):
    # Переопределяем зависимость get_db, чтобы тесты использовали тестовую сессию
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()