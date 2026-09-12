# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import models
from typing import List

app = FastAPI(title="LONMA Supermarket API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

products_db = [
    {"id": 1, "name": "Unga Ngano 2kg", "category": "Flour", "price": 180, "stock": 100, "unit": "bag", "image": ""},
    {"id": 2, "name": "Fresh Milk 500ml", "category": "Dairy", "price": 65, "stock": 200, "unit": "pkt", "image": ""},
    {"id": 3, "name": "White Bread", "category": "Bakery", "price": 70, "stock": 80, "unit": "pcs", "image": ""},
    {"id": 4, "name": "Cooking Oil 1L", "category": "Cooking", "price": 280, "stock": 50, "unit": "bottle", "image": ""},
    {"id": 5, "name": "Sugar 1kg", "category": "Essentials", "price": 160, "stock": 120, "unit": "kg", "image": ""},
    {"id": 6, "name": "Pishori Rice 2kg", "category": "Grains", "price": 350, "stock": 60, "unit": "bag", "image": ""},
    {"id": 7, "name": "Blue Band 500g", "category": "Spread", "price": 280, "stock": 40, "unit": "tin", "image": ""},
    {"id": 8, "name": "Eggs Tray", "category": "Dairy", "price": 420, "stock": 30, "unit": "tray", "image": ""},
]

orders_db = []
order_id_counter = 1

@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <html><head><title>LONMA Supermarket</title></head>
    <body style="font-family:sans-serif;text-align:center;padding:50px;background:#f5f5f5;">
    <h1 style="color:#2e7d32;">🛒 LONMA Supermarket API is LIVE</h1>
    <a href="/products" style="background:#2e7d32;color:white;padding:12px 24px;text-decoration:none;border-radius:8px;">View Products</a>
    <a href="/docs" style="background:#000;color:white;padding:12px 24px;text-decoration:none;border-radius:8px;margin-left:10px;">API Docs</a>
    </body></html>
    """

@app.get("/products", response_model=List[models.Product])
def get_all_products():
    return products_db

@app.get("/products/{product_id}")
def get_one_product(product_id: int):
    for product in products_db:
        if product["id"] == product_id:
            return product
    return {"error": "Product not found"}

@app.post("/order")
def create_order(order_data: models.OrderCreate):
    global order_id_counter
    product = next((p for p in products_db if p["id"] == order_data.product_id), None)
    if not product:
        return {"error": "Product not found"}
    if product["stock"] < order_data.quantity:
        return {"error": "Not enough stock"}
    total = product["price"] * order_data.quantity
    new_order = {
        "id": order_id_counter,
        "customer_name": order_data.customer_name,
        "phone": order_data.phone,
        "product_id": order_data.product_id,
        "product_name": product["name"],
        "quantity": order_data.quantity,
        "total": total,
        "status": "Pending"
    }
    orders_db.append(new_order)
    order_id_counter += 1
    product["stock"] -= order_data.quantity
    return {"message": "Order placed successfully!", "order": new_order}

@app.get("/orders")
def get_all_orders():
    return orders_db

@app.get("/categories")
def get_categories():
    cats = list(set([p["category"] for p in products_db]))
    return {"categories": cats}
