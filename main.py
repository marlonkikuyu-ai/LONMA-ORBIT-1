from fastapi import FastAPI, Request
import random
import time
OTP_STORE = {}
USERS = {}
def generate_otp():
    return str(random.randint(100000, 999999))
@app.post("/auth/send-otp")
async def send_otp(req: Request):
    b = await req.json()
    phone = b.get("phone","").strip()
    if len(phone) < 9:
        return {"success": False, "error": "Invalid phone"}
    otp = generate_otp()
    OTP_STORE[phone] = {"otp": otp, "exp": time.time() + 300, "tries": 0}
    print(f"OTP for {phone}: {otp}")
    return {"success": True, "message": "OTP sent", "debug_otp": otp}
@app.post("/auth/verify-otp")
async def verify_otp(req: Request):
    b = await req.json()
    phone = b.get("phone","").strip()
    code = b.get("code","").strip()
    name = b.get("name","").strip()
    rec = OTP_STORE.get(phone)
    if not rec:
        return {"success": False, "error": "No OTP sent"}
    if time.time() > rec["exp"]:
        del OTP_STORE[phone]
        return {"success": False, "error": "OTP expired"}
    if rec["tries"] >= 5:
        del OTP_STORE[phone]
        return {"success": False, "error": "Too many tries"}
    if rec["otp"]!= code:
        rec["tries"] += 1
        return {"success": False, "error": "Wrong code"}
    del OTP_STORE[phone]
    token = f"tok_{phone}_{int(time.time())}"
    USERS[token] = {"phone": phone, "name": name if name else "Mteja", "login_at": time.time()}
    return {"success": True, "token": token, "user": USERS[token]}
@app.get("/auth/me")
async def me(req: Request):
    token = req.headers.get("Authorization","").replace("Bearer ","")
    u = USERS.get(token)
    if not u:
        return {"logged_in": False}
    return {"logged_in": True, "user": u}
@app.post("/auth/logout")
async def logout(req: Request):
    token = req.headers.get("Authorization","").replace("Bearer ","")
    if token in USERS:
        del USERS[token]
    return {"success": True}
