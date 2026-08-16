from pydantic import BaseModel
from typing import List

class OrderItemCreate(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    merchant_id: int
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: float
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    merchant_id: int
    total_amount: float
    status: str
    items: List[OrderItemOut]
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str
