import abc

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload

from app.domain.models import Batch


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, batch: Batch) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, reference: str) -> Batch:
        raise NotImplementedError

    @abc.abstractmethod
    async def list(self) -> list[Batch]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, batch: Batch) -> None:
        self.session.add(batch)
        await self.session.flush()

    async def get(self, reference: str) -> Batch:
        return await self.session.get(Batch, reference)

    async def list(self) -> list[Batch]:
        result = await self.session.execute(
            sa.select(Batch).options(subqueryload(Batch._allocations))
        )
        return [r[0] for r in result.fetchall()]
