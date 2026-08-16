from pydantic import BaseModel

class SupermarketCreate(BaseModel):
    owner_id: int
    name: str
    address: str
    latitude: float
    longitude: float
    phone: str

class SupermarketUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    is_active: bool | None = None

class SupermarketOut(BaseModel):
    id: int
    owner_id: int
    name: str
    address: str
    latitude: float
    longitude: float
    phone: str
    is_active: bool
    class Config:
        from_attributes = True
