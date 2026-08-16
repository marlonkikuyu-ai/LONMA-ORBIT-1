from pydantic import BaseModel

class ProductCreate(BaseModel):
    merchant_id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: str | None = None

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    category: str | None = None
    image_url: str | None = None

class StockUpdate(BaseModel):
    quantity: int

class ProductOut(BaseModel):
    id: int
    merchant_id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: str | None = None
    class Config:
        from_attributes = True
