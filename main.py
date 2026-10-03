from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict
import uuid
from datetime import datetime

app = FastAPI()

# MULTI-SUPERMARKET DB
SUPERMARKETS = {
    "westlands": {"name": "LONMA Westlands", "location": "Westlands Mall", "products": [], "sales": []},
    "kitengela": {"name": "LONMA Kitengela", "location": "Kitengela Town", "products": [], "sales": []},
    "mombasa": {"name": "LONMA Mombasa Rd", "location": "Mombasa Road", "products": [], "sales": []},
}
# Seed products for all
seed = [
    {"id": "1", "name": "Milk 500ml", "price": 65, "stock": 120, "cat": "Dairy"},
    {"id": "2", "name": "Bread Supa Loaf", "price": 60, "stock": 80, "cat": "Bakery"},
    {"id": "3", "name": "Sugar 1kg", "price": 165, "stock": 200, "cat": "Groceries"},
]
for sm in SUPERMARKETS.values():
    sm["products"] = [dict(p) for p in seed]

class Product(BaseModel):
    name: str; price: float; stock: int; cat: str = "General"
class SupermarketCreate(BaseModel):
    id: str; name: str; location: str
class CartItem(BaseModel):
    product_id: str; qty: int = 1

@app.head("/")
async def head_root(): return Response(status_code=200)

