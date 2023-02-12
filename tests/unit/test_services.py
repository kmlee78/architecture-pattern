import pytest

from app.adapters.repository import AbstractRepository
from app.domain.models import Batch
from app.service import services


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


class FakeSession:
    committed = False

    def commit(self) -> None:
        self.committed = True


async def test_returns_allocation() -> None:
    repo, session = FakeRepository([]), FakeSession()
    await services.add_batch("b1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = await services.allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "b1"


async def test_error_for_invalid_sku() -> None:
    repo, session = FakeRepository([]), FakeSession()
    await services.add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        await services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


async def test_commits() -> None:
    repo, session = FakeRepository([]), FakeSession()
    await services.add_batch("b1", "OMINOUS-MIRROR", 100, None, repo, session)
    await services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True


async def test_add_batch() -> None:
    repo, session = FakeRepository([]), FakeSession()
    await services.add_batch("b1", "SMALL-TABLE", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed is True
