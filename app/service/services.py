from __future__ import annotations

from datetime import datetime

from app.domain import models
from app.domain.models import OrderLine
from app.service.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[models.Batch]) -> bool:
    return sku in {b.sku for b in batches}


async def allocate(
    order_id: str,
    sku: str,
    quantity: int,
    uow: AbstractUnitOfWork,
) -> str:
    line = OrderLine(order_id, sku, quantity)
    async with uow:
        batches = await uow.batches.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = models.allocate(line, batches)
        await uow.commit()
    return batchref


async def add_batch(
    ref: str,
    sku: str,
    quantity: int,
    eta: datetime | None,
    uow: AbstractUnitOfWork,
) -> None:
    async with uow:
        await uow.batches.add(models.Batch(ref, sku, quantity, eta))
        await uow.commit()
