from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI() # <-- MUST BE FIRST

# USERS WITH SIGNING
USERS = {
    "admin": {"password": "Lonma@2026", "role": "Owner", "name": "Marlone - Owner", "branch": "all", "signature": "signed", "created": "2026-10-03"},
    "cashier1": {"password": "1234", "role": "Cashier", "name": "Marlon - Cashier", "branch": "lonma-westlands", "signature": "signed", "created": "2026-10-06"},
}

# 7 BRANCHES WITH ICONS
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
    sm["sales"] = []

class Login(BaseModel):
    username: str; password: str
class Signup(BaseModel):
    username: str; password: str; name: str; role: str; branch: str; signature: str = ""
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

@app.post("/api/signup")
async def signup(s: Signup):
    from fastapi import HTTPException
    if s.username.lower() in USERS: raise HTTPException(status_code=400, detail="Username exists")
    USERS[s.username.lower()] = {"password": s.password, "role": s.role, "name": s.name, "branch": s.branch, "signature": s.signature, "created": datetime.now().isoformat()}
    return {"ok": True}

@app.get("/api/users")
async def list_users():
    return [{"username": k, "name": v["name"], "role": v["role"], "branch": v["branch"], "created": v.get("created",""), "hasSignature": bool(v.get("signature"))} for k,v in USERS.items()]

@app.get("/api/supermarkets")
async def get_markets(): return SUPERMARKETS

@app.get("/api/{branch_id}/sales")
async def branch_sales(branch_id: str): return SUPERMARKETS.get(branch_id, {}).get("sales", [])[::-1]

@app.post("/api/{branch_id}/products")
async def add_prod(branch_id: str, p: Product):
    new_p = {"id": str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat.upper(), "emoji": "📦"}
    SUPERMARKETS[branch_id]["products"].append(new_p); return new_p

@app.post("/api/{branch_id}/products/bulk")
async def bulk_add(branch_id: str, products: List[Product]):
    added=[]
    for p in products:
        new_p = {"id": str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat.upper(), "emoji": "📦"}
        SUPERMARKETS[branch_id]["products"].append(new_p); added.append(new_p)
    return {"added": len(added), "products": added}

@app.post("/api/{branch_id}/checkout")
async def checkout(branch_id: str, cart: List[dict]):
    sm = SUPERMARKETS[branch_id]; total=0; items=[]
    for ci in cart:
        prod = next((x for x in sm["products"] if x["id"]==ci["product_id"]), None)
        if prod and prod["stock"]>=ci["qty"]:
            prod["stock"]-=ci["qty"]; total+=prod["price"]*ci["qty"]; items.append({"name":prod["name"],"qty":ci["qty"]})
    sale={"receipt":f"{branch_id[:3].upper()}-{uuid.uuid4().hex[:6].upper()}","items":items,"total":total,"time":datetime.now().isoformat(),"cashier":"Marlon"}
    sm["sales"].append(sale); return sale

