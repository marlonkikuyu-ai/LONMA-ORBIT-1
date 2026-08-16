from pydantic import BaseModel

class AddressCreate(BaseModel):
    label: str
    address_line: str
    latitude: float
    longitude: float

class AddressOut(BaseModel):
    id: int
    user_id: int
    label: str
    address_line: str
    latitude: float
    longitude: float
    class Config:
        from_attributes = True

class WalletCreate(BaseModel):
    user_id: int

class TopUpRequest(BaseModel):
    amount: float

class WalletOut(BaseModel):
    id: int
    user_id: int
    balance: float
    class Config:
        from_attributes = True
