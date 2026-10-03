from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI()

USERS = {
    "admin": {"password": "Lonma@2026", "role": "Owner", "name": "Marlone - Owner", "branch": "all"},
    "marlone": {"password": "Orbit2026", "role": "CEO", "name": "Marlone CEO", "branch": "all"},
    "cashier1": {"password": "1234", "role": "Cashier", "name": "Cashier 1", "branch": "lonma-westlands"},
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
        raise HTTPException(status_code=401, detail="Wrong credentials")
    return {"username": l.username, "role": u["role"], "name": u["name"], "branch": u["branch"]}

@app.get("/terms", response_class=HTMLResponse)
async def terms_page():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Terms & Conditions - LONMA ORBIT</title>
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui} body{background:#070707;color:#ddd;padding:16px;max-width:800px;margin:0 auto;line-height:1.6}
h1{color:#0096B0;letter-spacing:3px;font-size:20px;margin:20px 0 10px} h2{color:#fff;font-size:14px;margin:18px 0 8px;letter-spacing:1px}
.card{background:#121212;border:1px solid #222;border-radius:12px;padding:16px;margin:12px 0} small{color:#888} a{color:#0096B0}.logo{width:60px;height:60px;background:#0096B0;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:24px;color:#fff;margin-bottom:10px}
.btn{background:#0096B0;color:#fff;border:none;padding:12px 20px;border-radius:10px;font-weight:800;cursor:pointer;text-decoration:none;display:inline-block;margin-top:12px}
</style></head><body>
<div class="logo">LO</div>
<h1>LONMA ORBIT - TERMS & CONDITIONS</h1>
<small>Effective Date: 3rd October 2026 • Version 1.0 • Nairobi, Kenya</small>

<div class="card"><h2>1. ACCEPTANCE OF TERMS</h2>
By accessing app.lonmaorbit.co.ke and LONMA Superchain OS, you agree to these Terms. If you are a cashier, manager, or owner of Naivas, Carrefour, Chandarana, Magunas, Khetias, Mathai's or LONMA branches, your use is bound by this agreement under Kenyan Law.</div>

<div class="card"><h2>2. SUPERCHAIN OS LICENSE</h2>
LONMA ORBIT grants a non-exclusive license to use Superchain OS for supermarket operations: inventory (FOOD, DRINKS, UTENSILS, ELECTRONICS), sales, checkout, and reporting. You may NOT copy, resell, or reverse-engineer the system without written permission from Marlone - Owner.</div>

<div class="card"><h2>3. USER ACCOUNTS & SECURITY</h2>
• Admin / CEO credentials: Full access to all 7 branches<br>
• Manager credentials: Access to assigned branch only<br>
• Cashier credentials (e.g., cashier1 / 1234): Checkout only, cannot add products<br>
• You are responsible for keeping passwords confidential. Any sale made under your login is your responsibility.<br>
• LONMA ORBIT is not liable for theft due to shared passwords.</div>

<div class="card"><h2>4. PRODUCT CATEGORIES</h2>
All products must be categorized as:<br>
<b>FOOD</b> - Perishables, groceries, bakery (KEBS standards apply)<br>
<b>DRINKS</b> - Milk, soda, water, juices (Must check expiry)<br>
<b>UTENSILS</b> - Sufuria, plates, cooking tools<br>
<b>ELECTRONICS</b> - Gas cookers, blenders, extensions (12-month warranty disclaimer must be given to customer)<br>
Mis-categorization affecting tax (VAT) is user's liability.</div>

<div class="card"><h2>5. SALES, RECEIPTS & KRA COMPLIANCE</h2>
• Every checkout generates a receipt (e.g., LON-XXXX). You must provide receipt to customer.<br>
• Prices are in KES. System stock deduction is final - ensure physical stock matches.<br>
• This system is NOT yet KRA eTIMS certified. Owner must integrate with KRA for tax compliance. LONMA ORBIT provides data only.<br>
• Sales data is stored in-memory for demo - for production, owner must enable database persistence.</div>

<div class="card"><h2>6. BRANCHES: NAIVAS, CARREFOUR, CHANDARANA, MAGUNAS, KHETIAS, MATHAI'S</h2>
Use of third-party supermarket names is for demonstration of multi-branch chain capability. LONMA ORBIT is not affiliated with Naivas Ltd, Carrefour Kenya (Majid Al Futtaim), Chandarana FoodPlus, Magunas, Khetias, or Mathai's Supermarkets. All trademarks belong to their owners. If you represent these brands and want removal, contact legal@lonmaorbit.co.ke</div>

<div class="card"><h2>7. DATA PRIVACY - KENYA DPA 2019</h2>
We comply with Kenya Data Protection Act 2019. Sales data, login times, IP (e.g., 102.6.24.228) are logged for audit. No customer phone numbers are stored unless M-Pesa module enabled. Cashier activity is tracked by username.</div>

<div class="card"><h2>8. LIMITATION OF LIABILITY</h2>
LONMA ORBIT Superchain OS is provided "AS IS". Maximum liability is KES 10,000 or last month's subscription, whichever is lower. Not liable for: stock loss, incorrect pricing, power failure during checkout, or loss of sales data due to in-memory storage.</div>

<div class="card"><h2>9. PAYMENTS & M-PESA</h2>
When M-Pesa module is active, STK Push uses Safaricom Daraja. Transaction fees are per Safaricom. LONMA does not hold customer funds.</div>

<div class="card"><h2>10. TERMINATION</h2>
We may suspend cashier accounts for fraud, sharing credentials, or stock theft patterns. Owner (admin) can delete branches.</div>

<div class="card"><h2>11. GOVERNING LAW</h2>
These Terms are governed by Laws of Kenya. Disputes: Milimani Law Courts, Nairobi. Contact: Marlone - LONMA ORBIT, Westlands Mall, Nairobi - support@lonmaorbit.co.ke - +254 700 000 000</div>

<div class="card" style="border-color:#0096B0;background:rgba(0,150,176,0.08)"><h2>12. ACCEPTANCE</h2>
By checking "I agree to Terms & Conditions" on login, you confirm you have read, understood, and agree to be bound. You are 18+ years old.<br><br>
<small>© 2026 LONMA ORBIT - LO. All Rights Reserved. Superchain OS v4.0<br>App: https://app.lonmaorbit.co.ke</small></div>

<a href="/" class="btn">← BACK TO LOGIN & ACCEPT</a>
<br><br><br>
</body></html>
    """

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA ORBIT - LOGIN</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui} body{background:#070707;color:#fff;min-height:100vh}
.login-bg{background:radial-gradient(circle at 50% 0%,rgba(0,150,176,0.25),transparent 50%),#070707;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:14px}
.login-card{background:#121212;border:1px solid rgba(0,150,176,0.3);border-radius:20px;padding:24px;width:100%;max-width:380px}
.logo{width:64px;height:64px;background:#0096B0;border-radius:14px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:26px;margin:0 auto 12px}
input{width:100%;background:#000;border:1px solid #333;padding:12px;border-radius:10px;color:#fff;margin:6px 0}
.btn{background:#0096B0;color:#fff;border:none;padding:13px;border-radius:10px;font-weight:800;width:100%;margin-top:8px;cursor:pointer}
.check{ display:flex;gap:8px;align-items:flex-start;margin:12px 0;font-size:11px;color:#aaa }.check a{color:#0096B0}
.header{position:sticky;top:0;z-index:99;background:#000;border-bottom:2px solid #0096B0;padding:10px 14px;display:flex;align-items:center;gap:10px}
.container{padding:12px;max-width:700px;margin:0 auto}.card{background:#121212;border:1px solid rgba(0,150,176,0.18);border-radius:14px;padding:12px;margin-bottom:12px}
.branch-scroll{display:flex;gap:8px;overflow-x:auto}.pill{white-space:nowrap;padding:8px 12px;border-radius:20px;border:1px solid #333;background:#151515;font-size:12px;font-weight:700;cursor:pointer}
.pill.active{background:#0096B0;color:#fff}.cat-tabs{display:flex;gap:6px;overflow-x:auto;margin:8px 0}.cat{white-space:nowrap;padding:7px 11px;border-radius:20px;font-size:11px;font-weight:800;cursor:pointer}
.products{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.prod{background:#1a1a1a;border:1px solid #222;border-radius:12px;padding:10px;cursor:pointer}.price{color:#0096B0;font-weight:800}
.footer-links{text-align:center;padding:18px;font-size:10px;color:#555}.footer-links a{color:#555;margin:0 6px;text-decoration:none}
</style></head><body>

<div id="loginPage" class="login-bg">
<div class="login-card">
<div class="logo">LO</div>
<div style="text-align:center"><div style="font-weight:800;letter-spacing:3px">LONMA ORBIT</div><div style="color:#0096B0;font-size:9px;letter-spacing:3px;margin-top:3px">SUPERCHAIN OS</div></div>

<input id="user" placeholder="Username"><input id="pass" type="password" placeholder="Password">
<div class="check"><input type="checkbox" id="agree" style="width:16px;height:16px;margin:0"><label for="agree">I agree to <a href="/terms" target="_blank">Terms & Conditions</a> and <a href="/terms" target="_blank">Privacy Policy</a> under Kenya DPA 2019. I am 18+ and responsible for sales under my login.</label></div>
<div id="err" style="color:#ff4444;font-size:12px;display:none;margin-bottom:6px"></div>
<button class="btn" onclick="doLogin()">LOGIN & ACCEPT TERMS →</button>

<div style="background:#000;border:1px dashed #333;border-radius:10px;padding:10px;margin-top:12px;font-size:11px;color:#888">
<b style="color:#0096B0">DEMO LOGINS:</b><br>
<div onclick="fill('admin','Lonma@2026')" style="cursor:pointer;padding:5px 0">👑 admin / Lonma@2026 - All branches</div>
<div onclick="fill('cashier1','1234')" style="cursor:pointer;padding:5px 0">💰 cashier1 / 1234</div>
</div>

<div class="footer-links"><a href="/terms">Terms & Conditions</a> • <a href="/terms">Privacy Policy</a> • <a href="/terms">KRA Compliance</a><br>© 2026 LO LONMA ORBIT • Nairobi, Kenya</div>
</div>
</div>

<div id="mainPage" style="display:none">
<div class="header"><div class="logo" style="width:40px;height:40px;font-size:16px">LO</div><div><div style="font-weight:800;font-size:12px;letter-spacing:2px" id="curName">Loading</div><div style="color:#0096B0;font-size:9px" id="userInfo"></div></div><div style="margin-left:auto;display:flex;gap:8px"><a href="/terms" target="_blank" style="color:#555;font-size:10px;text-decoration:none;border:1px solid #222;padding:6px 10px;border-radius:20px">T&C</a><button onclick="logout()" style="background:#111;border:1px solid #333;color:#888;padding:6px 10px;border-radius:20px;font-size:10px">Logout</button></div></div>
<div class="container">
<div class="card"><small style="color:#0096B0;font-weight:800;font-size:9px;letter-spacing:2px">BRANCHES</small><div class="branch-scroll" id="branchList" style="margin-top:6px"></div></div>
<div class="card" style="display:flex;justify-content:space-between;text-align:center"><div><small style="color:#888">STOCK</small><div id="stockValue" style="color:#0096B0;font-weight:800">0</div></div><div><small style="color:#888">SALES</small><div id="todaySales" style="color:#FFD700;font-weight:800">0</div></div><div><small style="color:#888">ITEMS</small><div id="prodCount" style="font-weight:800">0</div></div></div>
<div class="card"><small style="color:#0096B0;font-weight:800;font-size:9px">CATEGORIES</small><div class="cat-tabs"><div class="cat active" style="background:#fff;color:#000" id="tab-ALL" onclick="filterCat('ALL')">ALL</div><div class="cat" style="background:#FF9800" id="tab-FOOD" onclick="filterCat('FOOD')">FOOD</div><div class="cat" style="background:#0096B0;color:#fff" id="tab-DRINKS" onclick="filterCat('DRINKS')">DRINKS</div><div class="cat" style="background:#9C27B0;color:#fff" id="tab-UTENSILS" onclick="filterCat('UTENSILS')">UTENSILS</div><div class="cat" style="background:#FFD700" id="tab-ELECTRONICS" onclick="filterCat('ELECTRONICS')">ELECTRONICS</div></div><input id="search" placeholder="🔍 Search..." onkeyup="renderProducts()"><div class="products" id="plist" style="margin-top:8px"></div></div>
<div class="card"><b>🛒 CART - <span id="cartBranch" style="color:#0096B0"></span></b><div id="cart" style="margin-top:8px;color:#666;font-size:13px">Empty</div><div style="display:flex;justify-content:space-between;margin-top:10px;border-top:1px solid #222;padding-top:8px"><b>TOTAL</b><b id="total" style="color:#0096B0;font-size:18px">KES 0</b></div><button class="btn" onclick="checkout()">CHECKOUT</button></div>
<div class="card"><small style="color:#888;font-size:10px">By checking out you agree to <a href="/terms" style="color:#0096B0">Terms</a>. Receipt generated per Kenya law.</small></div>
<div class="footer-links"><a href="/terms">Terms & Conditions</a> • <a href="/terms">Privacy Policy</a> • © 2026 LONMA ORBIT</div>
</div>
</div>

<script>
let current='lonma-westlands'; let branches={}; let cart=[]; let activeCat='ALL'; let me=null;
function fill(u,p){document.getElementById('user').value=u; document.getElementById('pass').value=p;}
async function doLogin(){
  let u=document.getElementById('user').value; let p=document.getElementById('pass').value; let agree=document.getElementById('agree').checked;
  if(!agree){document.getElementById('err').style.display='block'; document.getElementById('err').innerText='⚠️ You must accept Terms & Conditions'; return}
  if(!u||!p){document.getElementById('err').style.display='block'; document.getElementById('err').innerText='Enter username & password'; return}
  let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  if(!r.ok){document.getElementById('err').style.display='block'; document.getElementById('err').innerText='❌ Wrong credentials'; return}
  me=await r.json(); me.acceptedTerms=true; me.acceptedAt=new Date().toISOString(); localStorage.setItem('lonma_user',JSON.stringify(me)); showMain();
}
function showMain(){document.getElementById('loginPage').style.display='none'; document.getElementById('mainPage').style.display='block'; document.getElementById('userInfo').innerText=me.name+' • '+me.role+' • T&C Accepted'; loadBranches();}
function logout(){localStorage.removeItem('lonma_user'); location.reload();}
(function(){let s=localStorage.getItem('lonma_user'); if(s){let u=JSON.parse(s); if(u.acceptedTerms){me=u; showMain();}}})();
async function loadBranches(){
  let r=await fetch('/api/supermarkets'); branches=await r.json();
  let tot=0; Object.values(branches).forEach(b=>b.products.forEach(p=>tot+=p.price*p.stock)); document.getElementById('stockValue').innerText='KES '+tot.toLocaleString();
  let list=Object.entries(branches); if(me.branch!='all') list=list.filter(([id])=>id==me.branch);
  document.getElementById('branchList').innerHTML=list.map(([id,b])=>`<div class="pill ${id==current?'active':''}" onclick="selectBranch('${id}')">${b.name}</div>`).join('');
  let b=branches[current]; document.getElementById('curName').innerText=b.name; document.getElementById('cartBranch').innerText=b.name; document.getElementById('prodCount').innerText=b.products.length; renderProducts(); loadSales();
}
function selectBranch(id){current=id; cart=[]; renderCart(); loadBranches();}
function filterCat(c){activeCat=c; document.querySelectorAll('.cat').forEach(x=>x.classList.remove('active')); document.getElementById('tab-'+c).classList.add('active'); renderProducts();}
function renderProducts(){let b=branches[current]; if(!b) return; let q=document.getElementById('search').value.toLowerCase(); let list=b.products.filter(p=>(activeCat=='ALL'||p.cat==activeCat)&&p.name.toLowerCase().includes(q)); let col={"FOOD":"#FF9800","DRINKS":"#0096B0","UTENSILS":"#9C27B0","ELECTRONICS":"#FFD700"}; document.getElementById('plist').innerHTML=list.map(p=>`<div class="prod" onclick="addCart('${p.id}')"><small style="background:${col[p.cat]};color:#000;padding:2px 5px;border-radius:5px;font-size:8px;font-weight:900">${p.cat}</small><div style="font-weight:700;margin-top:5px;font-size:12px">${p.name}</div><div class="price">KES ${p.price}</div></div>`).join('');}
function addCart(pid){let p=branches[current].products.find(x=>x.id==pid); let c=cart.find(x=>x.product_id==pid); if(c) c.qty++; else cart.push({product_id:pid,qty:1,name:p.name,price:p.price,cat:p.cat}); renderCart();}
function renderCart(){if(cart.length==0){document.getElementById('cart').innerHTML='Empty'; document.getElementById('total').innerText='KES 0'; return} let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #222"><span>${i.name} x${i.qty}</span><span style="color:#0096B0">KES ${i.price*i.qty}</span></div>`}).join(''); document.getElementById('total').innerText='KES '+total.toLocaleString();}
async function checkout(){if(cart.length==0) return alert('Empty'); if(!confirm('Confirm sale per Terms & Conditions?\\nReceipt will be generated.\\nBy checking out you agree to T&C.')) return; let r=await fetch(`/api/${current}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart)}); let d=await r.json(); alert('✅ SALE SUCCESS\\n'+d.receipt+' KES '+d.total+'\\nCashier: '+me.name+'\\nBranch: '+branches[current].name+'\\n\\nT&C Accepted'); cart=[]; renderCart(); loadBranches();}
async function loadSales(){let r=await fetch(`/api/${current}/sales`); let s=await r.json(); let tot=s.reduce((a,b)=>a+b.total,0); let el=document.getElementById('todaySales'); if(el) el.innerText='KES '+tot.toLocaleString();}
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
