from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI()
USERS = {
    "admin": {"password": "Lonma@2026", "role": "Owner", "name": "Marlone - Owner", "branch": "all", "signature": "signed", "created": "2026-10-03"},
    "cashier1": {"password": "1234", "role": "Cashier", "name": "Marlon - Cashier", "branch": "lonma-westlands", "signature": "signed", "created": "2026-10-06"},
}
SUPERMARKETS = {
    "lonma-westlands": {"name": "LONMA Westlands", "icon": "🏬", "location": "Westlands HQ", "products": [], "sales": []},
    "naivas": {"name": "Naivas", "icon": "🛒", "location": "100+ Branches", "products": [], "sales": []},
    "carrefour": {"name": "Carrefour", "icon": "🌍", "location": "Two Rivers", "products": [], "sales": []},
    "chandarana": {"name": "Chandarana", "icon": "🍏", "location": "Lavington", "products": [], "sales": []},
    "magunas": {"name": "Magunas", "icon": "🏪", "location": "Murang'a", "products": [], "sales": []},
    "khetias": {"name": "Khetias", "icon": "🏪", "location": "Western", "products": [], "sales": []},
    "mathais": {"name": "Mathai's", "icon": "🌄", "location": "Mt Kenya", "products": [], "sales": []},
}
seed = [
    {"name": "Bread - Festive 400g", "price": 60, "stock": 300, "cat": "FOOD", "emoji": "🍞"},
    {"name": "Sugar - Kabras 1kg", "price": 165, "stock": 800, "cat": "FOOD", "emoji": "🧂"},
    {"name": "Milk - Brookside 500ml", "price": 65, "stock": 500, "cat": "DRINKS", "emoji": "🥛"},
    {"name": "Soda - Coca 500ml", "price": 70, "stock": 1000, "cat": "DRINKS", "emoji": "🥤"},
    {"name": "Sufuria - 3pc Set", "price": 1850, "stock": 40, "cat": "UTENSILS", "emoji": "🍳"},
    {"name": "Gas Cooker - 2 Burner", "price": 4500, "stock": 15, "cat": "ELECTRONICS", "emoji": "🔥"},
]
for sm in SUPERMARKETS.values():
    sm["products"] = [dict(p, id=str(uuid.uuid4())[:6]) for p in seed]
    sm["sales"] = [{"receipt": "LON-A1B2C3", "total": 165, "items": [{"name": "Sugar - Kabras 1kg", "qty": 1}], "time": datetime.now().isoformat(), "cashier": "Marlon"}]

class Login(BaseModel):
    username: str; password: str
class Product(BaseModel):
    name: str; price: float; stock: int; cat: str

@app.head("/")
async def head_root(): return Response(status_code=200)