@app.get("/terms", response_class=HTMLResponse)
async def terms_page():
    return "<h1>LONMA Terms - Signing is legally binding under Kenya Law</h1><a href='/'>Back</a>"

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>LONMA ORBIT PRO v2.1</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,system-ui} body{background:#0a0a0a;color:#fff;padding-bottom:90px}
.header{position:sticky;top:0;z-index:100;background:#000000ee;backdrop-filter:blur(12px);border-bottom:2px solid #0096B0;padding:12px 14px;display:flex;align-items:center;gap:10px}
.logo{width:48px;height:48px;background:linear-gradient(135deg,#0096B0,#00d4ff);border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:20px;color:#fff;box-shadow:0 4px 12px rgba(0,150,176,0.4)}
.card{background:#161616;border:1px solid #262626;border-radius:16px;padding:14px;margin:10px 12px}
.pill{white-space:nowrap;padding:10px 16px;border-radius:24px;border:1.5px solid #333;background:#1e1e1e;font-size:13px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:6px}
.pill.active{background:#0096B0;border-color:#0096B0;color:#fff;box-shadow:0 4px 12px rgba(0,150,176,0.3)}
.branch-scroll{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;scrollbar-width:none}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 12px}
.stat{background:#161616;border:1px solid #262626;border-radius:14px;padding:12px;text-align:center}
.cat{white-space:nowrap;padding:9px 14px;border-radius:24px;font-size:12px;font-weight:800;cursor:pointer;border:1.5px solid transparent}
.cat.active{transform:scale(1.05)}
.products{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.prod{background:#1e1e1e;border:1px solid #2a2a2a;border-radius:14px;padding:12px;position:relative}
.btn{background:#0096B0;color:#fff;border:none;padding:14px;border-radius:14px;font-weight:900;width:100%;cursor:pointer}
.fab{position:fixed;bottom:20px;right:16px;width:56px;height:56px;background:#FFD700;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:900;color:#000;box-shadow:0 8px 20px rgba(255,215,0,0.4);z-index:99;cursor:pointer}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#000;border-top:1px solid #222;display:flex;justify-content:space-around;padding:8px 0 20px;z-index:90}
.bottom-nav div{font-size:10px;color:#666;text-align:center;cursor:pointer;padding:6px 12px;border-radius:10px}
.bottom-nav div.active{color:#0096B0;background:#0096B01a}
.modal{position:fixed;inset:0;background:#000000ee;display:none;align-items:flex-end;justify-content:center;z-index:200}
.modal-box{background:#161616;border-radius:20px 20px 0 0;width:100%;max-width:500px;padding:20px;max-height:85vh;overflow-y:auto;border-top:2px solid #0096B0}
input,select{width:100%;background:#0a0a0a;border:1.5px solid #333;padding:13px;border-radius:12px;color:#fff;margin:6px 0;font-size:14px}
.bg{background:radial-gradient(circle at 50% 0%,rgba(0,150,176,0.25),transparent 50%),#070707;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:12px}
.card-login{ background:#121212;border:1px solid rgba(0,150,176,0.3);border-radius:20px;padding:22px;width:100%;max-width:400px}
.tabs{display:flex;gap:6px;margin:12px 0}.tab{flex:1;padding:10px;border-radius:20px;border:1px solid #333;background:#111;color:#888;font-weight:700;font-size:12px;cursor:pointer;text-align:center}
.tab.active{background:#0096B0;color:#fff}
#sigCanvas{border:2px dashed #0096B0;border-radius:12px;background:#000;width:100%;height:140px;touch-action:none}
</style></head><body>

<div id="authPage" class="bg"><div class="card-login">
<div style="text-align:center"><div class="logo" style="margin:0 auto 10px">LO</div><div style="font-weight:800;letter-spacing:3px">LONMA ORBIT</div><div style="color:#0096B0;font-size:9px;letter-spacing:3px;margin-top:3px">SIGNING & CREATING PRO v2.1</div></div>
<div class="tabs"><div class="tab active" id="tab-login" onclick="switchAuth('login')">LOGIN</div><div class="tab" id="tab-signup" onclick="switchAuth('signup')">CREATE</div></div>
<div id="loginBox"><input id="user" placeholder="Username"><input id="pass" type="password" placeholder="Password"><div style="display:flex;gap:8px;margin:10px 0;font-size:11px;color:#aaa"><input type="checkbox" id="agree" style="width:16px"><label>I agree to Terms</label></div><div id="err" style="color:#ff4444;font-size:12px;display:none"></div><button class="btn" onclick="doLogin()">LOGIN →</button><div style="background:#000;border:1px dashed #333;border-radius:10px;padding:10px;margin-top:10px;font-size:11px;color:#888"><div onclick="fill('admin','Lonma@2026')" style="cursor:pointer;padding:4px 0">👑 admin / Lonma@2026</div><div onclick="fill('cashier1','1234')" style="cursor:pointer">💰 cashier1 / 1234</div></div></div>
<div id="signupBox" style="display:none"><input id="s-name" placeholder="Full Name"><input id="s-user" placeholder="Username"><input id="s-pass" type="password" placeholder="Password"><select id="s-role"><option value="Cashier">Cashier</option><option value="Manager">Manager</option><option value="Owner">Owner</option></select><select id="s-branch"><option value="lonma-westlands">LONMA Westlands</option><option value="naivas">Naivas</option><option value="carrefour">Carrefour</option><option value="all">All Branches</option></select><div style="margin:12px 0"><small style="color:#0096B0;font-weight:800;font-size:10px">✍️ DRAW SIGNATURE</small><canvas id="sigCanvas"></canvas><div style="display:flex;gap:6px;margin-top:6px"><button class="btn" style="flex:1;padding:8px;background:#111;color:#888" onclick="clearSig()">Clear</button></div><small id="sigStatus" style="color:#666;font-size:10px">Draw with finger</small></div><div style="display:flex;gap:8px;margin:10px 0;font-size:11px;color:#aaa"><input type="checkbox" id="agree2" style="width:16px"><label>Signature is legally binding</label></div><div id="err2" style="color:#ff4444;font-size:12px;display:none"></div><button class="btn" style="background:#FFD700;color:#000" onclick="doSignup()">✍️ SIGN & CREATE</button></div>
</div></div>

<div id="mainPage" style="display:none">
<div class="header"><div class="logo">LO</div><div style="flex:1"><div id="bName" style="font-weight:900;font-size:14px">LONMA Westlands</div><div id="uInfo" style="color:#0096B0;font-size:11px">Marlon • Cashier • Signed</div></div><button onclick="showUsers()" style="background:#111;border:1px solid #333;color:#ccc;padding:8px 14px;border-radius:20px;font-size:11px">Users</button><button onclick="logout()" style="background:#111;border:1px solid #333;color:#666;padding:8px 12px;border-radius:20px;font-size:11px;margin-left:6px">Logout</button></div>
<div class="card"><small style="color:#0096B0;font-weight:900;font-size:10px;letter-spacing:1.5px">BRANCHES - SCROLL →</small><div class="branch-scroll" id="branchList" style="margin-top:10px"></div></div>
<div class="stats"><div class="stat"><small>STOCK</small><b id="stockV" style="color:#0096B0">KES 0</b></div><div class="stat"><small>SALES</small><b id="salesV" style="color:#FFD700">KES 0</b></div><div class="stat"><small>ITEMS</small><b id="itemsV">0</b></div></div>
<div class="card"><small style="color:#0096B0;font-weight:900;font-size:10px">CATEGORIES</small><div style="display:flex;gap:7px;overflow-x:auto;margin:10px 0" id="catTabs"><div class="cat active" style="background:#fff;color:#000" onclick="filterCat('ALL',this)">ALL</div><div class="cat" style="background:#FF9800" onclick="filterCat('FOOD',this)">FOOD</div><div class="cat" style="background:#0096B0;color:#fff" onclick="filterCat('DRINKS',this)">DRINKS</div><div class="cat" style="background:#9C27B0;color:#fff" onclick="filterCat('UTENSILS',this)">UTENSILS</div><div class="cat" style="background:#FFD700" onclick="filterCat('ELECTRONICS',this)">ELECTRONICS</div></div><input id="search" placeholder="🔍 Search..." onkeyup="renderProducts()"><div class="products" id="plist" style="margin-top:12px"></div></div>
<div class="card" style="border:1.5px solid rgba(0,150,176,0.3)"><b>🛒 CART - <span id="cartBranch" style="color:#0096B0">LONMA</span></b><div id="cart" style="margin:10px 0;color:#666">Empty</div><div style="display:flex;justify-content:space-between;margin-top:8px;font-size:18px"><b>TOTAL</b><b id="total" style="color:#0096B0">KES 0</b></div><button class="btn" onclick="checkout()" style="margin-top:12px">💳 CHECKOUT - Signed by Marlon</button></div>
<div class="card" id="usersBox" style="display:none"><b>👥 CREATED USERS</b><div id="usersList" style="margin-top:10px"></div></div>
<div class="fab" onclick="openAddModal()">+</div>
<div class="bottom-nav"><div class="active">🏠<br>Home</div><div onclick="openAddModal()">➕<br>Add</div><div onclick="document.getElementById('cart').scrollIntoView({behavior:'smooth'})">🛒<br>Cart (<span id="cartCount">0</span>)</div><div onclick="showUsers()">👥<br>Users</div></div>
<div class="modal" id="addModal" onclick="if(event.target==this)closeAddModal()"><div class="modal-box"><h3>➕ ADD PRODUCT</h3><input id="p-name" placeholder="Name"><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px"><input id="p-price" type="number" placeholder="Price KES"><input id="p-stock" type="number" placeholder="Stock"></div><select id="p-cat"><option value="FOOD">FOOD</option><option value="DRINKS">DRINKS</option><option value="UTENSILS">UTENSILS</option><option value="ELECTRONICS">ELECTRONICS</option></select><button class="btn" style="background:#FFD700;color:#000;margin-top:10px" onclick="addProduct()">SAVE</button><button class="btn" style="background:#111;color:#888;margin-top:8px" onclick="closeAddModal()">Cancel</button></div></div>
<div class="modal" id="receiptModal"><div class="modal-box" style="text-align:center"><div style="width:60px;height:60px;background:#0096B0;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:30px">✅</div><h2>Sale Complete!</h2><div id="receiptContent" style="background:#000;border-radius:12px;padding:14px;margin:14px 0;text-align:left;font-family:monospace;font-size:12px"></div><button class="btn" onclick="closeReceipt()">New Sale</button></div></div>
</div>

<script>
let current='lonma-westlands'; let branches={}; let cart=[]; let activeCat='ALL'; let me=null; let signatureData='';
function switchAuth(t){document.getElementById('tab-login').classList.remove('active');document.getElementById('tab-signup').classList.remove('active');document.getElementById('loginBox').style.display='none';document.getElementById('signupBox').style.display='none';if(t=='login'){document.getElementById('tab-login').classList.add('active');document.getElementById('loginBox').style.display='block'}else{document.getElementById('tab-signup').classList.add('active');document.getElementById('signupBox').style.display='block';initSig();}}
function fill(u,p){document.getElementById('user').value=u; document.getElementById('pass').value=p;}
async function doLogin(){let u=document.getElementById('user').value; let p=document.getElementById('pass').value; let agree=document.getElementById('agree').checked; if(!agree){document.getElementById('err').style.display='block';document.getElementById('err').innerText='Accept Terms';return} let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})}); if(!r.ok){document.getElementById('err').style.display='block';document.getElementById('err').innerText='Wrong';return} me=await r.json(); localStorage.setItem('lonma_user',JSON.stringify(me)); showMain();}
async function doSignup(){let name=document.getElementById('s-name').value; let user=document.getElementById('s-user').value; let pass=document.getElementById('s-pass').value; let role=document.getElementById('s-role').value; let branch=document.getElementById('s-branch').value; let agree=document.getElementById('agree2').checked; if(!name||!user||!pass){document.getElementById('err2').style.display='block';document.getElementById('err2').innerText='Fill fields';return} if(!agree){document.getElementById('err2').style.display='block';document.getElementById('err2').innerText='Accept Terms';return} if(!signatureData){document.getElementById('err2').style.display='block';document.getElementById('err2').innerText='Draw signature';return} let r=await fetch('/api/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:user,password:pass,name:name,role:role,branch:branch,signature:signatureData})}); if(!r.ok){let d=await r.json(); document.getElementById('err2').style.display='block';document.getElementById('err2').innerText=d.detail;return} alert('Created! Login now'); switchAuth('login'); document.getElementById('user').value=user;}
function showMain(){document.getElementById('authPage').style.display='none';document.getElementById('mainPage').style.display='block';document.getElementById('uInfo').innerText=me.name+' • '+me.role+' • Signed'; loadBranches();}
function logout(){localStorage.removeItem('lonma_user');location.reload();}
async function loadBranches(){let r=await fetch('/api/supermarkets'); branches=await r.json(); document.getElementById('branchList').innerHTML=Object.entries(branches).map(([id,b])=>`<div class="pill ${id==current?'active':''}" onclick="selectBranch('${id}')">${b.icon} ${b.name}</div>`).join(''); let b=branches[current]; document.getElementById('bName').innerText=b.name; document.getElementById('cartBranch').innerText=b.name; document.getElementById('itemsV').innerText=b.products.length; let tot=0; b.products.forEach(p=>tot+=p.price*p.stock); document.getElementById('stockV').innerText='KES '+tot.toLocaleString(); renderProducts(); loadSales();}
function selectBranch(id){current=id; loadBranches();}
function filterCat(c,el){activeCat=c; document.querySelectorAll('.cat').forEach(x=>x.classList.remove('active')); el.classList.add('active'); renderProducts();}
function renderProducts(){let b=branches[current]; let q=document.getElementById('search').value.toLowerCase(); let list=b.products.filter(p=>(activeCat=='ALL'||p.cat==activeCat)&&p.name.toLowerCase().includes(q)); document.getElementById('plist').innerHTML=list.map(p=>`<div class="prod" onclick="addCart('${p.id}')"><div style="position:absolute;top:8px;right:8px;font-size:9px;background:#000;padding:3px 6px;border-radius:10px;color:${p.stock<20?'#ff4444':'#888'}">${p.stock} left</div><div style="font-size:22px">${p.emoji||'📦'}</div><small style="background:${p.cat=='FOOD'?'#FF9800':p.cat=='DRINKS'?'#0096B0':p.cat=='UTENSILS'?'#9C27B0':'#FFD700'};color:#000;padding:2px 6px;border-radius:5px;font-size:9px;font-weight:900">${p.cat}</small><div style="font-weight:700;margin-top:4px;font-size:12px">${p.name}</div><div style="color:#0096B0;font-weight:800">KES ${p.price}</div><div style="margin-top:6px;background:#0096B0;color:#fff;text-align:center;padding:5px;border-radius:8px;font-size:11px;font-weight:800">+ ADD</div></div>`).join('');}
function addCart(pid){let p=branches[current].products.find(x=>x.id==pid); let c=cart.find(x=>x.product_id==pid); if(c) c.qty++; else cart.push({product_id:pid,qty:1,name:p.name,price:p.price}); renderCart();}
function renderCart(){document.getElementById('cartCount').innerText=cart.reduce((a,b)=>a+b.qty,0); if(cart.length==0){document.getElementById('cart').innerHTML='Empty';document.getElementById('total').innerText='KES 0';return} let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #222"><span>${i.name} x${i.qty}</span><span style="color:#0096B0">KES ${i.price*i.qty}</span></div>`}).join(''); document.getElementById('total').innerText='KES '+total.toLocaleString();}
async function checkout(){if(cart.length==0) return alert('Empty'); let r=await fetch(`/api/${current}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart.map(c=>({product_id:c.product_id,qty:c.qty}))) }); let d=await r.json(); document.getElementById('receiptContent').innerHTML=`Receipt: <b>${d.receipt}</b><br>${d.items.map(i=>i.name+' x'+i.qty).join('<br>')}<br><br>TOTAL KES ${d.total}`; document.getElementById('receiptModal').style.display='flex'; cart=[]; renderCart(); loadBranches();}
function closeReceipt(){document.getElementById('receiptModal').style.display='none';}
function openAddModal(){document.getElementById('addModal').style.display='flex';}
function closeAddModal(){document.getElementById('addModal').style.display='none';}
async function addProduct(){let name=document.getElementById('p-name').value; let price=parseFloat(document.getElementById('p-price').value); let stock=parseInt(document.getElementById('p-stock').value); let cat=document.getElementById('p-cat').value; if(!name||!price||!stock) return alert('Fill all'); let r=await fetch(`/api/${current}/products`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,price,stock,cat})}); closeAddModal(); loadBranches(); alert('Added '+name);}
async function loadSales(){let r=await fetch(`/api/${current}/sales`); let s=await r.json(); let tot=s.reduce((a,b)=>a+b.total,0); document.getElementById('salesV').innerText='KES '+tot.toLocaleString();}
async function showUsers(){let box=document.getElementById('usersBox'); box.style.display=box.style.display=='none'?'block':'none'; let r=await fetch('/api/users'); let u=await r.json(); document.getElementById('usersList').innerHTML=u.map(x=>`<div style="padding:8px 0;border-bottom:1px solid #222;display:flex;justify-content:space-between"><span><b>${x.name}</b><br><small style="color:#888">${x.role} • ${x.branch}</small></span><small>${x.created?.substring(0,10)}</small></div>`).join('');}
let canvas, ctx, drawing=false;
function initSig(){canvas=document.getElementById('sigCanvas'); if(!canvas) return; ctx=canvas.getContext('2d'); canvas.width=canvas.offsetWidth*2; canvas.height=140*2; ctx.scale(2,2); ctx.strokeStyle='#0096B0'; ctx.lineWidth=2; ctx.lineCap='round'; function pos(e){let rect=canvas.getBoundingClientRect(); let x=(e.touches?e.touches[0].clientX:e.clientX)-rect.left; let y=(e.touches?e.touches[0].clientY:e.clientY)-rect.top; return {x,y};} canvas.addEventListener('mousedown', e=>{drawing=true; let p=pos(e); ctx.beginPath(); ctx.moveTo(p.x,p.y);}); canvas.addEventListener('mousemove', e=>{if(!drawing) return; let p=pos(e); ctx.lineTo(p.x,p.y); ctx.stroke();}); canvas.addEventListener('mouseup', ()=>{drawing=false; saveSig();}); canvas.addEventListener('touchstart', e=>{e.preventDefault(); drawing=true; let p=pos(e); ctx.beginPath(); ctx.moveTo(p.x,p.y);}); canvas.addEventListener('touchmove', e=>{e.preventDefault(); if(!drawing) return; let p=pos(e); ctx.lineTo(p.x,p.y); ctx.stroke();}); canvas.addEventListener('touchend', e=>{e.preventDefault(); drawing=false; saveSig();});}
function clearSig(){if(!canvas) return; ctx.clearRect(0,0,canvas.width,canvas.height); signatureData=''; document.getElementById('sigStatus').innerText='Cleared';}
function saveSig(){if(!canvas) return; signatureData=canvas.toDataURL(); document.getElementById('sigStatus').innerText='✅ Signature captured'; document.getElementById('sigStatus').style.color='#0096B0';}
(function(){let s=localStorage.getItem('lonma_user'); if(s){me=JSON.parse(s); showMain();}})();
</script></body></html>
    """
