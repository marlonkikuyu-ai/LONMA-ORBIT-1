from pydantic import BaseModel
from datetime import datetime
class PaymentCreate(BaseModel):
    order_id: str
    amount: float
    method: str
    phone: str
class PaymentOut(BaseModel):
    id: str
    order_id: str
    amount: float
    method: str
    mpesa_code: str | None
    status: str
    paid_at: datetime | None
    class Config:
        from_attributes = True
class PayoutOut(BaseModel):
    id: str
    recipient_id: str
    recipient_type: str
    amount: float
    status: str
    reference: str | None
    created_at: datetime
    class Config:
        from_attributes = True
