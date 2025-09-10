from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class OrderItemCreate(BaseModel):
    menu_item_id: int
    qty: int = Field(gt=0)

class OrderCreate(BaseModel):
    table_no: int
    customer_name: str
    items: List[OrderItemCreate]

class OrderStatusUpdate(BaseModel):
    status: str


class Order(BaseModel):
    id: int
    table_no: int
    customer_name: str
    order_code: str
    order_status: str
    amount_total: int
    created_at: datetime