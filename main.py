from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List
import uuid, os
from datetime import datetime

app = FastAPI()

CATEGORIES = {
    "FOOD": {"icon": "🍞", "color": "#FF9800"},
    "DRINKS": {"icon": "🥤", "color": "#0096B0"},
    "UTENSILS": {"icon": "🍽️", "color": "#9C27B0"},
    "ELECTRONICS": {"icon": "🔌", "color": "#FFD700"},
}

SUPERMARKETS = {
    "lonma-westlands": {"name": "LONMA Westlands", "location": "Westlands Mall - HQ", "products": [], "sales": []},
    "naivas": {"name": "Naivas", "location": "100+ Branches", "products": [], "sales": []},
    "carrefour": {"name": "Carrefour", "location": "Two Rivers", "products": [], "sales": []},
    "chandarana": {"name": "Chandarana", "location": "Lavington", "products": [], "sales": []},
    "magunas": {"name": "Magunas", "location": "Murang'a", "products": [], "sales": []},
    "khetias": {"name": "Khetias", "location": "Western", "products": [], "sales": []},
    "mathais": {"name": "Mathai's", "location": "Mt Kenya", "products": [], "sales": []},
}

seed = [
    {"name": "Bread - Festive 400g", "price": 60, "stock": 300, "cat": "FOOD"},
    {"name": "Sugar - Kabras 1kg", "price": 165, "stock": 800, "cat": "FOOD"},
    {"name": "Rice - Pishori 2kg", "price": 380, "stock": 400, "cat": "FOOD"},
    {"name": "Milk - Brookside 500ml", "price": 65, "stock": 500, "cat": "DRINKS"},
    {"name": "Soda - Coca 500ml", "price": 70, "stock": 1000, "cat": "DRINKS"},
    {"name": "Water - Dasani 1L", "price": 50, "stock": 800, "cat": "DRINKS"},
    {"name": "Sufuria - 3pc Set", "price": 1850, "stock": 40, "cat": "UTENSILS"},
    {"name": "Plates - 6pc", "price": 950, "stock": 80, "cat": "UTENSILS"},
    {"name": "Gas Cooker - 2 Burner", "price": 4500, "stock": 15, "cat": "ELECTRONICS"},
    {"name": "Blender - Ramtons", "price": 3800, "stock": 25, "cat": "ELECTRONICS"},
]

for sm in SUPERMARKETS.values():
    sm["products"] = [dict(p, id=str(uuid.uuid4())[:6]) for p in seed]

class Product(BaseModel):
    name: str; price: float; stock: int; cat: str
class SupermarketCreate(BaseModel):
    id: str; name: str; location: str
class CartItem(BaseModel):
    product_id: str; qty: int = 1

