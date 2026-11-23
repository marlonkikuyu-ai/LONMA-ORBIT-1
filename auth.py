# auth.py - Members use OWN credentials
from fastapi import APIRouter, Request, HTTPException
import sqlite3, secrets, os, hashlib

router = APIRouter()

ADMIN_EMAIL = "marlonkikuyu@gmail.com"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

def hash_pw(pw: str):
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_pw(pw: str, hashed: str):
    return hashlib.sha256(pw.encode()).hexdigest() == hashed

def audit_log(action, email, details):
    print(f"[AUDIT] {action} | {email} | {details}")

def get_db():
    conn = sqlite3.connect("lonma.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_users():
    db = get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT DEFAULT '',
        role TEXT DEFAULT 'member',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    db.commit(); db.close()

init_users()

@router.post("/api/auth/signup")
async def signup(request: Request):
    data = await request.json()
    email = data.get("email","").lower().strip()
    password = data.get("password","")
    name = data.get("name","").strip()
    if not email or "@" not in email:
        raise HTTPException(400, "Valid email required")
    if len(password) < 8:
        raise HTTPException(400, "Password must be 8+ characters")
    if email == ADMIN_EMAIL:
        raise HTTPException(403, "This email is reserved for Admin")
    db = get_db()
    try:
        db.execute("INSERT INTO users (email, password_hash, name, role) VALUES (?,?,?,?)",
                   (email, hash_pw(password), name, "member"))
        db.commit()
    except sqlite3.IntegrityError:
        db.close()
        raise HTTPException(400, "Email already registered - please Log In")
    db.close()
    audit_log("MEMBER_SIGNUP", email, f"New member: {name}")
    return {"ok": True, "message": "Account created - please Log In"}

@router.post("/api/auth/login")
async def member_login(request: Request):
    data = await request.json()
    email = data.get("email","").lower().strip()
    password = data.get("password","")
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if email == ADMIN_EMAIL:
        if password != ADMIN_PASSWORD:
            db.close()
            raise HTTPException(401, "Wrong email or password")
        token = secrets.token_urlsafe(32)
        db.execute("INSERT INTO sessions (token, email) VALUES (?,?)", (token, email))
        db.commit(); db.close()
        return {"ok": True, "token": token, "email": email, "role": "admin", "name": "Admin"}
    if not user or not verify_pw(password, user["password_hash"]):
        db.close()
        raise HTTPException(401, "Wrong email or password")
    token = secrets.token_urlsafe(32)
    db.execute("INSERT INTO sessions (token, email) VALUES (?,?)", (token, email))
    db.commit(); db.close()
    return {"ok": True, "token": token, "email": user["email"], "role": user["role"], "name": user["name"]}

def get_current_user(request: Request):
    auth = request.headers.get("Authorization","")
    token = auth.replace("Bearer ","") if auth.startswith("Bearer ") else ""
    if not token:
        raise HTTPException(401, "Please log in first")
    db = get_db()
    sess = db.execute("SELECT * FROM sessions WHERE token=?", (token,)).fetchone()
    db.close()
    if not sess:
        raise HTTPException(401, "Session expired - please log in again")
    return sess["email"]

@router.post("/api/auth/logout")
async def logout(request: Request):
    email = get_current_user(request)
    token = request.headers.get("Authorization","").replace("Bearer ","")
    db = get_db()
    db.execute("DELETE FROM sessions WHERE token=?", (token,))
    db.commit(); db.close()
    return {"ok": True}
