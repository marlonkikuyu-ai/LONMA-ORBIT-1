from pydantic import BaseModel

class DeliveryZoneCreate(BaseModel):
    name: str
    base_fee: float
    per_km_fee: float

class DeliveryZoneOut(BaseModel):
    id: int
    name: str
    base_fee: float
    per_km_fee: float
    class Config:
        from_attributes = True

class DeliveryFeeRequest(BaseModel):
    zone_id: int
    distance_km: float

class DeliveryFeeOut(BaseModel):
    fee: float
    distance_km: float

class AssignRiderRequest(BaseModel):
    order_id: int
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float
    zone_id: int
