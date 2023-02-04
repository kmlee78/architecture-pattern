import abc

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Batch


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
        await self.session.add(batch)

    async def get(self, reference: str) -> Batch:
        return await self.session.query(Batch).filter_by(reference=reference).one()

    async def list(self) -> list[Batch]:
        return await self.session.query(Batch).all()
