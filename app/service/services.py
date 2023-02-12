from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository import AbstractRepository
from app.domain import models
from app.domain.models import OrderLine


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[models.Batch]) -> bool:
    return sku in {b.sku for b in batches}


async def allocate(
    order_id: str, sku: str, quantity: int, repo: AbstractRepository, session: AsyncSession
) -> str:
    line = OrderLine(order_id, sku, quantity)
    batches = await repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = models.allocate(line, batches)
    session.commit()
    return batchref


async def add_batch(
    ref: str,
    sku: str,
    quantity: int,
    eta: datetime | None,
    repo: AbstractRepository,
    session: AsyncSession,
) -> None:
    await repo.add(models.Batch(ref, sku, quantity, eta))
    session.commit()