@app.get("/", response_class=HTMLResponse)
async def app_ui():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA SUPERCHAIN</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap" rel="stylesheet">
<style>
:root{--gold:#FFD700;--black:#070707;--card:#121212;--line:rgba(255,215,0,0.2)}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,sans-serif}
body{background:var(--black);color:#fff;display:flex;height:100vh}
.sidebar{width:280px;background:#000;border-right:1px solid var(--line);padding:20px;display:flex;flex-direction:column;overflow-y:auto}
.logo{font-weight:800;letter-spacing:2px}.logo span{color:var(--gold)}
.branch{margin-top:20px}.branch div{padding:12px;border:1px solid #222;border-radius:10px;margin-bottom:8px;cursor:pointer}
.branch div.active{background:var(--gold);color:#000;font-weight:700;border-color:var(--gold)}
.main{flex:1;overflow-y:auto;padding:20px}
.top{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin-top:15px}
.products{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:12px}
.prod{background:#151515;border:1px solid #222;border-radius:12px;padding:14px;cursor:pointer}
.prod:hover{border-color:var(--gold)}.price{color:var(--gold);font-weight:800}
.btn{background:var(--gold);color:#000;border:none;padding:10px;border-radius:8px;font-weight:800;cursor:pointer;width:100%;margin-top:8px}
input,select{width:100%;background:#000;border:1px solid #333;padding:10px;border-radius:8px;color:#fff;margin:5px 0}
.grid2{display:grid;grid-template-columns:2fr 1fr;gap:15px}
</style></head><body>
<div class="sidebar">
<div class="logo">LONMA <span>SUPERCHAIN</span><div style="font-size:9px;color:#666;letter-spacing:2px">MULTI-BRANCH POS</div></div>

<div style="margin-top:20px"><small style="color:var(--gold);letter-spacing:2px">BRANCHES</small></div>
<div class="branch" id="branchList"></div>

<div class="card" style="margin-top:15px">
<small style="color:var(--gold)">+ ADD SUPERMARKET</small>
<input id="smId" placeholder="id e.g ruiru"><input id="smName" placeholder="Name e.g LONMA Ruiru"><input id="smLoc" placeholder="Location">
<button class="btn" onclick="addSupermarket()">ADD BRANCH</button>
</div>

<div style="margin-top:auto;font-size:10px;color:#555">● LIVE • app.lonmaorbit.co.ke</div>
</div>

<div class="main">
<div class="top"><h2 id="curBranch">Loading...</h2><div><span id="branchSales" style="color:var(--gold)"></span></div></div>

<div class="grid2">
<div>
<input id="search" placeholder="Search products..." onkeyup="renderProducts()">
<div class="products" id="plist" style="margin-top:12px"></div>
</div>
<div>
<div class="card"><b>🛒 CART</b><div id="cart" style="margin-top:10px;color:#777">Empty</div><div style="display:flex;justify-content:space-between;margin-top:10px"><b>Total</b><b id="total" style="color:var(--gold)">0</b></div><button class="btn" onclick="checkout()">CHECKOUT</button><button class="btn" style="background:#000;color:var(--gold);border:1px solid var(--gold)" onclick="cart=[];renderCart()">Clear</button></div>
<div class="card"><b>+ Product to <span id="curBranch2"></span></b><input id="pName" placeholder="Name"><input id="pPrice" type="number" placeholder="Price"><input id="pStock" type="number" placeholder="Stock"><input id="pCat" placeholder="Category"><button class="btn" onclick="addProduct()">SAVE TO BRANCH</button></div>
</div>
</div>

<div class="card"><b>Sales Today - <span id="salesBranch"></span></b><div style="display:flex;gap:10px;margin-top:10px"><div class="card" style="flex:1"><small>TOTAL</small><h2 id="sTotal" style="color:var(--gold)">0</h2></div><div class="card" style="flex:1"><small>COUNT</small><h2 id="sCount">0</h2></div></div><div id="salesList" style="margin-top:10px"></div></div>
</div>

<script>
let currentBranch='westlands'; let branches={}; let cart=[];
async function loadBranches(){
  let r=await fetch('/api/supermarkets'); branches=await r.json();
  document.getElementById('branchList').innerHTML=Object.entries(branches).map(([id,b])=>`<div class="${id==currentBranch?'active':''}" onclick="selectBranch('${id}')"><b>${b.name}</b><br><small>${b.location} • ${b.products.length} items</small></div>`).join('');
  let b=branches[currentBranch];
  document.getElementById('curBranch').innerText=b.name; document.getElementById('curBranch2').innerText=b.name; document.getElementById('salesBranch').innerText=b.name;
  renderProducts();
}
function selectBranch(id){currentBranch=id; cart=[]; renderCart(); loadBranches(); loadSales();}
async function renderProducts(){
  let b=branches[currentBranch]; if(!b) return;
  let q=document.getElementById('search').value.toLowerCase();
  let prods=b.products.filter(p=>p.name.toLowerCase().includes(q));
  document.getElementById('plist').innerHTML=prods.map(p=>`<div class="prod" onclick="addCart('${p.id}')"><small style="color:#666">${p.cat}</small><div style="font-weight:700;margin-top:4px">${p.name}</div><div class="price">KES ${p.price}</div><small style="color:${p.stock<10?'#f44':'#888'}">Stock ${p.stock}</small></div>`).join('');
}
function addCart(pid){
  let p=branches[currentBranch].products.find(x=>x.id==pid);
  let c=cart.find(x=>x.product_id==pid); if(c) c.qty++; else cart.push({product_id:pid,qty:1,name:p.name,price:p.price}); renderCart();
}
function renderCart(){
  if(cart.length==0){document.getElementById('cart').innerHTML='Empty'; document.getElementById('total').innerText='KES 0'; return}
  let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #222"><span>${i.name} x${i.qty}</span><span style="color:var(--gold)">${i.price*i.qty}</span></div>`}).join('');
  document.getElementById('total').innerText='KES '+total;
}
async function checkout(){
  if(cart.length==0) return alert('Empty');
  let r=await fetch(`/api/${currentBranch}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart)});
  let d=await r.json(); alert('SOLD: KES '+d.total+' Receipt '+d.receipt+'\\nBranch: '+branches[currentBranch].name); cart=[]; renderCart(); loadBranches(); loadSales();
}
async function addProduct(){
  let body={name:document.getElementById('pName').value,price:parseFloat(document.getElementById('pPrice').value),stock:parseInt(document.getElementById('pStock').value),cat:document.getElementById('pCat').value};
  await fetch(`/api/${currentBranch}/products`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); loadBranches();
}
async function addSupermarket(){
  let body={id:document.getElementById('smId').value.toLowerCase(),name:document.getElementById('smName').value,location:document.getElementById('smLoc').value};
  await fetch('/api/supermarkets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); loadBranches();
}
async function loadSales(){
  let r=await fetch(`/api/${currentBranch}/sales`); let sales=await r.json();
  let tot=sales.reduce((s,x)=>s+x.total,0); document.getElementById('sTotal').innerText='KES '+tot; document.getElementById('sCount').innerText=sales.length;
  document.getElementById('salesList').innerHTML=sales.slice(0,10).map(s=>`<div style="padding:8px 0;border-bottom:1px solid #222;display:flex;justify-content:space-between"><span>${s.items.map(i=>i.name+' x'+i.qty).join(', ')}</span><span style="color:var(--gold)">KES ${s.total}</span></div>`).join('');
}
loadBranches(); setInterval(loadBranches,3000);
</script></body></html>
    """

@app.get("/api/supermarkets")
async def get_supermarkets(): return SUPERMARKETS

@app.post("/api/supermarkets")
async def create_sm(sm: SupermarketCreate):
    SUPERMARKETS[sm.id] = {"name": sm.name, "location": sm.location, "products": [dict(p) for p in seed], "sales": []}
    return SUPERMARKETS[sm.id]

@app.get("/api/{branch_id}/sales")
async def get_branch_sales(branch_id: str): return SUPERMARKETS.get(branch_id, {}).get("sales", [])[::-1]

@app.post("/api/{branch_id}/products")
async def add_branch_product(branch_id: str, p: Product):
    new_p = {"id": str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat}
    SUPERMARKETS[branch_id]["products"].append(new_p); return new_p

@app.post("/api/{branch_id}/checkout")
async def branch_checkout(branch_id: str, cart: List[CartItem]):
    sm = SUPERMARKETS[branch_id]; total=0; items=[]
    for ci in cart:
        prod = next((x for x in sm["products"] if x["id"]==ci.product_id), None)
        if prod and prod["stock"]>=ci.qty:
            prod["stock"]-=ci.qty; total+=prod["price"]*ci.qty; items.append({"name":prod["name"],"qty":ci.qty})
    sale={"receipt":f"{branch_id.upper()}-{uuid.uuid4().hex[:6].upper()}","items":items,"total":total,"time":datetime.now().isoformat()}
    sm["sales"].append(sale); return sale
