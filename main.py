from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OrderCreate(BaseModel):
    customer_name: str
    phone: str
    product_id: int
    quantity: int

products = [
    {"id": 1, "name": "Unga Ngano 2kg", "category": "Flour", "price": 180, "stock": 100, "img": "🌾"},
    {"id": 2, "name": "Fresh Milk 500ml", "category": "Dairy", "price": 65, "stock": 200, "img": "🥛"},
    {"id": 3, "name": "White Bread", "category": "Bakery", "price": 70, "stock": 80, "img": "🍞"},
    {"id": 4, "name": "Cooking Oil 1L", "category": "Cooking", "price": 280, "stock": 50, "img": "🫒"},
    {"id": 5, "name": "Sugar 1kg", "category": "Essentials", "price": 160, "stock": 120, "img": "🍬"},
    {"id": 6, "name": "Pishori Rice 2kg", "category": "Grains", "price": 350, "stock": 60, "img": "🍚"},
    {"id": 7, "name": "Blue Band 500g", "category": "Spread", "price": 280, "stock": 40, "img": "🧈"},
    {"id": 8, "name": "Eggs Tray", "category": "Dairy", "price": 420, "stock": 30, "img": "🥚"},
]
orders = []

SHOP_HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA Supermarket</title>
<style>
body{font-family:system-ui;margin:0;background:#f7f7f7}
header{background:#2e7d32;color:#fff;padding:16px;text-align:center;position:sticky;top:0;z-index:10}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;padding:16px}
.card{background:#fff;border-radius:16px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.card h3{margin:6px 0;font-size:14px} .price{color:#2e7d32;font-weight:700}
button{background:#2e7d32;color:#fff;border:0;padding:8px 12px;border-radius:10px;width:100%;margin-top:8px}
#cart{position:fixed;bottom:0;left:0;right:0;background:#fff;padding:12px;border-top:1px solid #ddd}
input{padding:8px;border-radius:8px;border:1px solid #ccc;width:100%;margin:4px 0}
</style></head>
<body>
<header><h2>🛒 LONMA Supermarket</h2><small>app.lonmaorbit.co.ke</small></header>
<div class="grid" id="grid"></div>
<div id="cart">
<input id="name" placeholder="Your Name">
<input id="phone" placeholder="Phone 07xx">
<button onclick="checkout()">Place Order via WhatsApp</button>
<p id="status" style="text-align:center"></p>
</div>
<script>
const products = """ + str(products) + """;
let cart = [];
function render(){
 document.getElementById('grid').innerHTML = products.map(p=>`
  <div class="card"><div style="font-size:40px;text-align:center">${p.img}</div>
  <h3>${p.name}</h3><small>${p.category} • Stock ${p.stock}</small>
  <div class="price">KSh ${p.price}</div>
  <button onclick="add(${p.id})">Add to Cart</button></div>`).join('');
}
function add(id){ cart.push(id); document.getElementById('status').innerText = cart.length + ' items in cart'; }
async function checkout(){
 const name=document.getElementById('name').value; const phone=document.getElementById('phone').value;
 if(!name||!phone) return alert('Enter name and phone');
 if(cart.length==0) return alert('Cart empty');
 for(let id of cart){
   await fetch('/order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({customer_name:name,phone:phone,product_id:id,quantity:1})})
 }
 const msg = `Hello LONMA! Order from ${name} (${phone}): ` + cart.map(id=>products.find(p=>p.id==id).name).join(', ');
 window.open('https://wa.me/254700000000?text='+encodeURIComponent(msg),'_blank');
 document.getElementById('status').innerText='Order Sent! ✅'; cart=[];
}
render();
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def shop():
    return SHOP_HTML

@app.get("/products")
def get_products():
    return products

@app.post("/order")
def create(o: OrderCreate):
    p = next((x for x in products if x["id"] == o.product_id), None)
    if not p: return {"error": "not found"}
    orders.append({"customer": o.customer_name, "phone": o.phone, "product": p["name"], "qty": o.quantity, "total": p["price"]*o.quantity})
    p["stock"] -= o.quantity
    return {"ok": True}

@app.get("/orders")
def get_orders():
    return orders
