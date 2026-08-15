from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    phone: str
    email: EmailStr | None = None
    password: str
    role: str

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: str
    phone: str
    email: str | None
    role: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True
