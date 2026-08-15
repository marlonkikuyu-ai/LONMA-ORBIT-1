from pydantic import BaseModel
from datetime import datetime

class AddressCreate(BaseModel):
    label: str
    address: str
    lat: float
    lng: float

class AddressOut(BaseModel):
    id: str
    user_id: str
    label: str
    address: str
    lat: float
    lng: float
    created_at: datetime
    class Config:
        from_attributes = True

class WalletOut(BaseModel):
    id: str
    user_id: str
    balance: float
    class Config:
        from_attributes = True
