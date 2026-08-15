from pydantic import BaseModel
from datetime import datetime

class ProductCreate(BaseModel):
    supermarket_id: str
    name: str
    category: str
    price: float
    stock: float
    unit: str
    image_url: str | None = None

class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    price: float | None = None
    stock: float | None = None
    unit: str | None = None
    image_url: str | None = None
    is_active: bool | None = None

class ProductOut(BaseModel):
    id: str
    supermarket_id: str
    name: str
    category: str
    price: float
    stock: float
    unit: str
    image_url: str | None
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True
