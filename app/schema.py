from pydantic import BaseModel


class OrderLineIn(BaseModel):
    order_id: str
    sku: str
    quantity: int


class BatchIn(BaseModel):
    reference: str
    sku: str
    quantity: int
    eta: str