@app.post("/api/login")
async def login(l: Login):
    from fastapi import HTTPException
    u = USERS.get(l.username.lower())
    if not u or u["password"]!= l.password: raise HTTPException(status_code=401, detail="Wrong")
    return {"username": l.username, "role": u["role"], "name": u["name"], "branch": u["branch"]}

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>LONMA ORBIT PRO</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,system-ui} body{background:#0a0a0a;color:#fff;padding-bottom:90px}
.header{position:sticky;top:0;z-index:100;background:#000000ee;backdrop-filter:blur(12px);border-bottom:2px solid #0096B0;padding:12px 14px;display:flex;align-items:center;gap:10px}
.logo{width:48px;height:48px;background:linear-gradient(135deg,#0096B0,#00d4ff);border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:20px;color:#fff;box-shadow:0 4px 12px rgba(0,150,176,0.4)}
.card{background:#161616;border:1px solid #262626;border-radius:16px;padding:14px;margin:10px 12px}
.pill{white-space:nowrap;padding:10px 16px;border-radius:24px;border:1.5px solid #333;background:#1e1e1e;font-size:13px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:6px}
.pill.active{background:#0096B0;border-color:#0096B0;color:#fff;box-shadow:0 4px 12px rgba(0,150,176,0.3)}
.branch-scroll{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;scrollbar-width:none}
.branch-scroll::-webkit-scrollbar{display:none}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 12px}
.stat{background:#161616;border:1px solid #262626;border-radius:14px;padding:12px;text-align:center}
.stat small{color:#777;font-size:10px;letter-spacing:1px;font-weight:800}
.stat b{font-size:14px;display:block;margin-top:4px}
.cat{white-space:nowrap;padding:9px 14px;border-radius:24px;font-size:12px;font-weight:800;cursor:pointer;border:1.5px solid transparent;transition:0.2s}
.cat.active{transform:scale(1.05);box-shadow:0 4px 10px rgba(0,0,0,0.5)}
.products{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.prod{background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:12px;position:relative;transition:0.2s}
.prod:active{transform:scale(0.97);border-color:#0096B0}
.prod.stock-badge{position:absolute;top:8px;right:8px;font-size:9px;background:#000;padding:3px 6px;border-radius:10px;color:#888}
.prod.emoji{font-size:26px;margin:4px 0}
.btn{background:#0096B0;color:#fff;border:none;padding:14px;border-radius:14px;font-weight:900;width:100%;cursor:pointer;font-size:14px;letter-spacing:0.5px}
.btn:active{transform:scale(0.98)}
.fab{position:fixed;bottom:20px;right:16px;width:56px;height:56px;background:#FFD700;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:900;color:#000;box-shadow:0 8px 20px rgba(255,215,0,0.4);z-index:99;cursor:pointer}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#000;border-top:1px solid #222;display:flex;justify-content:space-around;padding:8px 0 20px;z-index:90}
.bottom-nav div{font-size:10px;color:#666;text-align:center;cursor:pointer;padding:6px 12px;border-radius:10px}
.bottom-nav div.active{color:#0096B0;background:#0096B01a}
.modal{position:fixed;inset:0;background:#000000ee;display:none;align-items:flex-end;justify-content:center;z-index:200}
.modal-box{background:#161616;border-radius:20px 20px 0 0;width:100%;max-width:500px;padding:20px;max-height:85vh;overflow-y:auto;border-top:2px solid #0096B0}
input,select{width:100%;background:#0a0a0a;border:1.5px solid #333;padding:13px;border-radius:12px;color:#fff;margin:6px 0;font-size:14px}
input:focus{border-color:#0096B0;outline:none}
</style></head><body>

<div class="header">
<div class="logo">LO</div>
<div style="flex:1"><div id="bName" style="font-weight:900;letter-spacing:1px;font-size:14px">LONMA Westlands</div><div id="uInfo" style="color:#0096B0;font-size:11px">Marlon • Cashier • ✍️ Signed</div></div>
<button onclick="showUsers()" style="background:#111;border:1px solid #333;color:#ccc;padding:8px 14px;border-radius:20px;font-size:11px;font-weight:700">Users</button>
<button onclick="location.reload()" style="background:#111;border:1px solid #333;color:#666;padding:8px 12px;border-radius:20px;font-size:11px;margin-left:6px">Logout</button>
</div>

<!-- FIX 1: All 7 branches scrollable with icons -->
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center"><small style="color:#0096B0;font-weight:900;font-size:10px;letter-spacing:1.5px">BRANCHES - SCROLL →</small><small style="color:#666;font-size:10px" id="branchCount">7/7 Online</small></div>
<div class="branch-scroll" id="branchList" style="margin-top:10px"></div>
</div>

<!-- FIX 2: Stats with better design -->
<div class="stats">
<div class="stat"><small>STOCK VALUE</small><b id="stockV" style="color:#0096B0">KES 0</b></div>
<div class="stat"><small>TODAY SALES</small><b id="salesV" style="color:#FFD700">KES 0</b><small id="salesCount" style="color:#888">0 sales</small></div>
<div class="stat"><small>ITEMS</small><b id="itemsV">0</b><small id="lowStock" style="color:#ff4444"></small></div>
</div>

<!-- FIX 3: Categories + Search improved -->
<div class="card">
<small style="color:#0096B0;font-weight:900;font-size:10px;letter-spacing:1.5px">CATEGORIES - FILTER</small>
<div style="display:flex;gap:7px;overflow-x:auto;margin:10px 0;scrollbar-width:none" id="catTabs">
<div class="cat active" style="background:#fff;color:#000" onclick="filterCat('ALL',this)">ALL</div>
<div class="cat" style="background:#FF9800;color:#000" onclick="filterCat('FOOD',this)">🍞 FOOD</div>
<div class="cat" style="background:#0096B0;color:#fff" onclick="filterCat('DRINKS',this)">🥤 DRINKS</div>
<div class="cat" style="background:#9C27B0;color:#fff" onclick="filterCat('UTENSILS',this)">🍳 UTENSILS</div>
<div class="cat" style="background:#FFD700;color:#000" onclick="filterCat('ELECTRONICS',this)">🔌 ELECTRONICS</div>
</div>
<div style="position:relative"><input id="search" placeholder="🔍 Search product, SKU..." onkeyup="renderProducts()" style="padding-left:16px"><span style="position:absolute;right:14px;top:50%;transform:translateY(-50%);color:#666;font-size:12px" id="resultCount"></span></div>
<div class="products" id="plist" style="margin-top:12px"></div>
</div>

<!-- FIX 4: Cart with qty controls + receipt -->
<div class="card" style="border:1.5px solid rgba(0,150,176,0.3)">
<div style="display:flex;justify-content:space-between;align-items:center"><b>🛒 CART - <span id="cartBranch" style="color:#0096B0">LONMA</span></b><button onclick="clearCart()" style="background:none;border:none;color:#666;font-size:11px">Clear</button></div>
<div id="cart" style="margin:10px 0;color:#666;font-size:13px">Cart empty - Tap products above</div>
<div style="border-top:1px dashed #333;margin:12px 0"></div>
<div style="display:flex;justify-content:space-between"><span style="color:#888">Subtotal</span><span id="subtotal">KES 0</span></div>
<div style="display:flex;justify-content:space-between;margin:4px 0"><span style="color:#888">VAT (16%)</span><span id="vat" style="color:#888">KES 0</span></div>
<div style="display:flex;justify-content:space-between;margin-top:8px;font-size:18px"><b>TOTAL</b><b id="total" style="color:#0096B0">KES 0</b></div>
<button class="btn" onclick="checkout()" style="margin-top:12px;font-size:15px">💳 CHECKOUT - M-Pesa + Receipt<br><small style="font-size:11px;opacity:0.8">Signed by Marlon • Legal</small></button>
<button class="btn" onclick="showSales()" style="background:#111;border:1px solid #333;color:#aaa;margin-top:8px;padding:10px">📊 View Today's Sales</button>
</div>

<div class="card" id="usersBox" style="display:none"><b>👥 CREATED USERS</b><div id="usersList" style="margin-top:10px"></div></div>

<!-- FAB Add Product -->
<div class="fab" onclick="openAddModal()">+</div>

<!-- Bottom Nav - FIX 6: Safe area -->
<div class="bottom-nav">
<div class="active">🏠<br>Home</div><div onclick="openAddModal()">➕<br>Add</div><div onclick="document.getElementById('cart').scrollIntoView({behavior:'smooth'})">🛒<br>Cart (<span id="cartCount">0</span>)</div><div onclick="showSales()">📊<br>Sales</div><div onclick="showUsers()">👥<br>Users</div>
</div>

<!-- Add Product Modal -->
<div class="modal" id="addModal" onclick="if(event.target==this)closeAddModal()"><div class="modal-box">
<h3>➕ ADD NEW PRODUCT - <span id="modalBranch">LONMA Westlands</span></h3>
<small style="color:#888">Add to current branch - instant sync</small>
<input id="p-name" placeholder="Product Name - e.g., Bread - Festive 400g">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px"><input id="p-price" type="number" placeholder="Price KES"><input id="p-stock" type="number" placeholder="Stock Qty"></div>
<select id="p-cat"><option value="FOOD">🍞 FOOD</option><option value="DRINKS">🥤 DRINKS</option><option value="UTENSILS">🍳 UTENSILS</option><option value="ELECTRONICS">🔌 ELECTRONICS</option></select>
<input id="p-emoji" placeholder="Emoji - e.g., 🍞 🥛 🍳 (optional)">
<button class="btn" style="background:#FFD700;color:#000;margin-top:10px" onclick="addProduct()">SAVE PRODUCT - Add to Branch</button>
<button class="btn" style="background:#111;color:#888;margin-top:8px" onclick="closeAddModal()">Cancel</button>
</div></div>

<!-- Sales Modal -->
<div class="modal" id="salesModal" onclick="if(event.target==this)closeSales()"><div class="modal-box">
<h3>📊 TODAY'S SALES - <span id="salesBranch">LONMA</span></h3><div id="salesList" style="margin-top:12px"></div>
<button class="btn" style="background:#111;color:#888;margin-top:12px" onclick="closeSales()">Close</button>
</div></div>

<!-- Receipt Modal -->
<div class="modal" id="receiptModal"><div class="modal-box" style="text-align:center">
<div style="width:60px;height:60px;background:#0096B0;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:30px">✅</div>
<h2>Sale Complete!</h2><div id="receiptContent" style="background:#000;border-radius:12px;padding:14px;margin:14px 0;text-align:left;font-family:monospace;font-size:12px"></div>
<button class="btn" onclick="closeReceipt()">New Sale</button>
</div></div>

<script>
let current='lonma-westlands'; let branches={}; let cart=[]; let activeCat='ALL';
async function loadBranches(){
  let r=await fetch('/api/supermarkets'); branches=await r.json();
  let list=Object.entries(branches);
  document.getElementById('branchList').innerHTML=list.map(([id,b])=>`<div class="pill ${id==current?'active':''}" onclick="selectBranch('${id}')">${b.icon} ${b.name}</div>`).join('');
  let b=branches[current]; document.getElementById('bName').innerText=b.name; document.getElementById('cartBranch').innerText=b.name; document.getElementById('modalBranch').innerText=b.name; document.getElementById('salesBranch').innerText=b.name; document.getElementById('itemsV').innerText=b.products.length;
  let tot=0; b.products.forEach(p=>tot+=p.price*p.stock); document.getElementById('stockV').innerText='KES '+tot.toLocaleString();
  let low=b.products.filter(p=>p.stock<20).length; document.getElementById('lowStock').innerText=low?`⚠️ ${low} low stock`:'';
  renderProducts(); loadSales();
}
function selectBranch(id){current=id; loadBranches();}
function filterCat(c,el){activeCat=c; document.querySelectorAll('.cat').forEach(x=>x.classList.remove('active')); el.classList.add('active'); renderProducts();}
function renderProducts(){
  let b=branches[current]; let q=document.getElementById('search').value.toLowerCase();
  let list=b.products.filter(p=>(activeCat=='ALL'||p.cat==activeCat)&&p.name.toLowerCase().includes(q));
  document.getElementById('resultCount').innerText=list.length+' items';
  let col={"FOOD":"#FF9800","DRINKS":"#0096B0","UTENSILS":"#9C27B0","ELECTRONICS":"#FFD700"};
  document.getElementById('plist').innerHTML=list.map(p=>`
    <div class="prod" onclick="addCart('${p.id}')">
      <div class="stock-badge" style="color:${p.stock<20?'#ff4444':'#888'}">${p.stock} left</div>
      <div class="emoji">${p.emoji||'📦'}</div>
      <small style="background:${col[p.cat]};color:#000;padding:3px 7px;border-radius:6px;font-size:9px;font-weight:900">${p.cat}</small>
      <div style="font-weight:700;margin:6px 0 2px;font-size:12px;line-height:1.2">${p.name}</div>
      <div style="color:#0096B0;font-weight:900">KES ${p.price}</div>
      <div style="margin-top:8px;background:#0096B0;color:#fff;text-align:center;padding:6px;border-radius:8px;font-size:11px;font-weight:800">+ ADD</div>
    </div>`).join('') || `<div style="grid-column:span 2;text-align:center;padding:20px;color:#666">No products found<br><small>Try ALL category or clear search</small></div>`;
}
function addCart(pid){
  let p=branches[current].products.find(x=>x.id==pid); let c=cart.find(x=>x.product_id==pid);
  if(p.stock<=0) return alert('Out of stock!');
  if(c){ if(c.qty>=p.stock) return alert('Max stock reached'); c.qty++; } else cart.push({product_id:pid,qty:1,name:p.name,price:p.price,emoji:p.emoji||'📦'});
  renderCart();
}
function renderCart(){
  document.getElementById('cartCount').innerText=cart.reduce((a,b)=>a+b.qty,0);
  if(cart.length==0){document.getElementById('cart').innerHTML='<div style=\"text-align:center;padding:12px;color:#555\">Cart empty<br><small>Tap products above to add</small></div>'; document.getElementById('total').innerText='KES 0'; document.getElementById('subtotal').innerText='KES 0'; document.getElementById('vat').innerText='KES 0'; return}
  let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{
    total+=i.price*i.qty;
    return `<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #222">
      <div style="display:flex;align-items:center;gap:8px"><span>${i.emoji}</span><div><div style="font-weight:700;font-size:13px">${i.name}</div><div style="color:#888;font-size:11px">KES ${i.price} each</div></div></div>
      <div style="display:flex;align-items:center;gap:8px"><button onclick="changeQty('${i.product_id}',-1)" style="width:28px;height:28px;border-radius:50%;border:1px solid #333;background:#111;color:#fff">-</button><b style="min-width:20px;text-align:center">${i.qty}</b><button onclick="changeQty('${i.product_id}',1)" style="width:28px;height:28px;border-radius:50%;background:#0096B0;border:none;color:#fff">+</button><span style="color:#0096B0;font-weight:800;min-width:60px;text-align:right">KES ${i.price*i.qty}</span></div>
    </div>`}).join('');
  let vat=Math.round(total*0.16); let sub=total-vat;
  document.getElementById('subtotal').innerText='KES '+sub.toLocaleString(); document.getElementById('vat').innerText='KES '+vat.toLocaleString(); document.getElementById('total').innerText='KES '+total.toLocaleString();
}
function changeQty(pid,d){let c=cart.find(x=>x.product_id==pid); if(!c) return; let p=branches[current].products.find(x=>x.id==pid); c.qty+=d; if(c.qty<=0) cart=cart.filter(x=>x.product_id!=pid); if(c.qty>p.stock) c.qty=p.stock; renderCart();}
function clearCart(){cart=[]; renderCart();}
async function checkout(){
  if(cart.length==0) return alert('Cart empty');
  let r=await fetch(`/api/${current}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart.map(c=>({product_id:c.product_id,qty:c.qty})))});
  let d=await r.json();
  document.getElementById('receiptContent').innerHTML=`<div style="text-align:center"><b>LONMA ORBIT</b><br>${branches[current].name}<br><small>${new Date().toLocaleString()}</small></div><hr style="border:1px dashed #333;margin:10px 0">Receipt: <b>${d.receipt}</b><br>Cashier: Marlon (Signed ✍️)<br><br>${d.items.map(i=>`${i.name} x${i.qty}`).join('<br>')}<br><br><div style="display:flex;justify-content:space-between"><b>TOTAL</b><b>KES ${d.total}</b></div><hr style="border:1px dashed #333;margin:10px 0"><small style="color:#888">Thank you! VAT inclusive. M-Pesa confirmed.</small>`;
  document.getElementById('receiptModal').style.display='flex'; cart=[]; renderCart(); loadBranches();
}
function closeReceipt(){document.getElementById('receiptModal').style.display='none';}
function openAddModal(){document.getElementById('addModal').style.display='flex';}
function closeAddModal(){document.getElementById('addModal').style.display='none';}
async function addProduct(){
  let name=document.getElementById('p-name').value; let price=parseFloat(document.getElementById('p-price').value); let stock=parseInt(document.getElementById('p-stock').value); let cat=document.getElementById('p-cat').value; let emoji=document.getElementById('p-emoji').value||'📦';
  if(!name||!price||!stock) return alert('Fill all fields');
  let r=await fetch(`/api/${current}/products`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,price,stock,cat})});
  let p=await r.json(); p.emoji=emoji; let idx=branches[current].products.findIndex(x=>x.id==p.id); if(idx>=0) branches[current].products[idx].emoji=emoji;
  closeAddModal(); document.getElementById('p-name').value=''; document.getElementById('p-price').value=''; document.getElementById('p-stock').value=''; loadBranches(); alert('✅ Added: '+name);
}
async function loadSales(){let r=await fetch(`/api/${current}/sales`); let s=await r.json(); let tot=s.reduce((a,b)=>a+b.total,0); document.getElementById('salesV').innerText='KES '+tot.toLocaleString(); document.getElementById('salesCount').innerText=s.length+' sales';}
async function showSales(){await loadSales(); let r=await fetch(`/api/${current}/sales`); let s=await r.json(); document.getElementById('salesList').innerHTML=s.slice(0,20).map(x=>`<div style="padding:10px 0;border-bottom:1px solid #222"><div style="display:flex;justify-content:space-between"><b>${x.receipt}</b><b style="color:#0096B0">KES ${x.total}</b></div><small style="color:#888">${x.items.map(i=>i.name+' x'+i.qty).join(', ')} • ${new Date(x.time).toLocaleTimeString()}</small></div>`).join('')||'No sales yet'; document.getElementById('salesModal').style.display='flex';}
function closeSales(){document.getElementById('salesModal').style.display='none';}
async function showUsers(){let box=document.getElementById('usersBox'); box.style.display=box.style.display=='none'?'block':'none'; let r=await fetch('/api/users'); let u=await r.json(); document.getElementById('usersList').innerHTML=u.map(x=>`<div style="padding:8px 0;border-bottom:1px solid #222;display:flex;justify-content:space-between"><span><b>${x.name}</b><br><small style="color:#888">${x.role} • ${x.branch} • ${x.hasSignature?'✍️ Signed':''}</small></span><small>${x.created?.substring(0,10)}</small></div>`).join(''); if(box.style.display=='block') box.scrollIntoView({behavior:'smooth'});}
loadBranches();
</script></body></html>
    """

@app.get("/api/supermarkets")
async def get_markets(): return SUPERMARKETS
@app.get("/api/users")
async def list_users(): return [{"username": k, "name": v["name"], "role": v["role"], "branch": v["branch"], "created": v.get("created",""), "hasSignature": bool(v.get("signature"))} for k,v in USERS.items()]
@app.get("/api/{branch_id}/sales")
async def branch_sales(branch_id: str): return SUPERMARKETS.get(branch_id, {}).get("sales", [])[::-1]
@app.post("/api/{branch_id}/products")
async def add_prod(branch_id: str, p: Product):
    new_p = {"id": str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat.upper(), "emoji": "📦"}
    SUPERMARKETS[branch_id]["products"].append(new_p); return new_p
@app.post("/api/{branch_id}/checkout")
async def checkout(branch_id: str, cart: List[dict]):
    sm = SUPERMARKETS[branch_id]; total=0; items=[]
    for ci in cart:
        prod = next((x for x in sm["products"] if x["id"]==ci["product_id"]), None)
        if prod and prod["stock"]>=ci["qty"]:
            prod["stock"]-=ci["qty"]; total+=prod["price"]*ci["qty"]; items.append({"name":prod["name"],"qty":ci["qty"]})
    sale={"receipt":f"{branch_id[:3].upper()}-{uuid.uuid4().hex[:6].upper()}","items":items,"total":total,"time":datetime.now().isoformat(),"cashier":"Marlon"}
    sm["sales"].append(sale); return sale
