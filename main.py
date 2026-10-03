from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI(title="LONMA SUPERMARKET")

# In-memory DB (we will upgrade to Postgres later)
PRODUCTS = [
    {"id": "1", "name": "Milk - Fresh Dairy 500ml", "price": 65, "stock": 120, "cat": "Dairy"},
    {"id": "2", "name": "Bread - Supa Loaf", "price": 60, "stock": 80, "cat": "Bakery"},
    {"id": "3", "name": "Sugar - Kabras 1kg", "price": 165, "stock": 200, "cat": "Groceries"},
    {"id": "4", "name": "Cooking Oil - Elianto 1L", "price": 320, "stock": 50, "cat": "Groceries"},
]
SALES = []
CART = []

class Product(BaseModel):
    name: str
    price: float
    stock: int
    cat: str = "General"

class CartItem(BaseModel):
    product_id: str
    qty: int = 1

@app.head("/")
async def head_root():
    return Response(status_code=200)

@app.get("/", response_class=HTMLResponse)
async def supermarket_app():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LONMA SUPERMARKET | POS</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
:root{--gold:#FFD700;--black:#070707;--card:#121212;--line:rgba(255,215,0,0.2)}
*{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',sans-serif}
body{background:var(--black);color:#fff;display:flex;height:100vh}
.sidebar{width:260px;background:#000;border-right:1px solid var(--line);padding:25px;display:flex;flex-direction:column}
.logo{font-weight:800;letter-spacing:3px;font-size:18px}.logo span{color:var(--gold)}
.nav{margin-top:40px}.nav div{padding:14px 15px;cursor:pointer;border-radius:8px;margin-bottom:8px;color:#888;transition:0.2s}
.nav div.active,.nav div:hover{background:var(--gold);color:#000;font-weight:600}
.main{flex:1;overflow-y:auto;padding:25px;background:radial-gradient(circle at 80% 20%,rgba(255,215,0,0.08),transparent 30%)}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}
.grid{display:grid;grid-template-columns:2fr 1fr;gap:20px}
.products{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:15px}
.prod{background:#151515;border:1px solid #222;border-radius:12px;padding:15px;cursor:pointer;transition:0.2s}
.prod:hover{border-color:var(--gold);transform:translateY(-2px)}
.prod.price{color:var(--gold);font-weight:800;margin-top:8px}
.btn{background:var(--gold);color:#000;border:none;padding:10px 16px;border-radius:8px;font-weight:700;cursor:pointer;width:100%;margin-top:10px}
.btn-black{background:#000;color:var(--gold);border:1px solid var(--gold)}
input{width:100%;background:#000;border:1px solid #333;padding:12px;border-radius:8px;color:#fff;margin:6px 0}
table{width:100%;border-collapse:collapse;margin-top:10px}
th,td{padding:10px;text-align:left;border-bottom:1px solid #222;font-size:14px}
th{color:var(--gold);font-size:11px;letter-spacing:2px}
.badge{background:rgba(255,215,0,0.15);color:var(--gold);padding:4px 8px;border-radius:6px;font-size:11px}
#cartItems{max-height:300px;overflow-y:auto}
</style>
</head>
<body>
<div class="sidebar">
<div class="logo">LONMA <span>SUPERMARKET</span><div style="font-size:10px;letter-spacing:3px;color:#666;margin-top:5px">POS v1 • NAIROBI</div></div>
<div class="nav">
<div class="active" onclick="show('pos')">◈ POS - Sell</div>
<div onclick="show('stock')">⬢ Inventory</div>
<div onclick="show('sales')">⬣ Sales Report</div>
<div onclick="show('add')">+ Add Product</div>
</div>
<div style="margin-top:auto;font-size:11px;color:#555">● LIVE • app.lonmaorbit.co.ke<br>MPESA: Paybill Ready</div>
</div>

<div class="main">
<div class="top">
<h2 id="title">Point of Sale</h2>
<div class="badge" id="time">Loading...</div>
</div>

<div id="pos" class="grid">
<div>
<div style="display:flex;gap:10px;margin-bottom:15px"><input id="search" placeholder="Search product... Milk, Bread, Sugar" onkeyup="loadProducts()"></div>
<div class="products" id="productList"></div>
</div>
<div class="card">
<h3 style="color:var(--gold)">🛒 CART</h3>
<div id="cartItems" style="margin-top:15px;color:#777">Cart empty</div>
<hr style="margin:15px 0;border-color:#222">
<div style="display:flex;justify-content:space-between"><b>Total</b><b id="total" style="color:var(--gold)">KES 0</b></div>
<button class="btn" onclick="checkout()">CHECKOUT - MPESA / CASH</button>
<button class="btn btn-black" onclick="clearCart()">Clear Cart</button>
<div style="margin-top:15px;font-size:11px;color:#666">Customer: Walk-in • Cashier: Marlone</div>
</div>
</div>

<div id="stock" style="display:none" class="card"><h3>Inventory Stock</h3><table><thead><tr><th>PRODUCT</th><th>CAT</th><th>PRICE</th><th>STOCK</th></tr></thead><tbody id="stockTable"></tbody></table></div>
<div id="sales" style="display:none" class="card"><h3>Today Sales</h3><div style="display:flex;gap:15px;margin:15px 0"><div class="card" style="flex:1"><small>TOTAL SALES</small><h2 id="salesTotal" style="color:var(--gold)">KES 0</h2></div><div class="card" style="flex:1"><small>TRANSACTIONS</small><h2 id="salesCount">0</h2></div></div><table><thead><tr><th>TIME</th><th>ITEMS</th><th>TOTAL</th></tr></thead><tbody id="salesTable"></tbody></table></div>
<div id="add" style="display:none" class="card" style="max-width:500px"><h3>Add New Product</h3><input id="pName" placeholder="Product Name e.g Unga 2kg"><input id="pPrice" type="number" placeholder="Price KES"><input id="pStock" type="number" placeholder="Stock Qty"><input id="pCat" placeholder="Category e.g Groceries"><button class="btn" onclick="addProduct()">SAVE PRODUCT</button></div>
</div>

<script>
let products=[]; let cart=[]; let sales=[];
async function loadProducts(){
  let res=await fetch('/api/products'); products=await res.json();
  let q=document.getElementById('search').value.toLowerCase();
  let filtered=products.filter(p=>p.name.toLowerCase().includes(q));
  document.getElementById('productList').innerHTML=filtered.map(p=>`
    <div class="prod" onclick="addToCart('${p.id}')">
      <div style="font-size:11px;color:#666">${p.cat}</div>
      <div style="font-weight:600;margin-top:5px">${p.name}</div>
      <div class="price">KES ${p.price}</div>
      <div style="font-size:11px;color:${p.stock<10?'#ff4444':'#888'}">Stock: ${p.stock}</div>
    </div>`).join('');
  document.getElementById('stockTable').innerHTML=products.map(p=>`<tr><td>${p.name}</td><td>${p.cat}</td><td>KES ${p.price}</td><td style="color:${p.stock<10?'#ff4444':'#fff'}">${p.stock}</td></tr>`).join('');
}
function addToCart(id){
  let p=products.find(x=>x.id==id); let c=cart.find(x=>x.product_id==id);
  if(c) c.qty++; else cart.push({product_id:id,qty:1,name:p.name,price:p.price});
  renderCart();
}
function renderCart(){
  if(cart.length==0){document.getElementById('cartItems').innerHTML='Cart empty'; document.getElementById('total').innerText='KES 0'; return}
  let total=0; document.getElementById('cartItems').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #222"><span>${i.name} x${i.qty}</span><span style="color:var(--gold)">KES ${i.price*i.qty}</span></div>`}).join('');
  document.getElementById('total').innerText='KES '+total;
}
async function checkout(){
  if(cart.length==0) return alert('Cart empty');
  let res=await fetch('/api/checkout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart)});
  let data=await res.json(); alert('SALE SUCCESS: KES '+data.total+'\\nReceipt: '+data.receipt);
  cart=[]; renderCart(); loadProducts(); loadSales();
}
function clearCart(){cart=[]; renderCart();}
function show(id){
  ['pos','stock','sales','add'].forEach(x=>document.getElementById(x).style.display='none');
  document.getElementById(id).style.display=id=='pos'?'grid':'block';
  document.getElementById('title').innerText=id.toUpperCase();
  document.querySelectorAll('.nav div').forEach(d=>d.classList.remove('active'));
  event.target.classList.add('active');
  if(id=='sales') loadSales();
}
async function addProduct(){
  let body={name:document.getElementById('pName').value,price:parseFloat(document.getElementById('pPrice').value),stock:parseInt(document.getElementById('pStock').value),cat:document.getElementById('pCat').value};
  await fetch('/api/products',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  alert('Product added!'); loadProducts();
}
async function loadSales(){
  let res=await fetch('/api/sales'); sales=await res.json();
  let total=sales.reduce((s,x)=>s+x.total,0);
  document.getElementById('salesTotal').innerText='KES '+total;
  document.getElementById('salesCount').innerText=sales.length;
  document.getElementById('salesTable').innerHTML=sales.map(s=>`<tr><td>${new Date(s.time).toLocaleTimeString()}</td><td>${s.items.map(i=>i.name+' x'+i.qty).join(', ')}</td><td style="color:var(--gold)">KES ${s.total}</td></tr>`).join('');
}
setInterval(()=>{document.getElementById('time').innerText=new Date().toLocaleString()},1000);
loadProducts(); loadSales();
</script>
</body>
</html>
    """

@app.get("/api/products")
async def get_products():
    return PRODUCTS

@app.post("/api/products")
async def create_product(p: Product):
    new_p = {"id": str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat}
    PRODUCTS.append(new_p)
    return new_p

@app.post("/api/checkout")
async def checkout(cart_items: List[CartItem]):
    total = 0
    items_detail = []
    for ci in cart_items:
        prod = next((p for p in PRODUCTS if p["id"] == ci.product_id), None)
        if prod and prod["stock"] >= ci.qty:
            prod["stock"] -= ci.qty
            total += prod["price"] * ci.qty
            items_detail.append({"name": prod["name"], "qty": ci.qty, "price": prod["price"]})
    receipt = f"LONMA-{uuid.uuid4().hex[:8].upper()}"
    sale = {"receipt": receipt, "items": items_detail, "total": total, "time": datetime.now().isoformat()}
    SALES.append(sale)
    return sale

@app.get("/api/sales")
async def get_sales():
    return SALES[::-1]
