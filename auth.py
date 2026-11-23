import sqlite3
import hashlib
import secrets
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

DB_PATH = "app.db"
router = APIRouter()

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()

init_db()

def hash_password(pw: str):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_current_user(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not logged in")
    token = auth.replace("Bearer ", "").strip()
    db = get_db()
    row = db.execute("SELECT email FROM sessions WHERE token=?", (token,)).fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=401, detail="Session expired - please login again")
    return row["email"]

class SignupIn(BaseModel):
    name: str
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

@router.post("/api/auth/signup")
async def signup(data: SignupIn):
    db = get_db()
    email = data.email.lower().strip()
    existing = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    db.execute("INSERT INTO users (name, email, password_hash) VALUES (?,?,?)",
               (data.name, email, hash_password(data.password)))
    token = secrets.token_hex(32)
    db.execute("INSERT INTO sessions (token, email) VALUES (?,?)", (token, email))
    db.commit(); db.close()
    return {"ok": True, "token": token, "email": email, "name": data.name}

@router.post("/api/auth/login")
async def login(data: LoginIn):
    db = get_db()
    email = data.email.lower().strip()
    user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user or user["password_hash"] != hash_password(data.password):
        db.close()
        raise HTTPException(status_code=401, detail="Wrong email or password")
    token = secrets.token_hex(32)
    db.execute("INSERT INTO sessions (token, email) VALUES (?,?)", (token, email))
    db.commit(); db.close()
    return {"ok": True, "token": token, "email": email, "name": user["name"]}

@router.post("/api/auth/logout")
async def logout(request: Request):
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.replace("Bearer ", "").strip()
        db = get_db()
        db.execute("DELETE FROM sessions WHERE token=?", (token,))
        db.commit(); db.close()
    return {"ok": True}

@router.get("/api/auth/me")
async def check_me(request: Request):
    email = get_current_user(request)
    return {"ok": True, "email": email}

# --- FORCE LOGOUT ALL - Must be at BOTTOM ---
def logout_all_users():
    try:
        db = get_db()
        db.execute("DELETE FROM sessions")
        db.commit(); db.close()
        print("ALL USERS LOGGED OUT - Must sign in again")
    except Exception as e:
        print(f"logout_all skipped: {e}")

logout_all_users()
