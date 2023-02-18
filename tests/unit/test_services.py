import pytest

from app.adapters.repository import AbstractRepository
from app.domain.models import Batch
from app.service import services
from app.service.unit_of_work import AbstractUnitOfWork


class FakeRepository(AbstractRepository):
    def __init__(self, batches: list[Batch]) -> None:
        self._batches = set(batches)

    @staticmethod
    def for_batch(ref: str, sku: str, quantity: int, eta=None):  # type: ignore
        return FakeRepository([Batch(ref, sku, quantity, eta)])

    async def add(self, batch: Batch) -> None:
        self._batches.add(batch)

    async def get(self, reference: str) -> Batch:
        return next(b for b in self._batches if b.reference == reference)

    async def list(self) -> list[Batch]:
        return list(self._batches)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.batches = FakeRepository([])
        self.committed = False

    async def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


async def test_add_batch() -> None:
    uow = FakeUnitOfWork()
    await services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.batches.get("b1") is not None
    assert uow.committed is True


async def test_allocate_returns_allocation() -> None:
    uow = FakeUnitOfWork()
    await services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
    result = await services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "batch1"


async def test_error_for_invalid_sku() -> None:
    uow = FakeUnitOfWork()
    await services.add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        await services.allocate("o1", "NONEXISTENTSKU", 10, uow)


async def test_commits() -> None:
    uow = FakeUnitOfWork()
    await services.add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
    await services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed is True
