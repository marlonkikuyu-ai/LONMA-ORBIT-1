from pydantic import BaseModel
from datetime import datetime

class RiderCreate(BaseModel):
    name: str
    phone: str
    bike_plate: str

class RiderLocationUpdate(BaseModel):
    lat: float
    lng: float

class RiderStatusUpdate(BaseModel):
    is_online: bool

class RiderOut(BaseModel):
    id: str
    user_id: str
    name: str
    phone: str
    bike_plate: str
    lat: float
    lng: float
    is_online: bool
    wallet_balance: float
    total_deliveries: float
    rating: float
    created_at: datetime
    class Config:
        from_attributes = True
