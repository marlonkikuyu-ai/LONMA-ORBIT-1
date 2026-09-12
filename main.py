from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OrderCreate(BaseModel):
    customer_name: str
    phone: str
    product_id: int
    quantity: int

products = [
    {"id": 1, "name": "Unga 2kg", "category": "Flour", "price": 180, "stock": 100},
    {"id": 2, "name": "Milk 500ml", "category": "Dairy", "price": 65, "stock": 200},
    {"id": 3, "name": "Bread", "category": "Bakery", "price": 70, "stock": 80},
    {"id": 4, "name": "Oil 1L", "category": "Cooking", "price": 280, "stock": 50},
    {"id": 5, "name": "Sugar 1kg", "category": "Essentials", "price": 160, "stock": 120},
    {"id": 6, "name": "Rice 2kg", "category": "Grains", "price": 350, "stock": 60},
]

orders = []

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>Supermarket LIVE</h1><a href='/products'>Products</a> | <a href='/docs'>Docs</a>"

@app.get("/products")
def get_products():
    return products

@app.post("/order")
def order(o: OrderCreate):
    p = next((x for x in products if x["id"] == o.product_id), None)
    if not p: return {"error": "not found"}
    total = p["price"]*o.quantity
    new = {"customer": o.customer_name, "product": p["name"], "qty": o.quantity, "total": total}
    orders.append(new)
    return new