@app.head("/")
async def head_root(): return Response(status_code=200)
@app.get("/logo")
async def get_logo():
    if os.path.exists("logo.jpg"): return FileResponse("logo.jpg")
    return Response(status_code=404)

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA ORBIT</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap" rel="stylesheet">
<style>
:root{--teal:#0096B0;--gold:#FFD700;--black:#070707;--card:#121212}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,sans-serif}
body{background:var(--black);color:#fff;overflow-y:auto}
.header{position:sticky;top:0;z-index:99;background:#000;border-bottom:2px solid var(--teal);padding:14px 16px;display:flex;align-items:center;gap:14px}
.header img{width:55px;height:55px;border-radius:12px;background:var(--teal);object-fit:cover}
.header h1{font-size:16px;letter-spacing:3px;font-weight:800}
.header small{color:var(--teal);font-size:10px;letter-spacing:2px}
.container{padding:14px;max-width:800px;margin:0 auto}
.card{background:var(--card);border:1px solid rgba(0,150,176,0.2);border-radius:14px;padding:14px;margin-bottom:14px}
.branch-scroll{display:flex;gap:8px;overflow-x:auto;padding-bottom:8px;-webkit-overflow-scrolling:touch}
.branch-pill{white-space:nowrap;padding:10px 14px;border-radius:20px;border:1px solid #333;background:#111;font-size:12px;font-weight:700;cursor:pointer}
.branch-pill.active{background:var(--teal);border-color:var(--teal);color:#fff}
.cat-tabs{display:flex;gap:8px;overflow-x:auto;padding-bottom:8px;margin:12px 0}
.cat-tab{white-space:nowrap;padding:10px 14px;border-radius:20px;font-weight:800;font-size:11px;cursor:pointer;border:1px solid #333}
.cat-tab.active{outline:2px solid #fff}
.products{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.prod{background:#1a1a1a;border:1px solid #222;border-radius:12px;padding:12px;cursor:pointer}
.prod:hover{border-color:var(--teal)}
.price{color:var(--teal);font-weight:800}
.btn{background:var(--teal);color:#fff;border:none;padding:12px;border-radius:10px;font-weight:800;width:100%;margin-top:8px;cursor:pointer}
input,select{width:100%;background:#000;border:1px solid #333;padding:11px;border-radius:10px;color:#fff;margin:5px 0}
.cart-item{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #222;font-size:13px}
@media(min-width:600px){.products{grid-template-columns:repeat(3,1fr)}}
</style></head><body>

<div class="header">
<img src="/logo" onerror="this.style.background='#0096B0'" alt="LO">
<div><h1>LONMA ORBIT</h1><small>SUPERCHAIN OS • 7 BRANCHES LIVE</small></div>
<div style="margin-left:auto;text-align:right"><small id="time" style="color:#666"></small><br><small style="color:var(--teal)" id="curName">Loading</small></div>
</div>

<div class="container">

<div class="card">
<small style="color:var(--teal);letter-spacing:2px;font-weight:800">SELECT BRANCH ↓ SCROLL SIDEWAYS</small>
<div class="branch-scroll" id="branchList"></div>
</div>

<div class="card">
<div style="display:flex;justify-content:space-between"><small>STOCK VALUE</small><small>SALES TODAY</small><small>ITEMS</small></div>
<div style="display:flex;justify-content:space-between;margin-top:6px"><h3 id="stockValue" style="color:var(--teal)">0</h3><h3 id="todaySales" style="color:var(--gold)">0</h3><h3 id="prodCount">0</h3></div>
</div>

<div class="card">
<small style="color:var(--teal);letter-spacing:2px;font-weight:800">CATEGORIES - TAP TO FILTER</small>
<div class="cat-tabs">
<div class="cat-tab active" style="background:#fff;color:#000" id="tab-ALL" onclick="filterCat('ALL')">ALL</div>
<div class="cat-tab" style="background:#FF9800;color:#000" id="tab-FOOD" onclick="filterCat('FOOD')">🍞 FOOD</div>
<div class="cat-tab" style="background:#0096B0;color:#fff" id="tab-DRINKS" onclick="filterCat('DRINKS')">🥤 DRINKS</div>
<div class="cat-tab" style="background:#9C27B0;color:#fff" id="tab-UTENSILS" onclick="filterCat('UTENSILS')">🍽️ UTENSILS</div>
<div class="cat-tab" style="background:#FFD700;color:#000" id="tab-ELECTRONICS" onclick="filterCat('ELECTRONICS')">🔌 ELECTRONICS</div>
</div>
<input id="search" placeholder="🔍 Search products..." onkeyup="renderProducts()">
<div class="products" id="plist" style="margin-top:12px"></div>
</div>

<div class="card">
<b>🛒 CART - <span id="cartBranch" style="color:var(--teal)"></span></b>
<div id="cart" style="margin-top:10px;color:#777">Empty - Tap product above</div>
<div style="display:flex;justify-content:space-between;margin-top:12px;padding-top:10px;border-top:1px solid #333"><b>TOTAL</b><b id="total" style="color:var(--teal);font-size:18px">KES 0</b></div>
<button class="btn" onclick="checkout()">✅ CHECKOUT</button>
<button class="btn" style="background:#000;border:1px solid var(--teal);color:var(--teal)" onclick="cart=[];renderCart()">Clear Cart</button>
</div>

<div class="card">
<b style="color:var(--teal)">+ ADD NEW PRODUCT ↓</b>
<input id="pName" placeholder="Product Name">
<select id="pCat"><option value="FOOD">FOOD</option><option value="DRINKS">DRINKS</option><option value="UTENSILS">UTENSILS</option><option value="ELECTRONICS">ELECTRONICS</option></select>
<input id="pPrice" type="number" placeholder="Price KES"><input id="pStock" type="number" placeholder="Stock Quantity">
<button class="btn" style="background:var(--gold);color:#000" onclick="addProduct()">SAVE PRODUCT</button>
</div>

<div class="card">
<b>📜 SALES HISTORY - SCROLL DOWN</b>
<div id="salesList" style="margin-top:10px"></div>
</div>

<div style="text-align:center;padding:30px 0;color:#444;font-size:11px">
LO LONMA ORBIT © 2026<br>app.lonmaorbit.co.ke<br>Scroll to bottom ↑ All here!
</div>

</div>

<script>
let current='lonma-westlands'; let branches={}; let cart=[]; let activeCat='ALL';
async function loadBranches(){
  let r=await fetch('/api/supermarkets'); branches=await r.json();
  let totVal=0; Object.values(branches).forEach(b=>b.products.forEach(p=>totVal+=p.price*p.stock));
  document.getElementById('stockValue').innerText='KES '+totVal.toLocaleString();
  document.getElementById('branchList').innerHTML=Object.entries(branches).map(([id,b])=>`<div class="branch-pill ${id==current?'active':''}" onclick="selectBranch('${id}')">${b.name}</div>`).join('');
  let b=branches[current]; document.getElementById('curName').innerText=b.name; document.getElementById('cartBranch').innerText=b.name; document.getElementById('prodCount').innerText=b.products.length;
  renderProducts(); loadSales();
}
function selectBranch(id){current=id; cart=[]; renderCart(); loadBranches(); window.scrollTo({top:0,behavior:'smooth'});}
function filterCat(cat){activeCat=cat; document.querySelectorAll('.cat-tab').forEach(t=>t.classList.remove('active')); document.getElementById('tab-'+cat).classList.add('active'); renderProducts();}
function renderProducts(){
  let b=branches[current]; if(!b) return; let q=document.getElementById('search').value.toLowerCase();
  let list=b.products.filter(p=>(activeCat=='ALL'||p.cat==activeCat)&&p.name.toLowerCase().includes(q));
  let colors={"FOOD":"#FF9800","DRINKS":"#0096B0","UTENSILS":"#9C27B0","ELECTRONICS":"#FFD700"};
  document.getElementById('plist').innerHTML=list.map(p=>`<div class="prod" onclick="addCart('${p.id}')"><div style="display:flex;justify-content:space-between"><small style="background:${colors[p.cat]};color:#000;padding:2px 6px;border-radius:6px;font-size:8px;font-weight:800">${p.cat}</small><small style="color:${p.stock<10?'#f44':'#666'}">${p.stock} left</small></div><div style="font-weight:700;margin-top:8px;font-size:13px">${p.name}</div><div class="price">KES ${p.price}</div></div>`).join('');
}
function addCart(pid){let p=branches[current].products.find(x=>x.id==pid); let c=cart.find(x=>x.product_id==pid); if(c) c.qty++; else cart.push({product_id:pid,qty:1,name:p.name,price:p.price,cat:p.cat}); renderCart(); document.getElementById('cart').scrollIntoView({behavior:'smooth'});}
function renderCart(){if(cart.length==0){document.getElementById('cart').innerHTML='Empty - Tap product above'; document.getElementById('total').innerText='KES 0'; return} let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div class="cart-item"><span>[${i.cat}] ${i.name} x${i.qty}</span><span style="color:var(--teal)">KES ${i.price*i.qty}</span></div>`}).join(''); document.getElementById('total').innerText='KES '+total.toLocaleString();}
async function checkout(){if(cart.length==0) return alert('Cart empty'); let r=await fetch(`/api/${current}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart)}); let d=await r.json(); alert('✅ SALE!\\n'+d.receipt+'\\nTotal KES '+d.total+'\\nBranch: '+branches[current].name); cart=[]; renderCart(); loadBranches();}
async function addProduct(){let body={name:document.getElementById('pName').value,price:parseFloat(document.getElementById('pPrice').value),stock:parseInt(document.getElementById('pStock').value),cat:document.getElementById('pCat').value}; if(!body.name) return alert('Name required'); await fetch(`/api/${current}/products`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); document.getElementById('pName').value=''; loadBranches(); window.scrollTo({top:400,behavior:'smooth'});}
async function loadSales(){let r=await fetch(`/api/${current}/sales`); let sales=await r.json(); let tot=sales.reduce((s,x)=>s+x.total,0); document.getElementById('todaySales').innerText='KES '+tot.toLocaleString(); document.getElementById('salesList').innerHTML=sales.slice(0,20).map(s=>`<div style="padding:8px 0;border-bottom:1px solid #222;display:flex;justify-content:space-between;font-size:13px"><span>${s.items.map(i=>i.name.substring(0,15)+' x'+i.qty).join(', ')}</span><b style="color:var(--teal)">KES ${s.total}</b></div>`).join('')||'<small style="color:#555">No sales yet</small>';}
setInterval(()=>{document.getElementById('time').innerText=new Date().toLocaleTimeString()},1000); loadBranches();
</script></body></html>
    """

@app.get("/api/supermarkets")
async def get_markets(): return SUPERMARKETS
@app.post("/api/supermarkets")
async def create_market(sm: SupermarketCreate):
    SUPERMARKETS[sm.id] = {"name": sm.name, "location": sm.location, "owner": "Custom", "products": [dict(p, id=str(uuid.uuid4())[:6]) for p in seed], "sales": []}
    return SUPERMARKETS[sm.id]
@app.get("/api/{branch_id}/sales")
async def branch_sales(branch_id: str): return SUPERMARKETS.get(branch_id, {}).get("sales", [])[::-1]
@app.post("/api/{branch_id}/products")
async def add_prod(branch_id: str, p: Product):
    new_p = {"id": str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat.upper()}
    SUPERMARKETS[branch_id]["products"].append(new_p); return new_p
@app.post("/api/{branch_id}/checkout")
async def checkout(branch_id: str, cart: List[CartItem]):
    sm = SUPERMARKETS[branch_id]; total=0; items=[]
    for ci in cart:
        prod = next((x for x in sm["products"] if x["id"]==ci.product_id), None)
        if prod and prod["stock"]>=ci.qty:
            prod["stock"]-=ci.qty; total+=prod["price"]*ci.qty; items.append({"name":prod["name"],"qty":ci.qty})
    sale={"receipt":f"{branch_id[:3].upper()}-{uuid.uuid4().hex[:6].upper()}","items":items,"total":total,"time":datetime.now().isoformat()}
    sm["sales"].append(sale); return sale
