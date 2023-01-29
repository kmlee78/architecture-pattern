from __future__ import annotations

from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


class DataBase:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, echo=False)
        self._session_factory = async_scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                class_=AsyncSession,
                bind=self._engine,
            ),
            scopefunc=current_task,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.commit()
            await session.close()


async def session() -> AsyncGenerator[AsyncSession, None]:
    database = DataBase(settings.db_url)
    async with database.session() as session:
        yield session
