from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List
import uuid, os
from datetime import datetime

app = FastAPI(title="LONMA ORBIT - SUPERCHAIN")

SUPERMARKETS = {
    "lonma-westlands": {"name": "LONMA Westlands", "location": "Westlands Mall - HQ", "owner": "Marlone", "products": [], "sales": []},
    "naivas": {"name": "Naivas Supermarket", "location": "100+ Branches Kenya", "owner": "Naivas", "products": [], "sales": []},
    "carrefour": {"name": "Carrefour Kenya", "location": "Two Rivers, Junction", "owner": "Majid Al Futtaim", "products": [], "sales": []},
    "chandarana": {"name": "Chandarana FoodPlus", "location": "Lavington, Yaya", "owner": "Chandarana", "products": [], "sales": []},
    "magunas": {"name": "Magunas Supermarket", "location": "Murang'a, Kenol", "owner": "Magunas", "products": [], "sales": []},
    "khetias": {"name": "Khetias Supermarket", "location": "Bungoma, Eldoret", "owner": "Khetias", "products": [], "sales": []},
    "mathais": {"name": "Mathai's Supermarket", "location": "Nanyuki, Nyeri", "owner": "Mathai's", "products": [], "sales": []},
}

seed = [
    {"id": "1", "name": "Milk - Brookside 500ml", "price": 65, "stock": 500, "cat": "Dairy"},
    {"id": "2", "name": "Bread - Festive 400g", "price": 60, "stock": 300, "cat": "Bakery"},
    {"id": "3", "name": "Sugar - Kabras 1kg", "price": 165, "stock": 800, "cat": "Groceries"},
    {"id": "4", "name": "Oil - Elianto 1L", "price": 320, "stock": 250, "cat": "Groceries"},
]
for sm in SUPERMARKETS.values():
    sm["products"] = [dict(p, id=str(uuid.uuid4())[:6]) for p in seed]

class Product(BaseModel):
    name: str; price: float; stock: int; cat: str = "General"
class SupermarketCreate(BaseModel):
    id: str; name: str; location: str
class CartItem(BaseModel):
    product_id: str; qty: int = 1

@app.head("/")
async def head_root(): return Response(status_code=200)

