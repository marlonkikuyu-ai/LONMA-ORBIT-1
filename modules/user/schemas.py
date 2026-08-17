from pydantic import BaseModel
from datetime import datetime

class AddressCreate(BaseModel):
    label: str
    address_line: str
    latitude: float
    longitude: float

class AddressOut(AddressCreate):
    id: int
    user_id: int
    created_at: datetime
    class Config: from_attributes = True

class WalletCreate(BaseModel):
    pass

class WalletOut(BaseModel):
    id: int
    user_id: int
    balance: float
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True

class TopUpRequest(BaseModel):
    amount: float
    
