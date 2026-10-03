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
    "lonma-westlands": {"name": "LONMA Westlands", "location": "Westlands Mall - HQ", "owner": "Marlone", "products": [], "sales": []},
    "naivas": {"name": "Naivas", "location": "100+ Branches", "owner": "Naivas", "products": [], "sales": []},
    "carrefour": {"name": "Carrefour", "location": "Two Rivers, Junction", "owner": "Majid Al Futtaim", "products": [], "sales": []},
    "chandarana": {"name": "Chandarana", "location": "Lavington, Yaya", "owner": "Chandarana", "products": [], "sales": []},
    "magunas": {"name": "Magunas", "location": "Murang'a", "owner": "Magunas", "products": [], "sales": []},
    "khetias": {"name": "Khetias", "location": "Western", "owner": "Khetias", "products": [], "sales": []},
    "mathais": {"name": "Mathai's", "location": "Mt Kenya", "owner": "Mathai's", "products": [], "sales": []},
}

seed = [
    {"name": "Bread - Festive 400g", "price": 60, "stock": 300, "cat": "FOOD"},
    {"name": "Sugar - Kabras 1kg", "price": 165, "stock": 800, "cat": "FOOD"},
    {"name": "Rice - Pishori 2kg", "price": 380, "stock": 400, "cat": "FOOD"},
    {"name": "Flour - Ajab 2kg", "price": 180, "stock": 600, "cat": "FOOD"},
    {"name": "Milk - Brookside 500ml", "price": 65, "stock": 500, "cat": "DRINKS"},
    {"name": "Soda - Coca-Cola 500ml", "price": 70, "stock": 1000, "cat": "DRINKS"},
    {"name": "Water - Dasani 1L", "price": 50, "stock": 800, "cat": "DRINKS"},
    {"name": "Juice - Minute Maid 1L", "price": 220, "stock": 300, "cat": "DRINKS"},
    {"name": "Sufuria - 3pc Set", "price": 1850, "stock": 40, "cat": "UTENSILS"},
    {"name": "Plates - Melamine 6pc", "price": 950, "stock": 80, "cat": "UTENSILS"},
    {"name": "Cups - 6pc Set", "price": 650, "stock": 100, "cat": "UTENSILS"},
    {"name": "Gas Cooker - 2 Burner", "price": 4500, "stock": 15, "cat": "ELECTRONICS"},
    {"name": "Blender - Ramtons", "price": 3800, "stock": 25, "cat": "ELECTRONICS"},
    {"name": "Extension - 4 Socket", "price": 850, "stock": 120, "cat": "ELECTRONICS"},
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
    if os.path.exists("/mnt/data/wa_image_6489172589990200067"): return FileResponse("/mnt/data/wa_image_6489172589990200067")
    return Response(status_code=404)

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA ORBIT - SUPERCHAIN</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap" rel="stylesheet">
<style>
:root{--teal:#0096B0;--gold:#FFD700;--black:#070707;--card:#121212;--line:rgba(0,150,176,0.25)}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,sans-serif}
body{background:var(--black);color:#fff;display:flex;height:100vh}
.sidebar{width:300px;background:#000;border-right:1px solid var(--line);padding:16px;display:flex;flex-direction:column;overflow-y:auto}
.logo-box{background:var(--teal);border-radius:16px;padding:14px;text-align:center}
.logo-box img{width:100%;max-width:150px}
.main{flex:1;overflow-y:auto;padding:18px;background:radial-gradient(circle at 80% 10%,rgba(0,150,176,0.1),transparent 30%)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;margin-top:12px}
.cat-tabs{display:flex;gap:8px;margin:14px 0;flex-wrap:wrap}
.cat-tab{padding:10px 16px;border-radius:20px;border:1px solid #333;cursor:pointer;font-weight:700;font-size:12px;letter-spacing:1px;transition:0.2s}
.cat-tab.active{color:#000}
.products{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.prod{background:#161616;border:1px solid #222;border-radius:12px;padding:12px;cursor:pointer;position:relative;overflow:hidden}
.prod:hover{transform:translateY(-2px);border-color:var(--teal)}
.prod.cat-badge{font-size:9px;letter-spacing:1px;padding:3px 6px;border-radius:6px;color:#000;font-weight:800;position:absolute;top:8px;right:8px}
.price{color:var(--teal);font-weight:800;margin-top:6px}
.btn{background:var(--teal);color:#fff;border:none;padding:10px;border-radius:10px;font-weight:800;cursor:pointer;width:100%;margin-top:6px}
input,select{width:100%;background:#000;border:1px solid #333;padding:10px;border-radius:8px;color:#fff;margin:4px 0;font-size:13px}
.grid2{display:grid;grid-template-columns:2fr 1fr;gap:12px}
.branch div{padding:10px 12px;border:1px solid #222;border-radius:10px;margin-bottom:6px;cursor:pointer;font-size:13px}
.branch div.active{background:var(--teal);border-color:var(--teal);color:#fff;font-weight:800}
</style></head><body>
<div class="sidebar">
<div class="logo-box"><img src="/logo" alt="LONMA ORBIT"><div style="font-weight:800;letter-spacing:4px;font-size:11px;margin-top:8px">LONMA ORBIT</div></div>
<div style="margin-top:12px"><small style="color:var(--teal);font-weight:800;letter-spacing:2px">BRANCHES</small></div>
<div class="branch" id="branchList"></div>
<div class="card"><small style="color:var(--teal)">STOCK BY CATEGORY</small><div id="catStats" style="margin-top:8px"></div></div>
</div>

<div class="main">
<div style="display:flex;justify-content:space-between;align-items:center"><div><h2 id="curName">Loading</h2><small id="curLoc" style="color:#888"></small></div><div style="font-size:10px;color:#555" id="time"></div></div>

<div class="cat-tabs">
<div class="cat-tab active" style="background:#fff;color:#000" onclick="filterCat('ALL')" id="tab-ALL">ALL PRODUCTS</div>
<div class="cat-tab" style="background:#FF9800" onclick="filterCat('FOOD')" id="tab-FOOD">🍞 FOOD</div>
<div class="cat-tab" style="background:#0096B0;color:#fff" onclick="filterCat('DRINKS')" id="tab-DRINKS">🥤 DRINKS</div>
<div class="cat-tab" style="background:#9C27B0;color:#fff" onclick="filterCat('UTENSILS')" id="tab-UTENSILS">🍽️ UTENSILS</div>
<div class="cat-tab" style="background:#FFD700" onclick="filterCat('ELECTRONICS')" id="tab-ELECTRONICS">🔌 ELECTRONICS</div>
</div>

<div class="grid2">
<div>
<input id="search" placeholder="Search products..." onkeyup="renderProducts()">
<div class="products" id="plist" style="margin-top:10px"></div>
</div>
<div>
<div class="card"><b>🛒 CART</b><div id="cart" style="margin-top:8px;color:#777">Empty</div><hr style="margin:10px 0;border-color:#222"><div style="display:flex;justify-content:space-between"><b>Total</b><b id="total" style="color:var(--teal)">KES 0</b></div><button class="btn" onclick="checkout()">CHECKOUT</button><button class="btn" style="background:#000;color:var(--teal);border:1px solid var(--teal)" onclick="cart=[];renderCart()">Clear</button></div>

<div class="card"><b style="color:var(--teal)">+ ADD PRODUCT</b>
<input id="pName" placeholder="Name e.g TV 32 inch">
<select id="pCat"><option value="FOOD">FOOD</option><option value="DRINKS">DRINKS</option><option value="UTENSILS">UTENSILS</option><option value="ELECTRONICS">ELECTRONICS</option></select>
<input id="pPrice" type="number" placeholder="Price KES"><input id="pStock" type="number" placeholder="Stock Qty">
<button class="btn" style="background:var(--gold);color:#000" onclick="addProduct()">SAVE TO CATEGORY</button></div>

<div class="card"><b>Sales</b><div id="salesList" style="margin-top:8px;font-size:13px"></div></div>
</div>
</div>
</div>

<script>
let current='lonma-westlands'; let branches={}; let cart=[]; let activeCat='ALL';
async function loadBranches(){
  let r=await fetch('/api/supermarkets'); branches=await r.json();
  document.getElementById('branchList').innerHTML=Object.entries(branches).map(([id,b])=>`<div class="${id==current?'active':''}" onclick="selectBranch('${id}')"><b>${b.name}</b><br><small>${b.location}</small></div>`).join('');
  let b=branches[current]; document.getElementById('curName').innerText=b.name; document.getElementById('curLoc').innerText=b.location;
  let counts={}; b.products.forEach(p=>counts[p.cat]=(counts[p.cat]||0)+1);
  document.getElementById('catStats').innerHTML=Object.entries(counts).map(([c,n])=>`<div style="display:flex;justify-content:space-between;padding:4px 0"><span>${c}</span><b>${n}</b></div>`).join('');
  renderProducts(); loadSales();
}
function selectBranch(id){current=id; cart=[]; renderCart(); loadBranches();}
function filterCat(cat){
  activeCat=cat; document.querySelectorAll('.cat-tab').forEach(t=>t.classList.remove('active')); document.getElementById('tab-'+cat).classList.add('active');
  renderProducts();
}
async function renderProducts(){
  let b=branches[current]; if(!b) return; let q=document.getElementById('search').value.toLowerCase();
  let filtered=b.products.filter(p=>{
    let matchCat=activeCat=='ALL'||p.cat==activeCat;
    let matchSearch=p.name.toLowerCase().includes(q);
    return matchCat&&matchSearch;
  });
  let catColors={"FOOD":"#FF9800","DRINKS":"#0096B0","UTENSILS":"#9C27B0","ELECTRONICS":"#FFD700"};
  document.getElementById('plist').innerHTML=filtered.map(p=>`<div class="prod" onclick="addCart('${p.id}')"><div class="cat-badge" style="background:${catColors[p.cat]}">${p.cat}</div><div style="font-weight:700;margin-top:18px;font-size:13px">${p.name}</div><div class="price">KES ${p.price}</div><small style="color:${p.stock<10?'#f44':'#666'}">Stock ${p.stock}</small></div>`).join('');
}
function addCart(pid){let p=branches[current].products.find(x=>x.id==pid); let c=cart.find(x=>x.product_id==pid); if(c) c.qty++; else cart.push({product_id:pid,qty:1,name:p.name,price:p.price,cat:p.cat}); renderCart();}
function renderCart(){if(cart.length==0){document.getElementById('cart').innerHTML='Empty'; document.getElementById('total').innerText='KES 0'; return} let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #222"><span><small style="background:#222;padding:2px 5px;border-radius:4px;font-size:9px">${i.cat}</small> ${i.name} x${i.qty}</span><span style="color:var(--teal)">KES ${i.price*i.qty}</span></div>`}).join(''); document.getElementById('total').innerText='KES '+total.toLocaleString();}
async function checkout(){if(cart.length==0) return alert('Empty'); let r=await fetch(`/api/${current}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart)}); let d=await r.json(); alert('✅ '+d.receipt+' KES '+d.total+' @ '+branches[current].name); cart=[]; renderCart(); loadBranches();}
async function addProduct(){let body={name:document.getElementById('pName').value,price:parseFloat(document.getElementById('pPrice').value),stock:parseInt(document.getElementById('pStock').value),cat:document.getElementById('pCat').value}; if(!body.name) return alert('Name required'); await fetch(`/api/${current}/products`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); loadBranches();}
async function loadSales(){let r=await fetch(`/api/${current}/sales`); let sales=await r.json(); document.getElementById('salesList').innerHTML=sales.slice(0,8).map(s=>`<div style="padding:6px 0;border-bottom:1px solid #222;display:flex;justify-content:space-between"><span>${s.items.map(i=>i.name.substring(0,12)+' x'+i.qty).join(', ')}</span><b style="color:var(--teal)">KES ${s.total}</b></div>`).join('')||'No sales';}
setInterval(()=>{document.getElementById('time').innerText=new Date().toLocaleString()},1000); loadBranches();
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
