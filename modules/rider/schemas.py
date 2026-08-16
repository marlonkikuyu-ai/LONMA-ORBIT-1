from pydantic import BaseModel

class RiderCreate(BaseModel):
    user_id: int
    vehicle_type: str
    vehicle_number: str
    latitude: float
    longitude: float

class RiderUpdate(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    is_available: bool | None = None

class EarningUpdate(BaseModel):
    amount: float

class RatingUpdate(BaseModel):
    rating: float

class RiderOut(BaseModel):
    id: int
    user_id: int
    vehicle_type: str
    vehicle_number: str
    latitude: float
    longitude: float
    is_available: bool
    earnings: float
    rating: float
    class Config:
        from_attributes = True
