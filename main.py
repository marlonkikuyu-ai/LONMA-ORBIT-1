from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI()

USERS = {
    "admin": {"password": "Lonma@2026", "role": "Owner", "name": "Marlone - Owner", "branch": "all", "signature": None, "created": "2026-10-03"},
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
    {"name": "Milk - Brookside 500ml", "price": 65, "stock": 500, "cat": "DRINKS"},
    {"name": "Soda - Coca 500ml", "price": 70, "stock": 1000, "cat": "DRINKS"},
    {"name": "Sufuria - 3pc Set", "price": 1850, "stock": 40, "cat": "UTENSILS"},
    {"name": "Gas Cooker - 2 Burner", "price": 4500, "stock": 15, "cat": "ELECTRONICS"},
]
for sm in SUPERMARKETS.values():
    sm["products"] = [dict(p, id=str(uuid.uuid4())[:6]) for p in seed]

class Login(BaseModel):
    username: str; password: str
class Signup(BaseModel):
    username: str; password: str; name: str; role: str; branch: str; signature: str = ""
class Product(BaseModel):
    name: str; price: float; stock: int; cat: str
class CartItem(BaseModel):
    product_id: str; qty: int = 1

@app.head("/")
async def head_root(): return Response(status_code=200)

@app.post("/api/login")
async def login(l: Login):
    from fastapi import HTTPException
    u = USERS.get(l.username.lower())
    if not u or u["password"]!= l.password:
        raise HTTPException(status_code=401, detail="Wrong")
    return {"username": l.username, "role": u["role"], "name": u["name"], "branch": u["branch"], "signature": u.get("signature","")}

@app.post("/api/signup")
async def signup(s: Signup):
    from fastapi import HTTPException
    if s.username.lower() in USERS:
        raise HTTPException(status_code=400, detail="Username exists")
    USERS[s.username.lower()] = {"password": s.password, "role": s.role, "name": s.name, "branch": s.branch, "signature": s.signature, "created": datetime.now().isoformat()}
    return {"ok": True, "username": s.username}

@app.get("/api/users")
async def list_users():
    return [{"username": k, "name": v["name"], "role": v["role"], "branch": v["branch"], "created": v.get("created",""), "hasSignature": bool(v.get("signature"))} for k,v in USERS.items()]

