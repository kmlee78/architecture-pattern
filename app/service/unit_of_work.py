from __future__ import annotations

import abc
from asyncio import current_task

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.adapters import repository
from app.config import config


class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    async def __aenter__(self) -> AbstractUnitOfWork:
        pass

    async def __aexit__(self, *args) -> None:  # type: ignore
        pass

    @abc.abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = async_scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        class_=AsyncSession,
        bind=create_async_engine(config.DB_URL, echo=False),
    ),
    scopefunc=current_task,
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: async_scoped_session = DEFAULT_SESSION_FACTORY) -> None:
        self.session_factory = session_factory

    async def __aenter__(self) -> AbstractUnitOfWork:
        self.session = self.session_factory()
        self.batches = repository.SqlAlchemyRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):  # type: ignore
        await super().__aexit__(*args)
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
