import asyncio
from typing import AsyncGenerator, Generator

import pytest
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import clear_mappers

from app.config import settings
from app.orm import mapper_registry, start_mappers


@pytest.fixture(scope="session")
def event_loop() -> Generator[Connection, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(settings.db_url)
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)
    start_mappers()
    yield engine
    clear_mappers()
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    trans = await engine.begin()
    session = AsyncSession(bind=trans)
    yield session
    await session.close()
    await session.rollback()
