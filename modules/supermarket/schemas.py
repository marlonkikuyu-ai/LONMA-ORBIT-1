from pydantic import BaseModel
from datetime import datetime

class SupermarketCreate(BaseModel):
    name: str
    address: str
    lat: float
    lng: float
    phone: str
    bank_account: str

class SupermarketUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    phone: str | None = None
    is_active: bool | None = None

class SupermarketOut(BaseModel):
    id: str
    owner_id: str
    name: str
    address: str
    lat: float
    lng: float
    phone: str
    commission_rate: float
    is_active: bool
    bank_account: str
    created_at: datetime
    class Config:
        from_attributes = True
