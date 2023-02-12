from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository import SqlAlchemyRepository
from app.database import session
from app.domain import models
from app.schema import OrderLine
from app.service import services

router = APIRouter()


def is_valid_sku(sku: str, batches: list[models.Batch]) -> bool:
    return sku in {b.sku for b in batches}


@router.post("/allocate", status_code=status.HTTP_201_CREATED)
async def allocate_endpoint(
    orderline: OrderLine, session: AsyncSession = Depends(session)
) -> dict[str, str]:
    repo = SqlAlchemyRepository(session)
    batches = await repo.list()
    line = models.OrderLine(
        order_id=orderline.order_id, sku=orderline.sku, quantity=orderline.quantity
    )

    if not is_valid_sku(line.sku, batches):
        raise HTTPException(status_code=400, detail=f"Invalid sku {line.sku}")

    try:
        batchref = await services.allocate(
            orderline.order_id, orderline.sku, orderline.quantity, repo, session
        )
    except models.OutOfStock as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    return {"batchref": batchref}
