# async def insert_batch(
#     session: AsyncSession, ref: str, sku: str, qty: int, eta: datetime | None
# ) -> None:
#     await session.execute(
#         sa.text(
#             "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
#             " VALUES (:ref, :sku, :qty, :eta)"
#         ),
#         dict(ref=ref, sku=sku, qty=qty, eta=eta),
#     )


# async def get_allocated_batch_ref(session: AsyncSession, order_id: str, sku: str) -> str:
#     [[batch_ref]] = await session.execute(
#         sa.text(
#             "SELECT b.reference FROM order_lines AS ol JOIN allocations AS al ON ol.id ="
#             " a.orderline_id JOIN batches AS b ON a.batch_id = b.id"
#              " WHERE ol.order_id=:order_id AND"
#             " ol.sku=:sku"
#         ),
#         dict(order_id=order_id, sku=sku),
#     )
#     return batch_ref


# async def test_uow_can_retrieve_a_batch_and_allocate_to_it(session: AsyncSession):
#     session = session_factory()
#     await insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
#     await session.commit()

#     uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
#     with uow:
#         batch = uow.batches.get(reference="batch1")
#         line = OrderLine("o1", "HIPSTER-WORKBENCH", 10)
#         batch.allocate(line)
#         uow.commit()

#     batch_ref = await get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
#     assert batch_ref == "batch1"
