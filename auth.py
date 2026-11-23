from pydantic import BaseModel
from typing import Optional

class Signup(BaseModel):
    name: str
    password: str
    phone: Optional[str] = None
    email: Optional[str] = None

class Login(BaseModel):
    password: str
    phone: Optional[str] = None
    email: Optional[str] = None

def find_user(phone=None, email=None):
    # Search users.json by phone OR email
    for u in load_users():
        if phone and u.get("phone") == phone:
            return u
        if email and u.get("email","").lower() == email.lower():
            return u
    return None

# In signup:
# if not data.phone and not data.email: raise 400 "Phone or email required"
# if find_user(data.phone, data.email): raise 400 "Account already exists"

# In login:
# user = find_user(data.phone, data.email)
# if not user or not verify_password(data.password, user["password_hash"]):
#   raise 401 "Invalid phone/email or password"
