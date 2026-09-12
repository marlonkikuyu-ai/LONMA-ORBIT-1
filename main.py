from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from typing import List

app = FastAPI(title="Supermarket App - LONMA ORBIT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample supermarket products
products_db = [
    {"id": 1, "name": "Unga 2kg", "category": "Flour", "price": 180, "stock": 50, "image": ""},
    {"id": 2, "name": "Milk 500ml", "category": "Dairy", "price": 65, "stock": 100, "image": ""},
    {"id": 3, "name": "Bread", "category": "Bakery", "price": 70, "stock": 40, "image": ""},
    {"id": 4, "name": "Cooking Oil 1L", "category": "Cooking", "price": 280, "stock": 30, "image": ""},
    {"id": 5, "name": "Sugar 1kg", "category": "Essentials", "price": 160, "stock": 60, "image": ""},
    {"id": 6, "name": "Rice 2kg", "category": "Grains", "price": 350, "stock": 25, "image": ""},
]

orders_db = []

@app.get("/")
def home():
    return {"message": "Supermarket API is Live", "total_products": len(products_db)}

@app.get("/products", response_model=List[models.Product])
def get_products():
    return products_db

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products_db:
        if p["id"] == product_id:
            return p
    return {"error": "Product not found"}

@app.post("/order")
def create_order(order: models.Order):
    orders_db.append(order)
    return {"message": "Order received", "order": order}

@app.get("/orders")
def get_orders():
    return orders_db
