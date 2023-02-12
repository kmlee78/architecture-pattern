from pydantic import BaseModel


class OrderLine(BaseModel):
    order_id: str
    sku: str
    quantity: int


class Batch(BaseModel):
    reference: str
    sku: str
    quantity: int
    eta: str
