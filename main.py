from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"status": "ok", "app": "LONMA ORBIT", "url": "https://app.lonmaorbit.co.ke"}

@app.get("/www")
def www():
    return FileResponse("static/index.html")

@app.get("/orders")
def orders():
    return {
        "orders": [
            {"id": "ORD-10284", "customer": "Sarah Wanjiku", "total": 1850, "status": "Delivered"},
            {"id": "ORD-10283", "customer": "James Omondi", "total": 4200, "status": "In Transit"},
            {"id": "ORD-10282", "customer": "Emily Akinyi", "total": 950, "status": "Processing"},
            {"id": "ORD-10281", "customer": "David Kimani", "total": 2120, "status": "Delivered"},
            {"id": "ORD-10280", "customer": "Grace Njeri", "total": 720, "status": "Cancelled"}
        ]
    }

@app.get("/supermarket")
def supermarket():
    return {
        "products": [
            {"name": "Fresh Milk 1L", "price": 120, "stock": 50},
            {"name": "Bread", "price": 70, "stock": 100},
            {"name": "Eggs Tray", "price": 450, "stock": 30},
            {"name": "Sugar 2kg", "price": 320, "stock": 80},
            {"name": "Cooking Oil 1L", "price": 280, "stock": 60},
            {"name": "Rice 5kg", "price": 650, "stock": 40}
        ]
    }

@app.get("/riders")
def riders():
    return {
        "riders": [
            {"id": 1, "name": "John Mwangi", "status": "online"},
            {"id": 2, "name": "Peter Ochieng", "status": "busy"},
            {"id": 3, "name": "Ali Hassan", "status": "online"}
        ]
    }

@app.get("/payments")
def payments():
    return {
        "payments": [
            {"id": "PAY-001", "order": "ORD-10284", "method": "M-Pesa", "amount": 1850, "status": "Paid"},
            {"id": "PAY-002", "order": "ORD-10283", "method": "Card", "amount": 4200, "status": "Paid"}
        ]
    }