@app.get("/logo")
async def get_logo():
    if os.path.exists("logo.jpg"):
        return FileResponse("logo.jpg")
    return Response(status_code=404)

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA ORBIT | SUPERCHAIN</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap" rel="stylesheet">
<style>
:root{--teal:#0096B0;--gold:#FFD700;--black:#070707;--card:#111;--line:rgba(0,150,176,0.25)}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,sans-serif}
body{background:var(--black);color:#fff;display:flex;height:100vh}
.sidebar{width:310px;background:#000;border-right:1px solid var(--line);padding:18px;display:flex;flex-direction:column;overflow-y:auto}
.logo-box{background:var(--teal);border-radius:16px;padding:18px;text-align:center;margin-bottom:15px;box-shadow:0 8px 24px rgba(0,150,176,0.3)}
.logo-box img{width:100%;max-width:180px;filter:brightness(1.1)}
.brand-text{margin-top:12px;font-weight:800;letter-spacing:4px;font-size:12px;color:#fff}
.branch{margin-top:10px}.branch div{padding:11px 13px;border:1px solid #222;border-radius:12px;margin-bottom:8px;cursor:pointer}
.branch div.active{background:var(--teal);color:#fff;font-weight:800;border-color:var(--teal)}
.branch div:hover{border-color:var(--teal)}
.main{flex:1;overflow-y:auto;padding:20px;background:radial-gradient(circle at 80% 10%,rgba(0,150,176,0.12),transparent 30%)}
.top{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;margin-top:14px}
.products{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}
.prod{background:#151515;border:1px solid #222;border-radius:12px;padding:13px;cursor:pointer}
.prod:hover{border-color:var(--teal);transform:translateY(-2px)}
.price{color:var(--teal);font-weight:800;margin-top:5px}
.btn{background:var(--teal);color:#fff;border:none;padding:11px;border-radius:10px;font-weight:800;cursor:pointer;width:100%;margin-top:8px}
.btn-gold{background:var(--gold);color:#000}
input{width:100%;background:#000;border:1px solid #333;padding:10px;border-radius:8px;color:#fff;margin:4px 0;font-size:13px}
.grid2{display:grid;grid-template-columns:2fr 1fr;gap:14px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px}
.stat{background:#000;border:1px solid var(--line);border-radius:12px;padding:12px;text-align:center}
.stat h2{color:var(--teal)}
</style></head><body>
<div class="sidebar">
<div class="logo-box">
<img src="/logo" onerror="this.style.display='none';document.getElementById('fallback').style.display='block'" alt="LONMA ORBIT">
<div id="fallback" style="display:none;font-size:28px;font-weight:800;letter-spacing:4px">L<span style="color:#000">O</span> LONMA ORBIT</div>
<div class="brand-text">LONMA ORBIT</div>
<div style="font-size:8px;letter-spacing:3px;opacity:0.8;margin-top:4px">SUPERCHAIN OS • EST 2026</div>
</div>

<div style="display:flex;justify-content:space-between"><small style="color:var(--teal);letter-spacing:2px;font-weight:700">7 BRANCHES</small><small id="liveTime" style="color:#555"></small></div>
<div class="branch" id="branchList"></div>

<div class="card"><small style="color:var(--teal)">+ ADD MARKET</small><input id="smId" placeholder="id"><input id="smName" placeholder="Name"><input id="smLoc" placeholder="Location"><button class="btn" onclick="addMarket()">ADD</button></div>
<div style="margin-top:auto;font-size:10px;color:#555;padding-top:12px">● LIVE • app.lonmaorbit.co.ke<br>Logo © LONMA ORBIT</div>
</div>

<div class="main">
<div class="top"><div><h2 id="curName">Loading...</h2><small id="curLoc" style="color:#888"></small></div><div style="background:var(--teal);color:#fff;padding:6px 14px;border-radius:20px;font-size:11px;font-weight:800">LONMA ORBIT BRANDED</div></div>
<div class="stats"><div class="stat"><small>STOCK VALUE</small><h2 id="stockValue">0</h2></div><div class="stat"><small>TODAY SALES</small><h2 id="todaySales">0</h2></div><div class="stat"><small>PRODUCTS</small><h2 id="prodCount">0</h2></div></div>
<div class="grid2"><div><input id="search" placeholder="Search..." onkeyup="renderProducts()"><div class="products" id="plist" style="margin-top:12px"></div></div>
<div><div class="card"><b>🛒 CART - <span id="cartBranch"></span></b><div id="cart" style="margin-top:10px;color:#777">Empty</div><hr style="margin:12px 0;border-color:#222"><div style="display:flex;justify-content:space-between"><b>Total</b><b id="total" style="color:var(--teal)">KES 0</b></div><button class="btn" onclick="checkout()">CHECKOUT</button><button class="btn" style="background:#000;color:var(--teal);border:1px solid var(--teal)" onclick="cart=[];renderCart()">Clear</button></div>
<div class="card"><b style="color:var(--teal)">+ Product</b><input id="pName" placeholder="Name"><input id="pPrice" type="number" placeholder="Price"><input id="pStock" type="number" placeholder="Stock"><input id="pCat" placeholder="Category"><button class="btn btn-gold" onclick="addProduct()">SAVE</button></div></div></div>
<div class="card"><b>Sales Feed</b><div id="salesList" style="margin-top:10px"></div></div>
</div>
<script>
let current='lonma-westlands'; let branches={}; let cart=[];
async function loadBranches(){
  let r=await fetch('/api/supermarkets'); branches=await r.json();
  let totalValue=0; Object.values(branches).forEach(b=>{ b.products.forEach(p=> totalValue+=p.price*p.stock )});
  document.getElementById('stockValue').innerText='KES '+totalValue.toLocaleString();
  document.getElementById('branchList').innerHTML=Object.entries(branches).map(([id,b])=>{
    let icon=id=='naivas'?'🟢':id=='carrefour'?'🔵':id=='chandarana'?'🟡':id=='magunas'?'🟠':id=='khetias'?'🔴':id=='mathais'?'🟣':'⚫';
    return `<div class="${id==current?'active':''}" onclick="selectBranch('${id}')"><div style="display:flex;justify-content:space-between"><b>${icon} ${b.name}</b><small>${b.sales.length}</small></div><small style="opacity:0.7">${b.location}</small></div>`;
  }).join('');
  let b=branches[current]; document.getElementById('curName').innerText=b.name; document.getElementById('curLoc').innerText=b.location; document.getElementById('cartBranch').innerText=b.name.split(' ')[0]; document.getElementById('prodCount').innerText=b.products.length; renderProducts(); loadSales();
}
function selectBranch(id){current=id; cart=[]; renderCart(); loadBranches();}
async function renderProducts(){
  let b=branches[current]; if(!b) return; let q=document.getElementById('search').value.toLowerCase();
  let prods=b.products.filter(p=>p.name.toLowerCase().includes(q));
  document.getElementById('plist').innerHTML=prods.map(p=>`<div class="prod" onclick="addCart('${p.id}')"><small style="color:#666">${p.cat}</small><div style="font-weight:700;margin-top:4px">${p.name}</div><div class="price">KES ${p.price}</div><small>Stock ${p.stock}</small></div>`).join('');
}
function addCart(pid){let p=branches[current].products.find(x=>x.id==pid); let c=cart.find(x=>x.product_id==pid); if(c) c.qty++; else cart.push({product_id:pid,qty:1,name:p.name,price:p.price}); renderCart();}
function renderCart(){if(cart.length==0){document.getElementById('cart').innerHTML='Empty'; document.getElementById('total').innerText='KES 0'; return} let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #222"><span>${i.name} x${i.qty}</span><span style="color:var(--teal)">KES ${i.price*i.qty}</span></div>`}).join(''); document.getElementById('total').innerText='KES '+total.toLocaleString();}
async function checkout(){if(cart.length==0) return alert('Empty'); let r=await fetch(`/api/${current}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart)}); let d=await r.json(); alert('✅ SALE '+d.receipt+' KES '+d.total+' @ '+branches[current].name); cart=[]; renderCart(); loadBranches();}
async function addProduct(){let body={name:document.getElementById('pName').value,price:parseFloat(document.getElementById('pPrice').value),stock:parseInt(document.getElementById('pStock').value),cat:document.getElementById('pCat').value||'General'}; await fetch(`/api/${current}/products`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); loadBranches();}
async function addMarket(){let body={id:document.getElementById('smId').value.toLowerCase().replace(/\\s/g,'-'),name:document.getElementById('smName').value,location:document.getElementById('smLoc').value}; await fetch('/api/supermarkets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); loadBranches();}
async function loadSales(){let r=await fetch(`/api/${current}/sales`); let sales=await r.json(); let tot=sales.reduce((s,x)=>s+x.total,0); document.getElementById('todaySales').innerText='KES '+tot.toLocaleString(); document.getElementById('salesList').innerHTML=sales.slice(0,10).map(s=>`<div style="padding:8px 0;border-bottom:1px solid #222;display:flex;justify-content:space-between"><span>${s.items.map(i=>i.name+' x'+i.qty).join(', ')}</span><b style="color:var(--teal)">KES ${s.total}</b></div>`).join('')||'No sales';}
setInterval(()=>{document.getElementById('liveTime').innerText=new Date().toLocaleTimeString()},1000); loadBranches();
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
    new_p = {"id": str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat}
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
