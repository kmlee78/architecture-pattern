from datetime import datetime

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.domain.models import OrderLine
from app.service.unit_of_work import SqlAlchemyUnitOfWork


async def insert_batch(
    session: AsyncSession, ref: str, sku: str, qty: int, eta: datetime | None
) -> None:
    await session.execute(
        sa.text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            " VALUES (:ref, :sku, :qty, :eta)"
        ),
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


async def get_allocated_batch_ref(session: AsyncSession, order_id: str, sku: str) -> str:
    [[orderline_id]] = await session.execute(
        sa.text(
            f"SELECT id FROM order_lines WHERE order_id='{order_id}' AND sku='{sku}'",
            dict(order_id=order_id, sku=sku),
        )
    )
    [[batch_ref]] = await session.execute(
        sa.text(
            "SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id"
            f" WHERE orderline_id='{orderline_id}'",
            dict(orderline_id=orderline_id),
        )
    )
    return batch_ref


async def test_uow_can_retrieve_a_batch_and_allocate_to_it(
    session_factory: async_scoped_session,
) -> None:
    session = session_factory()
    await insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
    await session.commit()

    uow = SqlAlchemyUnitOfWork(session_factory)
    async with uow:
        batch = await uow.batches.get("batch1")
        line = OrderLine("o1", "HIPSTER-WORKBENCH", 10)
        batch.allocate(line)
        await uow.commit()
        batch_ref = await get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")

    assert batch_ref == "batch1"


async def test_rolls_back_uncommitted_work_by_default(
    session_factory: async_scoped_session,
) -> None:
    uow = SqlAlchemyUnitOfWork(session_factory)
    async with uow:
        await insert_batch(uow.session, "batch1", "MEDIUM-PLINTH", 100, None)
    session = session_factory()
    async with uow:
        rows = await session.execute(sa.text("SELECT * FROM batches"))

    assert list(rows) == []


async def test_rolls_back_on_error(session_factory: async_scoped_session) -> None:
    class MyException(Exception):
        pass

    uow = SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        async with uow:
            await insert_batch(uow.session, "batch1", "LARGE-FORK", 100, None)
            raise MyException()
    session = session_factory()
    async with uow:
        rows = await session.execute(sa.text("SELECT * FROM batches"))
    assert list(rows) == []
