from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI()

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
class CartItem(BaseModel):
    product_id: str; qty: int = 1

@app.head("/")
async def head_root(): return Response(status_code=200)

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA ORBIT</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui,sans-serif}
body{background:#070707;color:#fff}
.header{position:sticky;top:0;z-index:99;background:#000;border-bottom:2px solid #0096B0;padding:12px 14px;display:flex;align-items:center;gap:12px}
.logo{width:50px;height:50px;background:#0096B0;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:20px;letter-spacing:-1px;color:#fff;box-shadow:0 4px 15px rgba(0,150,176,0.4)}
.container{padding:12px;max-width:700px;margin:0 auto}
.card{background:#121212;border:1px solid rgba(0,150,176,0.18);border-radius:14px;padding:12px;margin-bottom:12px}
.branch-scroll{display:flex;gap:8px;overflow-x:auto;padding-bottom:6px}
.pill{white-space:nowrap;padding:9px 13px;border-radius:20px;border:1px solid #333;background:#151515;font-size:12px;font-weight:700;cursor:pointer}
.pill.active{background:#0096B0;color:#fff;border-color:#0096B0}
.cat-tabs{display:flex;gap:7px;overflow-x:auto;margin:10px 0;padding-bottom:6px}
.cat{white-space:nowrap;padding:8px 12px;border-radius:20px;font-size:11px;font-weight:800;cursor:pointer}
.products{display:grid;grid-template-columns:repeat(2,1fr);gap:9px}
.prod{background:#1a1a1a;border:1px solid #222;border-radius:12px;padding:11px;cursor:pointer}
.prod:active{transform:scale(0.97)}
.price{color:#0096B0;font-weight:800;margin-top:4px}
.btn{background:#0096B0;color:#fff;border:none;padding:12px;border-radius:10px;font-weight:800;width:100%;margin-top:8px;cursor:pointer;font-size:14px}
input,select{width:100%;background:#000;border:1px solid #333;padding:11px;border-radius:10px;color:#fff;margin:4px 0}
</style></head><body>
<div class="header">
<div class="logo">LO</div>
<div><div style="font-weight:800;letter-spacing:3px;font-size:14px">LONMA ORBIT</div><div style="color:#0096B0;font-size:9px;letter-spacing:2px">SUPERCHAIN OS • 7 BRANCHES</div></div>
<div style="margin-left:auto;text-align:right"><small id="time" style="color:#555"></small><br><small id="curName" style="color:#0096B0;font-size:11px"></small></div>
</div>

<div class="container">
<div class="card"><small style="color:#0096B0;font-weight:800;letter-spacing:2px;font-size:10px">BRANCHES - SCROLL →</small><div class="branch-scroll" id="branchList" style="margin-top:8px"></div></div>

<div class="card" style="display:flex;justify-content:space-between;text-align:center">
<div><small style="color:#888">STOCK VALUE</small><div id="stockValue" style="color:#0096B0;font-weight:800;margin-top:2px">0</div></div>
<div><small style="color:#888">TODAY SALES</small><div id="todaySales" style="color:#FFD700;font-weight:800;margin-top:2px">0</div></div>
<div><small style="color:#888">ITEMS</small><div id="prodCount" style="font-weight:800;margin-top:2px">0</div></div>
</div>

<div class="card">
<small style="color:#0096B0;font-weight:800;letter-spacing:2px;font-size:10px">CATEGORIES - TAP TO FILTER ↓</small>
<div class="cat-tabs">
<div class="cat active" style="background:#fff;color:#000" id="tab-ALL" onclick="filterCat('ALL')">ALL</div>
<div class="cat" style="background:#FF9800" id="tab-FOOD" onclick="filterCat('FOOD')">🍞 FOOD</div>
<div class="cat" style="background:#0096B0;color:#fff" id="tab-DRINKS" onclick="filterCat('DRINKS')">🥤 DRINKS</div>
<div class="cat" style="background:#9C27B0;color:#fff" id="tab-UTENSILS" onclick="filterCat('UTENSILS')">🍽️ UTENSILS</div>
<div class="cat" style="background:#FFD700" id="tab-ELECTRONICS" onclick="filterCat('ELECTRONICS')">🔌 ELECTRONICS</div>
</div>
<input id="search" placeholder="🔍 Search..." onkeyup="renderProducts()">
<div class="products" id="plist" style="margin-top:10px"></div>
</div>

<div class="card">
<b>🛒 CART - <span id="cartBranch" style="color:#0096B0"></span></b>
<div id="cart" style="margin-top:8px;color:#666;font-size:13px">Empty - Tap product</div>
<div style="display:flex;justify-content:space-between;margin-top:10px;border-top:1px solid #222;padding-top:10px"><b>TOTAL</b><b id="total" style="color:#0096B0;font-size:18px">KES 0</b></div>
<button class="btn" onclick="checkout()">CHECKOUT - PRINT</button>
<button class="btn" style="background:#000;border:1px solid #0096B0;color:#0096B0" onclick="cart=[];renderCart()">Clear</button>
</div>

<div class="card">
<b style="color:#0096B0;font-size:13px">+ ADD PRODUCT (SCROLL DOWN)</b>
<input id="pName" placeholder="Name">
<select id="pCat"><option>FOOD</option><option>DRINKS</option><option>UTENSILS</option><option>ELECTRONICS</option></select>
<input id="pPrice" type="number" placeholder="Price KES"><input id="pStock" type="number" placeholder="Stock">
<button class="btn" style="background:#FFD700;color:#000" onclick="addProduct()">SAVE</button>
</div>

<div class="card"><b style="font-size:13px">📜 SALES HISTORY - BOTTOM</b><div id="salesList" style="margin-top:8px;font-size:12px"></div></div>

<div style="text-align:center;padding:25px;color:#333;font-size:10px;letter-spacing:2px">LO LONMA ORBIT © 2026<br>SCROLL TO BOTTOM - EVERYTHING HERE<br>app.lonmaorbit.co.ke</div>
</div>

<script>
let current='lonma-westlands'; let branches={}; let cart=[]; let activeCat='ALL';
async function loadBranches(){
  let r=await fetch('/api/supermarkets'); branches=await r.json();
  let tot=0; Object.values(branches).forEach(b=>b.products.forEach(p=>tot+=p.price*p.stock));
  document.getElementById('stockValue').innerText='KES '+tot.toLocaleString();
  document.getElementById('branchList').innerHTML=Object.entries(branches).map(([id,b])=>`<div class="pill ${id==current?'active':''}" onclick="selectBranch('${id}')">${b.name}</div>`).join('');
  let b=branches[current]; document.getElementById('curName').innerText=b.name; document.getElementById('cartBranch').innerText=b.name; document.getElementById('prodCount').innerText=b.products.length;
  renderProducts(); loadSales();
}
function selectBranch(id){current=id; cart=[]; renderCart(); loadBranches();}
function filterCat(c){activeCat=c; document.querySelectorAll('.cat').forEach(x=>x.classList.remove('active')); document.getElementById('tab-'+c).classList.add('active'); renderProducts();}
function renderProducts(){
  let b=branches[current]; if(!b) return; let q=document.getElementById('search').value.toLowerCase();
  let list=b.products.filter(p=>(activeCat=='ALL'||p.cat==activeCat)&&p.name.toLowerCase().includes(q));
  let col={"FOOD":"#FF9800","DRINKS":"#0096B0","UTENSILS":"#9C27B0","ELECTRONICS":"#FFD700"};
  document.getElementById('plist').innerHTML=list.map(p=>`<div class="prod" onclick="addCart('${p.id}')"><div style="display:flex;justify-content:space-between"><small style="background:${col[p.cat]};color:#000;padding:2px 6px;border-radius:5px;font-size:8px;font-weight:900">${p.cat}</small><small style="color:#666">${p.stock}</small></div><div style="font-weight:700;margin-top:6px;font-size:12px">${p.name}</div><div class="price">KES ${p.price}</div></div>`).join('');
}
function addCart(pid){let p=branches[current].products.find(x=>x.id==pid); let c=cart.find(x=>x.product_id==pid); if(c) c.qty++; else cart.push({product_id:pid,qty:1,name:p.name,price:p.price,cat:p.cat}); renderCart();}
function renderCart(){if(cart.length==0){document.getElementById('cart').innerHTML='Empty - Tap product'; document.getElementById('total').innerText='KES 0'; return} let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #222"><span>${i.cat} ${i.name} x${i.qty}</span><span style="color:#0096B0">KES ${i.price*i.qty}</span></div>`}).join(''); document.getElementById('total').innerText='KES '+total.toLocaleString();}
async function checkout(){if(cart.length==0) return alert('Empty'); let r=await fetch(`/api/${current}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart)}); let d=await r.json(); alert('✅ '+d.receipt+'\\nKES '+d.total+' @ '+branches[current].name); cart=[]; renderCart(); loadBranches();}
async function addProduct(){let body={name:document.getElementById('pName').value,price:parseFloat(document.getElementById('pPrice').value),stock:parseInt(document.getElementById('pStock').value),cat:document.getElementById('pCat').value}; if(!body.name) return alert('Name'); await fetch(`/api/${current}/products`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); loadBranches();}
async function loadSales(){let r=await fetch(`/api/${current}/sales`); let s=await r.json(); let tot=s.reduce((a,b)=>a+b.total,0); document.getElementById('todaySales').innerText='KES '+tot.toLocaleString(); document.getElementById('salesList').innerHTML=s.slice(0,15).map(x=>`<div style="padding:6px 0;border-bottom:1px solid #222;display:flex;justify-content:space-between"><span>${x.items.map(i=>i.name.substring(0,12)+' x'+i.qty).join(', ')}</span><b style="color:#0096B0">KES ${x.total}</b></div>`).join('')||'No sales';}
setInterval(()=>{let el=document.getElementById('time'); if(el) el.innerText=new Date().toLocaleTimeString()},1000); loadBranches();
</script></body></html>
    """

@app.get("/api/supermarkets")
async def get_markets(): return SUPERMARKETS
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
