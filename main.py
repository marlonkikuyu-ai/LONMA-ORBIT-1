import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def root():
    return {"status": "ok", "service": "LONMA ORBIT"}

@app.get("/www")
def serve_www():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "static/index.html not found"}

@app.get("/orders")
def get_orders():
    return {"orders": []}

@app.get("/supermarket")
def get_supermarket():
    return {"products": []}

@app.get("/payments")
def get_payments():
    return {"payments": []}

@app.get("/riders")
def get_riders():
    return {"riders": []}

@app.get("/delivery")
def get_delivery():
    return {"deliveries": []}