@app.get("/terms", response_class=HTMLResponse)
async def terms_page():
    return """<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#070707;color:#ccc;padding:16px;font-family:system-ui;max-width:800px;margin:0 auto;line-height:1.6}h1{color:#0096B0}.card{background:#121212;border:1px solid #222;border-radius:12px;padding:14px;margin:10px 0}</style></head><body>
<h1>LO LONMA ORBIT TERMS</h1><small>Effective 3 Oct 2026 - Nairobi, Kenya</small>
<div class="card"><b>1. ACCEPTANCE</b><br>By signing digitally and creating account, you agree to Kenya DPA 2019, KRA compliance, and Superchain OS license. Signature is legally binding.</div>
<div class="card"><b>2. DIGITAL SIGNATURE</b><br>Your drawn signature on canvas is stored as acceptance of T&C. Equivalent to handwritten signature under Kenya Electronic Transactions.</div>
<div class="card"><b>3. CREATING ACCOUNTS</b><br>Owner can create Manager/Cashier. Cashiers: checkout only. Managers: manage branch stock. Owner: all branches.</div>
<div class="card"><b>4. BRANCHES</b><br>LONMA, Naivas, Carrefour, Chandarana, Magunas, Khetias, Mathai's are separate. Trademarks belong to owners. For demo of multi-branch chain.</div>
<div class="card"><b>5. LIABILITY</b><br>Max KES 10,000. Not liable for stock loss, power failure. Sales data in-memory for demo.</div>
<br><a href="/" style="background:#0096B0;color:#fff;padding:12px 20px;border-radius:10px;text-decoration:none;font-weight:800">← BACK TO CREATE & SIGN</a></body></html>"""

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA ORBIT - SIGNING & CREATING</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui} body{background:#070707;color:#fff;min-height:100vh}
.bg{background:radial-gradient(circle at 50% 0%,rgba(0,150,176,0.25),transparent 50%),#070707;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:12px}
.card{ background:#121212;border:1px solid rgba(0,150,176,0.3);border-radius:20px;padding:22px;width:100%;max-width:400px;box-shadow:0 20px 60px rgba(0,0,0,0.8)}
.logo{width:60px;height:60px;background:#0096B0;border-radius:14px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:24px;margin:0 auto 10px}
input,select{width:100%;background:#000;border:1px solid #333;padding:12px;border-radius:10px;color:#fff;margin:5px 0;font-size:14px}
.btn{background:#0096B0;color:#fff;border:none;padding:12px;border-radius:10px;font-weight:800;width:100%;margin-top:8px;cursor:pointer}
.btn-gold{background:#FFD700;color:#000}.btn-black{background:#000;border:1px solid #333;color:#888}
.tabs{display:flex;gap:6px;margin:12px 0}.tab{flex:1;padding:10px;border-radius:20px;border:1px solid #333;background:#111;color:#888;font-weight:700;font-size:12px;cursor:pointer;text-align:center}
.tab.active{background:#0096B0;color:#fff;border-color:#0096B0}
#sigCanvas{border:2px dashed #0096B0;border-radius:12px;background:#000;width:100%;height:140px;touch-action:none;cursor:crosshair}
.header{position:sticky;top:0;z-index:99;background:#000;border-bottom:2px solid #0096B0;padding:10px 14px;display:flex;align-items:center;gap:10px}
.container{padding:12px;max-width:700px;margin:0 auto}.pill{white-space:nowrap;padding:8px 12px;border-radius:20px;border:1px solid #333;background:#151515;font-size:12px;font-weight:700;cursor:pointer}
.pill.active{background:#0096B0;color:#fff}.cat-tabs{display:flex;gap:6px;overflow-x:auto;margin:8px 0}.cat{white-space:nowrap;padding:7px 11px;border-radius:20px;font-size:11px;font-weight:800;cursor:pointer}
.products{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.prod{background:#1a1a1a;border:1px solid #222;border-radius:12px;padding:10px;cursor:pointer}.price{color:#0096B0;font-weight:800}
.branch-scroll{display:flex;gap:8px;overflow-x:auto}
</style></head><body>

<div id="authPage" class="bg">
<div class="card">
<div class="logo">LO</div>
<div style="text-align:center"><div style="font-weight:800;letter-spacing:3px">LONMA ORBIT</div><div style="color:#0096B0;font-size:9px;letter-spacing:3px;margin-top:3px">SIGNING & CREATING OS</div></div>

<div class="tabs">
<div class="tab active" id="tab-login" onclick="switchAuth('login')">LOGIN</div>
<div class="tab" id="tab-signup" onclick="switchAuth('signup')">CREATE ACCOUNT</div>
</div>

<div id="loginBox">
<input id="user" placeholder="Username">
<input id="pass" type="password" placeholder="Password">
<div style="display:flex;gap:8px;align-items:flex-start;margin:10px 0;font-size:11px;color:#aaa"><input type="checkbox" id="agree" style="width:16px;height:16px"><label for="agree">I agree to <a href="/terms" target="_blank" style="color:#0096B0">Terms & Conditions</a></label></div>
<div id="err" style="color:#ff4444;font-size:12px;display:none;margin-bottom:6px"></div>
<button class="btn" onclick="doLogin()">LOGIN →</button>
<div style="background:#000;border:1px dashed #333;border-radius:10px;padding:10px;margin-top:10px;font-size:11px;color:#888">
<div onclick="fill('admin','Lonma@2026')" style="cursor:pointer;padding:4px 0">👑 admin / Lonma@2026</div>
<div onclick="fill('cashier1','1234')" style="cursor:pointer">💰 cashier1 / 1234</div>
</div>
</div>

<div id="signupBox" style="display:none">
<input id="s-name" placeholder="Full Name - e.g., John Kamau">
<input id="s-user" placeholder="Username - e.g., john_k">
<input id="s-pass" type="password" placeholder="Create Password">
<select id="s-role"><option value="Cashier">Cashier - Checkout Only</option><option value="Manager">Manager - Branch Admin</option><option value="Owner">Owner - All Branches</option></select>
<select id="s-branch"><option value="lonma-westlands">LONMA Westlands - HQ</option><option value="naivas">Naivas</option><option value="carrefour">Carrefour</option><option value="chandarana">Chandarana</option><option value="magunas">Magunas</option><option value="khetias">Khetias</option><option value="mathais">Mathai's</option><option value="all">All Branches (Owner Only)</option></select>

<div style="margin:12px 0"><small style="color:#0096B0;font-weight:800;letter-spacing:2px;font-size:10px">✍️ DRAW YOUR SIGNATURE BELOW - LEGAL BINDING</small>
<canvas id="sigCanvas"></canvas>
<div style="display:flex;gap:6px;margin-top:6px"><button class="btn-black btn" style="flex:1;padding:8px;font-size:11px" onclick="clearSig()">Clear</button><button class="btn-black btn" style="flex:1;padding:8px;font-size:11px" onclick="saveSigPreview()">Preview</button></div>
<small id="sigStatus" style="color:#666;font-size:10px">Draw signature with finger / mouse</small>
</div>

<div style="display:flex;gap:8px;align-items:flex-start;margin:10px 0;font-size:11px;color:#aaa"><input type="checkbox" id="agree2" style="width:16px;height:16px"><label for="agree2">I have read <a href="/terms" target="_blank" style="color:#0096B0">Terms</a> and my signature above is legally binding under Kenya Law</label></div>
<div id="err2" style="color:#ff4444;font-size:12px;display:none;margin-bottom:6px"></div>
<button class="btn btn-gold" onclick="doSignup()">✍️ SIGN & CREATE ACCOUNT</button>
<button class="btn btn-black" onclick="switchAuth('login')">Already have account? Login</button>
</div>

<div style="text-align:center;padding:12px;font-size:9px;color:#444"><a href="/terms" style="color:#444;text-decoration:none">Terms</a> • <a href="/terms" style="color:#444;text-decoration:none">Privacy</a> • © 2026 LO</div>
</div>
</div>

<div id="mainPage" style="display:none">
<div class="header"><div class="logo" style="width:40px;height:40px;font-size:16px">LO</div><div><div style="font-weight:800;font-size:12px;letter-spacing:2px" id="curName">Loading</div><div style="color:#0096B0;font-size:9px" id="userInfo"></div></div><div style="margin-left:auto;display:flex;gap:6px"><button onclick="showUsers()" style="background:#111;border:1px solid #333;color:#888;padding:6px 10px;border-radius:20px;font-size:10px">Users</button><button onclick="logout()" style="background:#111;border:1px solid #333;color:#888;padding:6px 10px;border-radius:20px;font-size:10px">Logout</button></div></div>
<div class="container">
<div class="card" style="background:#121212;border:1px solid rgba(0,150,176,0.18);border-radius:14px;padding:12px;margin-bottom:12px"><small style="color:#0096B0;font-weight:800;font-size:9px">BRANCHES - SCROLL →</small><div class="branch-scroll" id="branchList" style="margin-top:6px"></div></div>
<div class="card" style="display:flex;justify-content:space-between;text-align:center;background:#121212;border-radius:14px;padding:12px;margin-bottom:12px"><div><small style="color:#888">STOCK</small><div id="stockValue" style="color:#0096B0;font-weight:800">0</div></div><div><small style="color:#888">SALES</small><div id="todaySales" style="color:#FFD700;font-weight:800">0</div></div><div><small style="color:#888">ITEMS</small><div id="prodCount" style="font-weight:800">0</div></div></div>
<div class="card" style="background:#121212;border-radius:14px;padding:12px;margin-bottom:12px"><small style="color:#0096B0;font-weight:800;font-size:9px">CATEGORIES</small><div class="cat-tabs"><div class="cat active" style="background:#fff;color:#000" id="tab-ALL" onclick="filterCat('ALL')">ALL</div><div class="cat" style="background:#FF9800" id="tab-FOOD" onclick="filterCat('FOOD')">FOOD</div><div class="cat" style="background:#0096B0;color:#fff" id="tab-DRINKS" onclick="filterCat('DRINKS')">DRINKS</div><div class="cat" style="background:#9C27B0;color:#fff" id="tab-UTENSILS" onclick="filterCat('UTENSILS')">UTENSILS</div><div class="cat" style="background:#FFD700" id="tab-ELECTRONICS" onclick="filterCat('ELECTRONICS')">ELECTRONICS</div></div><input id="search" placeholder="🔍 Search..." onkeyup="renderProducts()" style="width:100%;background:#000;border:1px solid #333;padding:10px;border-radius:10px;color:#fff;margin-top:8px"><div class="products" id="plist" style="margin-top:8px"></div></div>
<div class="card" style="background:#121212;border-radius:14px;padding:12px;margin-bottom:12px"><b>🛒 CART - <span id="cartBranch" style="color:#0096B0"></span></b><div id="cart" style="margin-top:8px;color:#666;font-size:13px">Empty</div><div style="display:flex;justify-content:space-between;margin-top:10px;border-top:1px solid #222;padding-top:8px"><b>TOTAL</b><b id="total" style="color:#0096B0;font-size:18px">KES 0</b></div><button class="btn" style="width:100%;margin-top:8px" onclick="checkout()">CHECKOUT - Signed by <span id="signName"></span></button></div>
<div id="usersBox" class="card" style="display:none;background:#121212;border-radius:14px;padding:12px"><b>👥 CREATED USERS</b><div id="usersList" style="margin-top:8px;font-size:12px"></div></div>
</div>
</div>

<script>
let current='lonma-westlands'; let branches={}; let cart=[]; let activeCat='ALL'; let me=null; let signatureData='';
function switchAuth(t){document.getElementById('tab-login').classList.remove('active');document.getElementById('tab-signup').classList.remove('active');document.getElementById('loginBox').style.display='none';document.getElementById('signupBox').style.display='none';if(t=='login'){document.getElementById('tab-login').classList.add('active');document.getElementById('loginBox').style.display='block'}else{document.getElementById('tab-signup').classList.add('active');document.getElementById('signupBox').style.display='block'; initSig();}}
function fill(u,p){document.getElementById('user').value=u; document.getElementById('pass').value=p;}
async function doLogin(){
  let u=document.getElementById('user').value; let p=document.getElementById('pass').value; let agree=document.getElementById('agree').checked;
  if(!agree){document.getElementById('err').style.display='block'; document.getElementById('err').innerText='⚠️ Accept Terms'; return}
  if(!u||!p){document.getElementById('err').style.display='block'; document.getElementById('err').innerText='Enter credentials'; return}
  let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  if(!r.ok){document.getElementById('err').style.display='block'; document.getElementById('err').innerText='❌ Wrong credentials'; return}
  me=await r.json(); me.acceptedAt=new Date().toISOString(); localStorage.setItem('lonma_user',JSON.stringify(me)); showMain();
}
async function doSignup(){
  let name=document.getElementById('s-name').value; let user=document.getElementById('s-user').value; let pass=document.getElementById('s-pass').value;
  let role=document.getElementById('s-role').value; let branch=document.getElementById('s-branch').value; let agree=document.getElementById('agree2').checked;
  if(!name||!user||!pass){document.getElementById('err2').style.display='block'; document.getElementById('err2').innerText='Fill all fields'; return}
  if(!agree){document.getElementById('err2').style.display='block'; document.getElementById('err2').innerText='Accept Terms & Sign'; return}
  if(!signatureData){document.getElementById('err2').style.display='block'; document.getElementById('err2').innerText='⚠️ Draw your signature first'; return}
  let r=await fetch('/api/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:user,password:pass,name:name,role:role,branch:branch,signature:signatureData})});
  if(!r.ok){let d=await r.json(); document.getElementById('err2').style.display='block'; document.getElementById('err2').innerText=d.detail; return}
  alert('✅ Account Created & Signed!\\nUsername: '+user+'\\nRole: '+role+'\\nSignature saved - Legally binding\\nNow Login');
  switchAuth('login'); document.getElementById('user').value=user;
}
function showMain(){document.getElementById('authPage').style.display='none'; document.getElementById('mainPage').style.display='block'; document.getElementById('userInfo').innerText=me.name+' • '+me.role+(me.signature?' • ✍️ Signed':''); document.getElementById('signName').innerText=me.name; loadBranches();}
function logout(){localStorage.removeItem('lonma_user'); location.reload();}
function showUsers(){let b=document.getElementById('usersBox'); b.style.display=b.style.display=='none'?'block':'none'; loadUsers();}
async function loadUsers(){let r=await fetch('/api/users'); let u=await r.json(); document.getElementById('usersList').innerHTML=u.map(x=>`<div style="padding:8px 0;border-bottom:1px solid #222;display:flex;justify-content:space-between"><span><b>${x.name}</b> (${x.username})<br><small style="color:#888">${x.role} • ${x.branch} • ${x.hasSignature?'✍️ Signed':'No sig'}</small></span><small style="color:#555">${x.created?x.created.substring(0,10):''}</small></div>`).join('');}
(function(){let s=localStorage.getItem('lonma_user'); if(s){me=JSON.parse(s); showMain();}})();
async function loadBranches(){
  let r=await fetch('/api/supermarkets'); branches=await r.json(); let tot=0; Object.values(branches).forEach(b=>b.products.forEach(p=>tot+=p.price*p.stock)); document.getElementById('stockValue').innerText='KES '+tot.toLocaleString();
  let list=Object.entries(branches); if(me.branch!='all') list=list.filter(([id])=>id==me.branch);
  document.getElementById('branchList').innerHTML=list.map(([id,b])=>`<div class="pill ${id==current?'active':''}" onclick="selectBranch('${id}')">${b.name}</div>`).join('');
  let b=branches[current]; document.getElementById('curName').innerText=b.name; document.getElementById('cartBranch').innerText=b.name; document.getElementById('prodCount').innerText=b.products.length; renderProducts(); loadSales();
}
function selectBranch(id){current=id; cart=[]; renderCart(); loadBranches();}
function filterCat(c){activeCat=c; document.querySelectorAll('.cat').forEach(x=>x.classList.remove('active')); let el=document.getElementById('tab-'+c); if(el) el.classList.add('active'); renderProducts();}
function renderProducts(){let b=branches[current]; if(!b) return; let q=document.getElementById('search').value.toLowerCase(); let list=b.products.filter(p=>(activeCat=='ALL'||p.cat==activeCat)&&p.name.toLowerCase().includes(q)); let col={"FOOD":"#FF9800","DRINKS":"#0096B0","UTENSILS":"#9C27B0","ELECTRONICS":"#FFD700"}; document.getElementById('plist').innerHTML=list.map(p=>`<div class="prod" onclick="addCart('${p.id}')"><small style="background:${col[p.cat]};color:#000;padding:2px 5px;border-radius:5px;font-size:8px;font-weight:900">${p.cat}</small><div style="font-weight:700;margin-top:5px;font-size:12px">${p.name}</div><div class="price">KES ${p.price}</div></div>`).join('');}
function addCart(pid){let p=branches[current].products.find(x=>x.id==pid); let c=cart.find(x=>x.product_id==pid); if(c) c.qty++; else cart.push({product_id:pid,qty:1,name:p.name,price:p.price,cat:p.cat}); renderCart();}
function renderCart(){if(cart.length==0){document.getElementById('cart').innerHTML='Empty'; document.getElementById('total').innerText='KES 0'; return} let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #222"><span>${i.name} x${i.qty}</span><span style="color:#0096B0">KES ${i.price*i.qty}</span></div>`}).join(''); document.getElementById('total').innerText='KES '+total.toLocaleString();}
async function checkout(){if(cart.length==0) return alert('Empty'); let r=await fetch(`/api/${current}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart)}); let d=await r.json(); alert('✅ SALE\\n'+d.receipt+' KES '+d.total+'\\nSigned by: '+me.name+'\\nSignature on file: '+(me.signature?'YES - Legal':'No')); cart=[]; renderCart(); loadBranches();}
async function loadSales(){let r=await fetch(`/api/${current}/sales`); let s=await r.json(); let tot=s.reduce((a,b)=>a+b.total,0); let el=document.getElementById('todaySales'); if(el) el.innerText='KES '+tot.toLocaleString();}

let canvas, ctx, drawing=false;
function initSig(){
  canvas=document.getElementById('sigCanvas'); if(!canvas) return; ctx=canvas.getContext('2d');
  canvas.width=canvas.offsetWidth*2; canvas.height=140*2; ctx.scale(2,2); ctx.strokeStyle='#0096B0'; ctx.lineWidth=2; ctx.lineCap='round';
  function pos(e){let rect=canvas.getBoundingClientRect(); let x=(e.touches?e.touches[0].clientX:e.clientX)-rect.left; let y=(e.touches?e.touches[0].clientY:e.clientY)-rect.top; return {x,y};}
  canvas.addEventListener('mousedown', e=>{drawing=true; let p=pos(e); ctx.beginPath(); ctx.moveTo(p.x,p.y);});
  canvas.addEventListener('mousemove', e=>{if(!drawing) return; let p=pos(e); ctx.lineTo(p.x,p.y); ctx.stroke();});
  canvas.addEventListener('mouseup', ()=>{drawing=false; saveSigPreview();}); canvas.addEventListener('mouseleave', ()=>drawing=false);
  canvas.addEventListener('touchstart', e=>{e.preventDefault(); drawing=true; let p=pos(e); ctx.beginPath(); ctx.moveTo(p.x,p.y);});
  canvas.addEventListener('touchmove', e=>{e.preventDefault(); if(!drawing) return; let p=pos(e); ctx.lineTo(p.x,p.y); ctx.stroke();});
  canvas.addEventListener('touchend', e=>{e.preventDefault(); drawing=false; saveSigPreview();});
}
function clearSig(){if(!canvas) return; ctx.clearRect(0,0,canvas.width,canvas.height); signatureData=''; document.getElementById('sigStatus').innerText='Cleared - Draw again'; document.getElementById('sigStatus').style.color='#666';}
function saveSigPreview(){if(!canvas) return; signatureData=canvas.toDataURL(); document.getElementById('sigStatus').innerText='✅ Signature captured - Legally binding'; document.getElementById('sigStatus').style.color='#0096B0';}
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
