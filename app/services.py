from __future__ import annotations

import models
from models import OrderLine
from repository import AbstractRepository
from sqlalchemy.ext.asyncio import AsyncSession


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[models.Batch]) -> bool:
    return sku in {b.sku for b in batches}


async def allocate(line: OrderLine, repo: AbstractRepository, session: AsyncSession) -> str:
    batches = await repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = models.allocate(line, batches)
    session.commit()
    return batchref
