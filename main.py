from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"status": "ok", "app": "LONMA ORBIT"}

@app.get("/www")
def www():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"error": "static/index.html missing - upload it"}

@app.get("/orders")
def orders():
    return {"orders": [
        {"id": "ORD-10284", "customer": "Sarah Wanjiku", "total": 1850, "status": "Delivered"},
        {"id": "ORD-10283", "customer": "James Omondi", "total": 4200, "status": "In Transit"},
        {"id": "ORD-10282", "customer": "Emily Akinyi", "total": 950, "status": "Processing"}
    ]}

@app.get("/supermarket")
def supermarket():
    return {"products": [
        {"name": "Fresh Milk 1L", "price": 120, "stock": 50},
        {"name": "Bread", "price": 70, "stock": 100},
        {"name": "Eggs Tray", "price": 450, "stock": 30}
    ]}

@app.get("/riders")
def riders():
    return {"riders": [{"id": 1, "name": "John Mwangi", "status": "online"}]}

@app.get("/payments")
def payments():
    return {"payments": []}
