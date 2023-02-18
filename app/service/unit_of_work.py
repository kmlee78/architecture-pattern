from __future__ import annotations

import abc

from sqlalchemy.ext.asyncio import async_scoped_session

from app.adapters import repository
from app.database import DEFAULT_SESSION_FACTORY


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
