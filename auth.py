from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import json, os, hashlib, secrets

router = APIRouter(prefix="/api/auth", tags=["auth"])

USERS_FILE = "users.json"
SESSIONS = {}  # token -> user

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE) as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(p: str):
    return hashlib.sha256(p.encode()).hexdigest()

def verify_password(p: str, h: str):
    return hashlib.sha256(p.encode()).hexdigest() == h

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
    for u in load_users():
        if phone and u.get("phone") == phone:
            return u
        if email and u.get("email","").lower() == email.lower():
            return u
    return None

@router.post("/signup")
def signup(data: Signup):
    if not data.phone and not data.email:
        raise HTTPException(400, "Phone or email required")
    if len(data.password) < 4:
        raise HTTPException(400, "Password min 4 chars")
    if find_user(data.phone, data.email):
        raise HTTPException(400, "Account already exists")
    users = load_users()
    new_user = {
        "name": data.name,
        "phone": data.phone or "",
        "email": (data.email or "").lower(),
        "password_hash": hash_password(data.password)
    }
    users.append(new_user)
    save_users(users)
    token = secrets.token_hex(16)
    SESSIONS[token] = new_user
    return {"token": token, "name": new_user["name"], "phone": new_user["phone"], "email": new_user["email"]}

@router.post("/login")
def login(data: Login):
    if not data.phone and not data.email:
        raise HTTPException(400, "Phone or email required")
    user = find_user(data.phone, data.email)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid phone/email or password")
    token = secrets.token_hex(16)
    SESSIONS[token] = user
    return {"token": token, "name": user["name"], "phone": user["phone"], "email": user["email"]}

@router.get("/me")
def me(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "No token")
    token = authorization.replace("Bearer ", "")
    user = SESSIONS.get(token)
    if not user:
        raise HTTPException(401, "Invalid token")
    return {"name": user["name"], "phone": user["phone"], "email": user["email"]}

@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        SESSIONS.pop(token, None)
    return {"ok": True}
