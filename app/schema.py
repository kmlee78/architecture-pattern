from pydantic import BaseModel


class OrderLine(BaseModel):
    order_id: str
    sku: str
    quantity: int
