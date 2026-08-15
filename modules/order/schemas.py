from pydantic import BaseModel
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: float

class OrderCreate(BaseModel):
    supermarket_id: str
    items: list[OrderItemCreate]
    delivery_address: str
    lat: float
    lng: float

class OrderOut(BaseModel):
    id: str
    customer_id: str
    supermarket_id: str
    rider_id: str | None
    status: str
    total_amount: float
    delivery_fee: float
    commission: float
    supermarket_payout: float
    payment_status: str
    delivery_address: str
    lat: float
    lng: float
    created_at: datetime
    class Config:
        from_attributes = True
