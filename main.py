from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI(title="KENYA SUPERCHAIN OS")

# KENYA'S TOP SUPERMARKETS + LONMA
SUPERMARKETS = {
    "lonma-westlands": {"name": "LONMA Westlands", "location": "Westlands Mall - HQ", "owner": "Marlone", "products": [], "sales": []},
    "naivas": {"name": "Naivas Supermarket", "location": "Multiple - 100+ Branches", "owner": "Naivas Family", "products": [], "sales": []},
    "carrefour": {"name": "Carrefour Kenya", "location": "Two Rivers, Junction, TRM", "owner": "Majid Al Futtaim", "products": [], "sales": []},
    "chandarana": {"name": "Chandarana FoodPlus", "location": "Lavington, Yaya, Diamond", "owner": "Chandarana Family", "products": [], "sales": []},
    "magunas": {"name": "Magunas Supermarket", "location": "Murang'a, Kenol, Makuyu", "owner": "Magunas", "products": [], "sales": []},
    "khetias": {"name": "Khetias Supermarket", "location": "Bungoma, Kitale, Eldoret", "owner": "Khetias Group", "products": [], "sales": []},
    "mathais": {"name": "Mathai's Supermarket", "location": "Nanyuki, Nyeri, Karatina", "owner": "Mathai's Group", "products": [], "sales": []},
}

