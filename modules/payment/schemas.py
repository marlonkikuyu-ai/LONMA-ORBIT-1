from pydantic import BaseModel

class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    method: str

class PaymentOut(BaseModel):
    id: int
    order_id: int
    amount: float
    method: str
    reference: str
    status: str
    class Config:
        from_attributes = True

class PayoutCreate(BaseModel):
    merchant_id: int
    amount: float
    method: str

class PayoutOut(BaseModel):
    id: int
    merchant_id: int
    amount: float
    method: str
    reference: str
    status: str
    class Config:
        from_attributes = True
