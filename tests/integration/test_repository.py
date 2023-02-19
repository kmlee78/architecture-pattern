import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository import SqlAlchemyRepository
from app.domain.models import Batch


async def insert_order_line(session: AsyncSession) -> int:
    await session.execute(
        sa.text(
            "INSERT INTO order_lines (order_id, sku, quantity) VALUES ('order1',"
            " 'GENERIC-SOFA', 12)"
        )
    )
    [[orderline_id]] = await session.execute(
        sa.text("SELECT id FROM order_lines WHERE order_id=:order_id AND sku=:sku"),
        dict(order_id="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id


async def insert_batch(session: AsyncSession, batch_id: str) -> int:
    await session.execute(
        sa.text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            " VALUES (:batch_id, 'GENERIC-SOFA', 100, null)"
        ),
        dict(batch_id=batch_id),
    )
    [[id]] = await session.execute(
        sa.text("SELECT id FROM batches WHERE reference=:batch_id AND sku='GENERIC-SOFA'"),
        dict(batch_id=batch_id),
    )
    return id


async def insert_allocation(session: AsyncSession, orderline_id: int, batch_id: int) -> None:
    await session.execute(
        sa.text(
            "INSERT INTO allocations (orderline_id, batch_id) VALUES (:orderline_id, :batch_id)"
        ),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


async def test_repository_can_save_a_batch(session: AsyncSession) -> None:
    batch = Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = SqlAlchemyRepository(session)
    await repo.add(batch)

    rows = await session.execute(
        sa.text("SELECT reference, sku, _purchased_quantity, eta FROM batches")
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


async def test_repository_can_retrieve_a_batch_with_allocations(session: AsyncSession) -> None:
    orderline_id = await insert_order_line(session)
    batch1_id = await insert_batch(session, "batch1")
    await insert_allocation(session, orderline_id, batch1_id)

    repo = SqlAlchemyRepository(session)
    retrieved = await repo.get("batch1")

    expected = Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved.reference == expected.reference
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    # TODO: assert allocations
