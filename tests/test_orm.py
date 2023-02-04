import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OrderLine


async def test_orderline_mapper_can_load_lines(session: AsyncSession) -> None:
    session.execute(
        sa.text(
            "INSERT INTO order_lines (order_id, sku, quantity) VALUES "
            "('order1', 'RED-CHAIR', 12),"
            "('order1', 'RED-TABLE', 13),"
            "('order2', 'BLUE-LIPSTICK', 14)"
        )
    )
    expected = [
        OrderLine("order1", "RED-CHAIR", 12),
        OrderLine("order1", "RED-TABLE", 13),
        OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]
    result = await session.execute(sa.select(OrderLine))
    assert [r[0] for r in result.fetchall()] == expected


# async def test_orderline_mapper_can_save_lines(session: AsyncSession) -> None:
#     new_line = OrderLine("order1", "DECORATIVE-WIDGET", 12)
#     session.add(new_line)
#     session.flush()

#     rows = await session.execute(sa.text("SELECT order_id, sku, quantity FROM order_lines"))
#     assert rows.fetchall() == [("order1", "DECORATIVE-WIDGET", 12)]
