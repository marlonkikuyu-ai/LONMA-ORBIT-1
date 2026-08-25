from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="LONMA ORBIT - Thika OS", version="2.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

# --- FIX HEAD 405 - STOPS PORT SCAN TIMEOUT ---
@app.api_route("/", methods=["GET", "HEAD"])
def home():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"status": "LONMA ORBIT LIVE", "brand": "#FFA500", "phone1": "0727828838", "phone2": "07463876981"}

@app.api_route("/www", methods=["GET", "HEAD"])
def www():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"status": "LONMA ORBIT LIVE - WWW", "brand": "#FFA500"}

# --- API: ORDERS ---
@app.get("/orders")
def get_orders():
    return {
        "orders": [
            {"id": "ORD-10284", "customer": "Sarah Wanjiku", "total": 1850, "status": "Delivered", "super": "Naivas Thika Town"},
            {"id": "ORD-10283", "customer": "James Omondi", "total": 4200, "status": "In Transit", "super": "Quickmart Kiganjo"},
            {"id": "ORD-10282", "customer": "Brian 0727828838", "total": 3100, "status": "Pending", "super": "Carrefour Ananas Mall"},
            {"id": "ORD-10281", "customer": "Grace 07463876981", "total": 2750, "status": "Delivered", "super": "Magunas Thika"}
        ]
    }

# --- API: RIDERS ---
@app.get("/riders")
def get_riders():
    return {
        "riders": [
            {"name": "Peter Rider", "phone": "0727828838", "status": "Online", "orders": 12},
            {"name": "John Rider", "phone": "07463876981", "status": "Online", "orders": 8}
        ]
    }

# --- API: SUPERMARKETS (15) ---
@app.get("/supers")
def get_supers():
    return {
        "supers": [
            {"name": "Naivas Thika Town", "loc": "CBD", "fee": 80},
            {"name": "Naivas Mountain Mall", "loc": "Mountain Mall", "fee": 120},
            {"name": "Quickmart Kiganjo", "loc": "Kiganjo Rd", "fee": 70},
            {"name": "Quickmart Thika", "loc": "Thika Arcade", "fee": 80},
            {"name": "Carrefour Ananas Mall", "loc": "Ananas Mall", "fee": 100},
            {"name": "Carrefour Juja", "loc": "Juja City Mall", "fee": 150},
            {"name": "Magunas Thika", "loc": "Gatitu", "fee": 90},
            {"name": "Choppies Thika", "loc": "Bazaar", "fee": 70},
            {"name": "Eastmatt Thika", "loc": "Eastmatt", "fee": 80},
            {"name": "Cleanshelf Thika", "loc": "Mama Ngina", "fee": 60},
            {"name": "Mathai Supermarket", "loc": "Makongeni", "fee": 50},
            {"name": "Khetias Thika", "loc": "Kenyatta Hwy", "fee": 90},
            {"name": "Naivas Juja", "loc": "Juja Town", "fee": 130},
            {"name": "Quickmart Ruiru", "loc": "Ruiru", "fee": 140},
            {"name": "Carrefour Ruiru", "loc": "Ruiru Mall", "fee": 150}
        ]
    }

# --- API: M-PESA PAY ---
@app.post("/pay/mpesa")
def pay_mpesa(data: dict):
    return {
        "status": "Payment request sent",
        "phone": data.get("phone", "0727828838"),
        "amount": data.get("amount", 0),
        "order_id": data.get("order_id", "ORD-10284"),
        "till": "0727828838",
        "support": "07463876981",
        "brand_color": "#FFA500"
    }

@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok", "service": "lonma-orbit", "live": True}
