import asyncio
from typing import Any, AsyncGenerator, Generator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import clear_mappers

from app.config import config
from app.orm import metadata, start_mappers


@pytest.fixture(scope="session")
def event_loop() -> Generator[Any, Any, Any]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(config.DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    start_mappers()
    yield engine
    clear_mappers()
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    await engine.dispose()


@pytest.fixture(autouse=True)
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    trans = await engine.begin()
    session = AsyncSession(bind=trans)
    yield session
    await session.rollback()
    await session.close()