seed = [
    {"id": "1", "name": "Milk - Brookside 500ml", "price": 65, "stock": 500, "cat": "Dairy"},
    {"id": "2", "name": "Bread - Festive 400g", "price": 60, "stock": 300, "cat": "Bakery"},
    {"id": "3", "name": "Sugar - Kabras 1kg", "price": 165, "stock": 800, "cat": "Groceries"},
    {"id": "4", "name": "Oil - Elianto 1L", "price": 320, "stock": 250, "cat": "Groceries"},
    {"id": "5", "name": "Rice - Pishori 2kg", "price": 380, "stock": 400, "cat": "Groceries"},
    {"id": "6", "name": "Flour - Ajab 2kg", "price": 180, "stock": 600, "cat": "Groceries"},
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

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>KENYA SUPERCHAIN OS | LONMA</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Cinzel:wght@600&display=swap" rel="stylesheet">
<style>
:root{--gold:#FFD700;--black:#070707;--card:#121212;--line:rgba(255,215,0,0.18)}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,sans-serif}
body{background:var(--black);color:#fff;display:flex;height:100vh}
.sidebar{width:310px;background:#000;border-right:1px solid var(--line);padding:18px;display:flex;flex-direction:column;overflow-y:auto}
.logo{font-family:Cinzel;font-weight:600;letter-spacing:3px;font-size:16px}.logo span{color:var(--gold)}
.branch{margin-top:15px}.branch div{padding:12px 14px;border:1px solid #222;border-radius:12px;margin-bottom:8px;cursor:pointer;transition:0.2s}
.branch div.active{background:linear-gradient(90deg,var(--gold),#B8860B);color:#000;font-weight:800;border-color:var(--gold)}
.branch div:hover{border-color:var(--gold)}
.main{flex:1;overflow-y:auto;padding:20px;background:radial-gradient(circle at 80% 20%,rgba(255,215,0,0.07),transparent 30%)}
.top{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:15px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;margin-top:14px}
.products{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}
.prod{background:#151515;border:1px solid #222;border-radius:12px;padding:13px;cursor:pointer;transition:0.2s}
.prod:hover{border-color:var(--gold);transform:translateY(-2px)}
.price{color:var(--gold);font-weight:800;margin-top:5px}
.btn{background:var(--gold);color:#000;border:none;padding:11px;border-radius:8px;font-weight:800;cursor:pointer;width:100%;margin-top:8px;letter-spacing:1px}
.btn-outline{background:#000;color:var(--gold);border:1px solid var(--gold)}
input{width:100%;background:#000;border:1px solid #333;padding:10px;border-radius:8px;color:#fff;margin:4px 0;font-size:13px}
.grid2{display:grid;grid-template-columns:2fr 1fr;gap:14px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px}
.stat{background:#000;border:1px solid var(--line);border-radius:10px;padding:12px;text-align:center}
.stat h2{color:var(--gold)}
</style></head><body>
<div class="sidebar">
<div class="logo">KENYA <span>SUPERCHAIN</span><div style="font-size:8px;color:#666;letter-spacing:3px;margin-top:4px">POWERED BY LONMA ORBIT</div></div>

<div style="margin-top:18px;display:flex;justify-content:space-between;align-items:center"><small style="color:var(--gold);letter-spacing:2px;font-weight:700">7 BRANCHES LIVE</small><small id="liveTime" style="color:#555">--:--</small></div>
<div class="branch" id="branchList"></div>

<div class="card" style="background:#0a0a0a">
<small style="color:var(--gold);letter-spacing:2px">+ ADD NEW SUPERMARKET</small>
<input id="smId" placeholder="id e.g quickmart"><input id="smName" placeholder="Name"><input id="smLoc" placeholder="Location">
<button class="btn" onclick="addMarket()">ADD TO CHAIN</button>
</div>
<div style="margin-top:auto;padding-top:15px;border-top:1px solid #222;font-size:10px;color:#555">● LIVE • app.lonmaorbit.co.ke<br>Chain OS by Marlone • 2026</div>
</div>

<div class="main">
<div class="top"><div><h2 id="curName" style="font-family:Cinzel">Loading...</h2><small id="curLoc" style="color:#888"></small></div><div class="badge" style="background:var(--gold);color:#000;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:800" id="branchCount">7 MARKETS</div></div>

<div class="stats"><div class="stat"><small>TOTAL STOCK VALUE</small><h2 id="stockValue">KES 0</h2></div><div class="stat"><small>TODAY SALES</small><h2 id="todaySales">KES 0</h2></div><div class="stat"><small>PRODUCTS</small><h2 id="prodCount">0</h2></div></div>

<div class="grid2">
<div>
<div style="display:flex;gap:8px;margin-top:14px"><input id="search" placeholder="Search Milk, Sugar, Bread..." onkeyup="renderProducts()" style="flex:1"></div>
<div class="products" id="plist" style="margin-top:12px"></div>
</div>
<div>
<div class="card"><div style="display:flex;justify-content:space-between"><b>🛒 CART</b><small id="cartBranch" style="color:var(--gold)"></small></div><div id="cart" style="margin-top:10px;color:#777">Empty - click product</div><hr style="margin:12px 0;border-color:#222"><div style="display:flex;justify-content:space-between"><b>Total</b><b id="total" style="color:var(--gold)">KES 0</b></div><button class="btn" onclick="checkout()">CHECKOUT • PRINT RECEIPT</button><button class="btn btn-outline" onclick="cart=[];renderCart()">Clear Cart</button></div>

<div class="card"><b style="color:var(--gold)">+ Add Product</b><input id="pName" placeholder="Product Name"><input id="pPrice" type="number" placeholder="Price KES"><input id="pStock" type="number" placeholder="Stock Qty"><input id="pCat" placeholder="Category"><button class="btn" onclick="addProduct()">SAVE TO <span id="saveTo"></span></button></div>
</div>
</div>

<div class="card"><div style="display:flex;justify-content:space-between"><b>Sales Feed - <span id="salesBranch"></span></b><button class="btn" style="width:auto;padding:6px 12px;font-size:11px" onclick="loadSales()">REFRESH</button></div><div id="salesList" style="margin-top:10px"></div></div>
</div>

<script>
let current='lonma-westlands'; let branches={}; let cart=[];
async function loadBranches(){
  let r=await fetch('/api/supermarkets'); branches=await r.json();
  let totalValue=0; Object.values(branches).forEach(b=>{ b.products.forEach(p=> totalValue+=p.price*p.stock )});
  document.getElementById('stockValue').innerText='KES '+totalValue.toLocaleString();
  document.getElementById('branchList').innerHTML=Object.entries(branches).map(([id,b])=>{
    let sv=b.products.reduce((s,p)=>s+p.price*p.stock,0);
    let icon=id=='naivas'?'🟢':id=='carrefour'?'🔵':id=='chandarana'?'🟡':id=='magunas'?'🟠':id=='khetias'?'🔴':id=='mathais'?'🟣':'⚫';
    return `<div class="${id==current?'active':''}" onclick="selectBranch('${id}')"><div style="display:flex;justify-content:space-between"><b>${icon} ${b.name}</b><small>${b.sales.length} sales</small></div><small style="opacity:0.7">${b.location}</small><br><small style="font-size:10px;opacity:0.6">Stock Value KES ${sv.toLocaleString()}</small></div>`;
  }).join('');
  let b=branches[current];
  document.getElementById('curName').innerText=b.name; document.getElementById('curLoc').innerText=b.location+' • Owner: '+b.owner;
  document.getElementById('saveTo').innerText=b.name.split(' ')[0]; document.getElementById('cartBranch').innerText=b.name; document.getElementById('salesBranch').innerText=b.name;
  document.getElementById('prodCount').innerText=b.products.length;
  renderProducts(); loadSales();
}
function selectBranch(id){current=id; cart=[]; renderCart(); loadBranches();}
async function renderProducts(){
  let b=branches[current]; if(!b) return;
  let q=document.getElementById('search').value.toLowerCase();
  let prods=b.products.filter(p=>p.name.toLowerCase().includes(q) || p.cat.toLowerCase().includes(q));
  document.getElementById('plist').innerHTML=prods.map(p=>`<div class="prod" onclick="addCart('${p.id}')"><div style="display:flex;justify-content:space-between"><small style="color:#666">${p.cat}</small><small style="color:${p.stock<20?'#ff4444':'#555'}">● ${p.stock}</small></div><div style="font-weight:700;margin-top:4px;font-size:14px">${p.name}</div><div class="price">KES ${p.price}</div></div>`).join('');
}
function addCart(pid){
  let p=branches[current].products.find(x=>x.id==pid);
  let c=cart.find(x=>x.product_id==pid); if(c) c.qty++; else cart.push({product_id:pid,qty:1,name:p.name,price:p.price}); renderCart();
}
function renderCart(){
  if(cart.length==0){document.getElementById('cart').innerHTML='Empty - click product'; document.getElementById('total').innerText='KES 0'; return}
  let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #222"><span>${i.name} x${i.qty}</span><span style="color:var(--gold)">KES ${i.price*i.qty}</span></div>`}).join('');
  document.getElementById('total').innerText='KES '+total.toLocaleString();
}
async function checkout(){
  if(cart.length==0) return alert('Cart empty');
  let r=await fetch(`/api/${current}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart)});
  let d=await r.json(); alert('✅ SALE SUCCESS\\nBranch: '+branches[current].name+'\\nReceipt: '+d.receipt+'\\nTotal: KES '+d.total+'\\n\\nThank you!');
  cart=[]; renderCart(); loadBranches();
}
async function addProduct(){
  let body={name:document.getElementById('pName').value,price:parseFloat(document.getElementById('pPrice').value),stock:parseInt(document.getElementById('pStock').value),cat:document.getElementById('pCat').value||'General'};
  if(!body.name) return alert('Name required');
  await fetch(`/api/${current}/products`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  document.getElementById('pName').value=''; loadBranches();
}
async function addMarket(){
  let body={id:document.getElementById('smId').value.toLowerCase().replace(/\\s/g,'-'),name:document.getElementById('smName').value,location:document.getElementById('smLoc').value};
  if(!body.id) return alert('ID required');
  await fetch('/api/supermarkets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); loadBranches();
}
async function loadSales(){
  let r=await fetch(`/api/${current}/sales`); let sales=await r.json();
  let tot=sales.reduce((s,x)=>s+x.total,0); document.getElementById('todaySales').innerText='KES '+tot.toLocaleString();
  document.getElementById('salesList').innerHTML=sales.slice(0,15).map(s=>`<div style="padding:10px 0;border-bottom:1px solid #222;display:flex;justify-content:space-between;align-items:center"><div><small style="color:#666">${new Date(s.time).toLocaleTimeString()} • ${s.receipt}</small><br>${s.items.map(i=>i.name+' x'+i.qty).join(', ')}</div><b style="color:var(--gold)">KES ${s.total}</b></div>`).join('')||'<small style="color:#555">No sales yet - make first sale!</small>';
}
setInterval(()=>{document.getElementById('liveTime').innerText=new Date().toLocaleTimeString()},1000);
loadBranches();
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
