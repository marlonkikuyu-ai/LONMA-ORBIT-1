from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir("static"):
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    except:
        pass

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/www")
def www():
    path = "static/index.html"
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "index.html not found"}

@app.get("/orders")
def orders():
    return {"orders": [
        {"id": "ORD-10284", "customer": "Sarah Wanjiku", "total": 1850, "status": "Delivered"},
        {"id": "ORD-10283", "customer": "James Omondi", "total": 4200, "status": "In Transit"},
    ]}

@app.get("/supermarket")
def supermarket():
    return {"products": [
        {"name": "Fresh Milk", "price": 120, "stock": 50},
        {"name": "Bread", "price": 70, "stock": 100}
    ]}

@app.get("/riders")
def riders():
    return {"riders": [{"id": 1, "name": "John", "status": "online"}]}

@app.get("/payments")
def payments():
    return {"payments": []}

class PayRequest(BaseModel):
    phone: str
    amount: int
    order_id: str

@app.post("/pay/mpesa")
def mpesa_pay(req: PayRequest):
    phone = req.phone.strip().replace(" ", "").replace("+", "")
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    return {"status": "sent", "phone": phone, "amount": req.amount, "order_id": req.order_id, "message": f"STK sent to {req.phone}"}
