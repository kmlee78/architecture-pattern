from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.domain import models
from app.schema import BatchIn, OrderLineIn
from app.service import services
from app.service.unit_of_work import SqlAlchemyUnitOfWork

router = APIRouter()


@router.post("/allocate", status_code=status.HTTP_201_CREATED)  # type: ignore
async def allocate_endpoint(orderline: OrderLineIn) -> dict[str, str]:
    try:
        batchref = await services.allocate(
            orderline.order_id, orderline.sku, orderline.quantity, uow=SqlAlchemyUnitOfWork()
        )
    except (models.OutOfStock, services.InvalidSku) as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    return {"batchref": batchref}


@router.post("/add_batch", status_code=status.HTTP_201_CREATED)  # type: ignore
async def add_batch(batch: BatchIn) -> dict[str, str]:
    eta = datetime.fromisoformat(batch.eta) if batch.eta else None
    await services.add_batch(
        batch.reference, batch.sku, batch.quantity, eta, uow=SqlAlchemyUnitOfWork()
    )
    return {"message": "success"}
