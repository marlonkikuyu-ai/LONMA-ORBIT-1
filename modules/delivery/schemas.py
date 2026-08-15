from pydantic import BaseModel
class DeliveryZoneCreate(BaseModel):
    supermarket_id: str
    name: str
    base_fee: float
    per_km_fee: float
class DeliveryZoneOut(BaseModel):
    id: str
    supermarket_id: str
    name: str
    base_fee: float
    per_km_fee: float
    class Config:
        from_attributes = True
