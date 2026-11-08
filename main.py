from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, sqlite3, json, datetime, requests, base64
from threading import Thread
import time

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DARAJA_KEY = os.getenv("DARAJA_KEY",""); DARAJA_SECRET=os.getenv("DARAJA_SECRET","")
DARAJA_SHORTCODE=os.getenv("DARAJA_SHORTCODE","174379"); DARAJA_PASSKEY=os.getenv("DARAJA_PASSKEY","")
DARAJA_CALLBACK=os.getenv("CALLBACK_URL","https://app.lonmaorbit.co.ke/mpesa/callback")
USE_PROD=os.getenv("DARAJA_ENV","sandbox")=="production"

conn=sqlite3.connect("lonma.db",check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, code TEXT, image TEXT, category TEXT, stock INTEGER)")
conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, order_no TEXT, name TEXT, phone TEXT, area TEXT, location TEXT, items TEXT, total INTEGER, status TEXT, created TEXT, mpesa_receipt TEXT, checkout_id TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE, name TEXT, password TEXT)")
cur=conn.cursor(); cur.execute("DELETE FROM products")
PRODS=[
(1,"Diva Anti-Dandruff Pomade 250ml",250,"DIV-001","p1.jpg","Pomades",45),
(2,"Detrex Pine Drops Soap 110g",95,"DET-002","p2.jpg","Soaps",80),
(3,"Fresh Fri Cooking Oil 2L",890,"FRE-003","p3.jpg","Cooking Oils",50),
(4,"Detrex Citronella Soap 110g",95,"DET-004","p4.jpg","Soaps",100),
(5,"Sawa Men Lotion 72Hrs",320,"SAW-005","p5.jpg","Lotions",12),
(6,"Detrex Cool Mint Soap 110g",95,"DET-006","p6.jpg","Soaps",4),
(7,"Diva Anti-Breakage Pomade 250ml",250,"DIV-007","p7.jpg","Pomades",30),
(8,"Sawa Cocoa Butter Lotion 72Hrs",320,"SAW-008","p8.jpg","Lotions",28),
(9,"Detrex Germ Protection Soap 110g",95,"DET-009","p9.jpg","Soaps",60),
]
for pid,name,price,code,img,cat,stock in PRODS:
    cur.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?)",(pid,name,price,code,img,cat,stock))
conn.commit()

def get_token():
    try:
        base="https://api.safaricom.co.ke" if USE_PROD else "https://sandbox.safaricom.co.ke"
        r=requests.get(f"{base}/oauth/v1/generate?grant_type=client_credentials",auth=(DARAJA_KEY,DARAJA_SECRET),timeout=10)
        return r.json().get("access_token")
    except: return None

@app.api_route("/mpesa/callback",methods=["GET","POST"])
async def callback(request:Request):
    try:
        data=await request.json()
        stk=data.get("Body",{}).get("stkCallback",{})
        if stk.get("ResultCode")==0:
            receipt=""
            for it in stk.get("CallbackMetadata",{}).get("Item",[]):
                if it.get("Name")=="MpesaReceiptNumber": receipt=it.get("Value")
            conn.execute("UPDATE orders SET status='PAID', mpesa_receipt=? WHERE checkout_id=?",(receipt,stk.get("CheckoutRequestID","")))
            conn.commit()
        return {"ResultCode":0,"ResultDesc":"Accepted"}
    except: return {"ResultCode":0,"ResultDesc":"Accepted"}

@app.get("/api/products")
def prods_api():
    cur=conn.cursor(); cur.execute("SELECT id,name,price,code,image,category,stock FROM products")
    return [{"id":r[0],"name":r[1],"price":r[2],"code":r[3],"image":f"/images/{r[4]}","category":r[5],"stock":r[6]} for r in cur.fetchall()]

@app.get("/images/{name}")
def serve_img(name:str):
    for p in [f"images/{name}", name, f"./images/{name}"]:
        if os.path.exists(p): return FileResponse(p)
    return FileResponse("images/p1.jpg") if os.path.exists("images/p1.jpg") else HTMLResponse("",404)

@app.get("/api/verify/{code}")
def verify(code:str):
    cur=conn.cursor(); cur.execute("SELECT name FROM products WHERE code=?",(code.upper(),))
    row=cur.fetchone(); return {"valid":True,"product":{"name":row[0]}} if row else {"valid":False}

@app.get("/api/orders")
def orders_api(phone:str=""):
    cur=conn.cursor()
    if phone: cur.execute("SELECT order_no,name,total,status,created FROM orders WHERE phone=? ORDER BY id DESC",(phone,))
    else: cur.execute("SELECT order_no,name,total,status,created FROM orders ORDER BY id DESC LIMIT 50")
    return [{"order_no":r[0],"name":r[1],"total":r[2],"status":r[3],"created":r[4]} for r in cur.fetchall()]

@app.get("/api/admin/orders")
def admin_orders():
    cur=conn.cursor(); cur.execute("SELECT order_no,name,phone,total,status,created FROM orders ORDER BY id DESC")
    return [{"order_no":r[0],"name":r[1],"phone":r[2],"total":r[3],"status":r[4],"created":r[5]} for r in cur.fetchall()]

@app.post("/mpesa/stkpush")
async def stk(req:Request):
    d=await req.json()
    raw=d.get('phone','').strip(); phone=raw.replace(" ","").replace("+254","0")
    if phone.startswith("0"): phone="254"+phone[1:]
    phone="".join([c for c in phone if c.isdigit()]); amount=int(d.get('amount',1))
    order_no='LONMA'+datetime.datetime.now().strftime("%H%M%S")
    conn.execute("INSERT INTO orders (order_no,name,phone,area,location,items,total,status,created,mpesa_receipt,checkout_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(order_no,d.get('name','Guest'),raw,d.get('area'),d.get('location'),json.dumps(d.get('cart',[])),amount,'Pending',datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"",order_no))
    conn.commit()
    if DARAJA_KEY and DARAJA_PASSKEY:
        token=get_token()
        if token:
            ts=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            pwd=base64.b64encode(f"{DARAJA_SHORTCODE}{DARAJA_PASSKEY}{ts}".encode()).decode()
            payload={"BusinessShortCode":DARAJA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":amount,"PartyA":phone,"PartyB":DARAJA_SHORTCODE,"PhoneNumber":phone,"CallBackURL":DARAJA_CALLBACK,"AccountReference":order_no,"TransactionDesc":order_no}
            try:
                base="https://api.safaricom.co.ke" if USE_PROD else "https://sandbox.safaricom.co.ke"
                r=requests.post(f"{base}/mpesa/stkpush/v1/processrequest",json=payload,headers={"Authorization":f"Bearer {token}"},timeout=15)
                res=r.json()
                if res.get("ResponseCode")=="0":
                    conn.execute("UPDATE orders SET checkout_id=? WHERE order_no=?",(res.get("CheckoutRequestID",order_no),order_no)); conn.commit()
                    return {"status":"ok","message":f"STK sent to {raw}","order_no":order_no}
            except: pass
    return {"status":"ok","message":f"Order {order_no} saved","order_no":order_no}

@app.post("/api/auth/register")
async def reg(req:Request):
    d=await req.json(); phone=d.get("phone","").strip(); name=d.get("name","").strip(); pwd=d.get("password","").strip()
    cur=conn.cursor(); cur.execute("SELECT id FROM users WHERE phone=?",(phone,)); 
    if cur.fetchone(): return {"status":"error","message":"Exists"}
    cur.execute("INSERT INTO users (phone,name,password) VALUES (?,?,?)",(phone,name,pwd)); conn.commit()
    return {"status":"ok","user":{"phone":phone,"name":name}}

@app.post("/api/auth/login")
async def log(req:Request):
    d=await req.json(); cur=conn.cursor(); cur.execute("SELECT phone,name FROM users WHERE phone=? AND password=?",(d.get("phone","").strip(),d.get("password","").strip()))
    row=cur.fetchone(); return {"status":"ok","user":{"phone":row[0],"name":row[1]}} if row else {"status":"error","message":"Wrong"}

HTML="""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT</title><style>
:root{--teal:#0A9EBB;--dark:#0f172a;--line:#e2e8f0}*{box-sizing:border-box}body{margin:0;font-family:Inter,-apple-system,Arial;background:#f8fafc;color:var(--dark)}
.nav{position:fixed;top:0;width:100%;background:#fff;z-index:1000;border-bottom:1px solid var(--line)}.nav-top{padding:12px 16px;display:flex;justify-content:space-between;align-items:center;height:64px}
.logo{display:flex;align-items:center;gap:10px;cursor:pointer}.logo img{width:38px;height:38px;border-radius:50%}.logo b{font-size:16px;letter-spacing:.5px}
.cart-pill{background:var(--dark);color:#fff;padding:8px 16px;border-radius:30px;font-weight:800;font-size:12px;cursor:pointer;position:relative}
.cart-num{position:absolute;top:-6px;right:-6px;background:var(--teal);color:#fff;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:11px}
.search-wrap{padding:0 16px 12px}.search-box{background:#f1f5f9;border-radius:30px;height:44px;display:flex;align-items:center;gap:12px;padding:0 16px;border:1px solid var(--line)}
.search-box input{border:none;outline:none;background:transparent;flex:1;font-size:14px}.burger{font-size:22px;cursor:pointer}
.cat-chips{display:flex;gap:8px;overflow-x:auto;padding:0 16px 12px;scrollbar-width:none}.chip{white-space:nowrap;padding:8px 16px;border-radius:20px;background:#fff;border:1px solid var(--line);font-size:12px;font-weight:700;cursor:pointer}.chip.active{background:var(--dark);color:#fff}
.page{display:none;padding:168px 14px 90px;max-width:480px;margin:0 auto}.page.active{display:block}
.banner{background:linear-gradient(135deg,#0A9EBB 0%,#0f172a 100%);color:#fff;border-radius:20px;padding:16px 18px;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.card{background:#fff;border-radius:20px;padding:12px;margin:10px 0;border:1px solid #f1f5f9;box-shadow:0 4px 16px rgba(15,23,42,.04);display:flex;gap:12px}
.card img{width:90px;height:90px;object-fit:contain;border-radius:14px;background:#f8fafc;flex-shrink:0}
.btn{background:var(--dark);color:#fff;border:none;padding:14px;border-radius:30px;width:100%;font-weight:800;cursor:pointer}.btn-teal{background:var(--teal)}
input,select,textarea{width:100%;padding:14px;border-radius:14px;border:1px solid var(--line);margin:6px 0;font-size:14px;background:#fff}
.bottom{position:fixed;bottom:0;width:100%;background:#fff;border-top:1px solid var(--line);display:flex;justify-content:space-around;padding:10px 0;z-index:1000}
.bottom div{font-size:11px;text-align:center;flex:1;cursor:pointer;color:#94a3b8}.bottom div.active{color:var(--dark);font-weight:800}
.side{position:fixed;top:0;left:-320px;width:300px;height:100%;background:#fff;z-index:2000;transition:.35s;box-shadow:20px 0 60px rgba(0,0,0,.12)}.side.open{left:0}.overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(15,23,42,.4);z-index:1999}.overlay.open{display:block}
.top-box{background:var(--dark);padding:28px 20px;color:#fff;text-align:center}.lc{width:70px;height:70px;background:#fff;border-radius:50%;margin:0 auto;display:flex;align-items:center;justify-content:center}.lc img{width:66px;height:66px;border-radius:50%}
.menu{padding:12px 0}.mi{display:flex;align-items:center;gap:14px;padding:15px 20px;cursor:pointer}.mi:hover{background:#f8fafc}.mi b{font-size:14px;font-weight:600;flex:1}.ico{width:38px;height:38px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:17px}.tag{font-size:11px;font-weight:800;padding:5px 10px;border-radius:20px}.div{height:1px;background:#f1f5f9;margin:8px 20px}.label{font-size:10px;font-weight:800;letter-spacing:.2em;color:#94a3b8;padding:14px 20px 6px}
</style></head><body>
<div class="nav"><div class="nav-top"><div class="logo" onclick="show('products')"><img src="/logo.png"><b>LONMA ORBIT</b></div><div class="cart-pill" onclick="show('cart')">CART <span id="cartCount" class="cart-num" style="display:none">0</span></div></div><div class="search-wrap"><div class="search-box"><span class="burger" onclick="openMenu()">☰</span><input id="searchInput" placeholder="Search Diva, Detrex, Sawa..." oninput="filterProducts()"></div></div><div class="cat-chips"><div class="chip active" onclick="filterCat('All',this)">All</div><div class="chip" onclick="filterCat('Soaps',this)">Soaps</div><div class="chip" onclick="filterCat('Lotions',this)">Lotions</div><div class="chip" onclick="filterCat('Pomades',this)">Pomades</div><div class="chip" onclick="filterCat('Cooking Oils',this)">Oils</div></div></div>
<div class="overlay" id="overlay" onclick="closeMenu()"></div>
<div class="side" id="side"><div class="top-box"><div style="text-align:right"><span style="background:rgba(255,255,255,.15);padding:6px 14px;border-radius:20px;font-size:11px;font-weight:700;cursor:pointer" onclick="show('cart');closeMenu()">VIEW CART</span></div><div class="lc" onclick="show('products');closeMenu()"><img src="/logo.png"></div><div style="font-weight:800;font-size:19px;margin-top:12px">LONMA ORBIT</div><div style="opacity:.8;font-size:12px;margin-top:4px">100% Genuine • Fast Delivery</div></div><div class="menu"><div class="label">SHOP</div><div class="mi" onclick="show('products');closeMenu()"><div class="ico" style="background:#f0fdfa">🏠</div><b>Home • Products</b><span class="tag" style="background:var(--teal);color:#fff">NEW</span></div><div class="mi" onclick="show('cart');closeMenu()"><div class="ico" style="background:#fef3c7">🛒</div><b>Cart</b><span class="tag" style="background:#f1f5f9" id="mc">0</span></div><div class="mi" onclick="show('orders');closeMenu()"><div class="ico" style="background:#dbeafe">📦</div><b>Orders</b></div><div class="div"></div><div class="label">SUPPORT</div><div class="mi" onclick="show('scan');closeMenu()"><div class="ico" style="background:#dcfce7">🛡️</div><b>Verify Product</b></div><div class="mi" onclick="show('account');closeMenu()"><div class="ico" style="background:#f1f5f9">👤</div><b>My Account</b></div><div class="mi" onclick="show('terms');closeMenu()"><div class="ico" style="background:#fef3c7">📄</div><b>Terms</b></div><div class="div"></div><div class="mi" onclick="show('admin');closeMenu()" style="opacity:.6"><div class="ico" style="background:#0f172a;color:#fff">🔐</div><b>Admin</b></div><div style="text-align:center;padding:18px;color:#94a3b8;font-size:11px">v5.0 Real Images • 🇰🇪</div></div></div>
<div id="products" class="page active"><div class="banner"><div><div style="font-weight:800;font-size:15px">FREE Delivery</div><div style="font-size:12px;opacity:.9">Orders over KSh 2000</div></div><div style="background:#fff;color:var(--dark);padding:6px 14px;border-radius:20px;font-weight:800;font-size:12px">SHOP NOW</div></div><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><h3 style="margin:0">Products</h3><span style="font-size:12px;color:#64748b" id="pCount">9 items</span></div><div id="plist"></div></div>
<div id="cart" class="page"><h3>Cart</h3><div id="cartItems"></div><div id="cartSum" style="display:none"><div class="card" style="display:block"><div style="display:flex;justify-content:space-between"><span>Subtotal (<span id="tItems">0</span>)</span><b>KSh <span id="sub">0</span></b></div><div style="display:flex;justify-content:space-between;margin-top:8px"><span>Delivery</span><b id="delFee"></b></div><div style="display:flex;justify-content:space-between;margin-top:12px;font-size:18px;border-top:1px solid #f1f5f9;padding-top:12px"><span>Total</span><b>KSh <span id="tot">0</span></b></div><div style="margin-top:16px"><input id="custName" placeholder="Full Name"><input id="phone" placeholder="M-Pesa 07..."><select id="area"><option value="">Select Area</option><option value="CBD">CBD - 150</option><option value="Westlands">Westlands - 200</option><option value="Upcountry">Upcountry - 350</option></select><textarea id="loc" placeholder="Exact location / building"></textarea><label style="font-size:12px;display:flex;gap:8px;align-items:center;margin:12px 0"><input type="checkbox" id="agree" style="width:auto"> I agree to <a href="#" onclick="show('terms');return false" style="color:#0A9EBB;font-weight:800">Terms</a></label></div><button class="btn" onclick="checkout()">Pay KSh <span id="pay">0</span> with M-Pesa</button><p id="ps" style="text-align:center;font-size:13px"></p></div></div><div id="emptyCart" class="card" style="text-align:center;padding:30px;display:block"><div style="font-size:40px">🛒</div><h4>Your cart is empty</h4><button class="btn btn-teal" onclick="show('products')">Start Shopping</button></div></div>
<div id="orders" class="page"><h3>Orders</h3><div style="display:flex;gap:8px;margin-bottom:12px"><input id="phLookup" placeholder="Enter phone 07..."><button class="btn" style="width:auto;padding:10px 20px" onclick="loadOrders()">Load</button></div><div id="olist"></div><div id="noOrd" class="card" style="text-align:center;display:block"><p>No orders yet</p></div></div>
<div id="scan" class="page"><h3>Verify Authenticity</h3><div class="card" style="display:block;padding:20px;text-align:center"><div style="font-size:40px">🛡️</div><h4>Check Product</h4><p style="font-size:12px;color:#64748b">Enter code like DIV-001</p><input id="vcode" placeholder="DIV-001"><button class="btn btn-teal" onclick="verify()" style="margin-top:10px">Verify Now</button><p id="vres" style="font-weight:700;margin-top:12px"></p></div></div>
<div id="account" class="page"><div id="out"><div class="card" style="display:block"><h4>Create Account</h4><input id="rn" placeholder="Full name"><input id="rp" placeholder="07xxxxxxxx"><input id="rpass" type="password" placeholder="Password"><button class="btn" onclick="register()">Create Account</button><p id="rs"></p></div><div class="card" style="display:block"><h4>Sign In</h4><input id="lp" placeholder="07xxxxxxxx"><input id="lpass" type="password" placeholder="Password"><button class="btn" style="background:var(--teal)" onclick="login()">Sign In</button><p id="ls"></p></div></div><div id="in" style="display:none"><div class="card" style="display:block;background:var(--dark);color:#fff;text-align:center;padding:24px"><h3 id="an" style="margin:12px 0 4px">Welcome</h3><p id="ap" style="opacity:.7;font-size:13px"></p><button class="btn" style="background:#fff;color:var(--dark);margin-top:16px" onclick="logout()">Sign Out</button></div></div></div>
<div id="terms" class="page"><h3>Terms & Conditions</h3><div class="card" style="display:block;line-height:1.7;font-size:13px;padding:18px"><h4>1. Delivery</h4><p>CBD KSh 150, Westlands KSh 200, Upcountry KSh 350. FREE for orders KSh 2000+.</p><h4>2. Payments</h4><p>All payments via M-Pesa STK Push. Order confirmed after receipt.</p><h4>3. Authenticity</h4><p>100% genuine Pwani products. Verify code.</p><h4>4. Returns</h4><p>Returns within 24hrs if unopened with receipt.</p><p style="margin-top:16px;font-size:11px;color:#94a3b8">v5.0 • Made in Kenya 🇰🇪</p><button class="btn" style="margin-top:14px" onclick="show('cart')">Back to Cart</button></div></div>
<div id="admin" class="page"><h3>Admin</h3><div class="card" style="display:block"><input id="apass" type="password" placeholder="Password"><button class="btn" onclick="adminLogin()">Login</button><p id="ast"></p></div><div id="acont" style="display:none"><div id="alist"></div></div></div>
<div id="receipt" class="page"><div class="card" style="display:block;text-align:center;padding:24px" id="rcont"></div><button class="btn" onclick="show('products')">Continue Shopping</button></div>
<div class="bottom"><div id="b-products" class="active" onclick="show('products')">🏠<br>Home</div><div id="b-cart" onclick="show('cart')">🛒<br>Cart</div><div id="b-orders" onclick="show('orders')">📦<br>Orders</div><div id="b-account" onclick="show('account')">👤<br>Account</div></div>
<script>
let all=[],cart=[],myOrders=JSON.parse(localStorage.getItem('my_orders')||'[]'),activeCat='All';
try{let s=localStorage.getItem('lonma_cart');if(s)cart=JSON.parse(s);}catch(e){cart=[];}
function save(){localStorage.setItem('lonma_cart',JSON.stringify(cart));updateCount();}
function updateCount(){let c=0;for(let i of cart)c+=i.qty;let el=document.getElementById('cartCount');if(el){el.innerText=c;el.style.display=c>0?'flex':'none';}document.getElementById('mc').innerText=c;}
function openMenu(){document.getElementById('side').classList.add('open');document.getElementById('overlay').classList.add('open');}
function closeMenu(){document.getElementById('side').classList.remove('open');document.getElementById('overlay').classList.remove('open');}
function filterCat(cat,el){activeCat=cat;document.querySelectorAll('.chip').forEach(c=>c.classList.remove('active'));el.classList.add('active');filterProducts();}
function filterProducts(){let q=document.getElementById('searchInput').value.toLowerCase();let f=all.filter(p=>{let matchCat=activeCat==='All'||p.category===activeCat;let matchSearch=!q||p.name.toLowerCase().includes(q);return matchCat&&matchSearch;});render(f);}
function render(list){let h='';for(let p of list){let inC=cart.find(c=>c.id===p.id);let low=p.stock<=8?`<span style="color:#ef4444;font-size:10px;font-weight:800;background:#fef2f2;padding:3px 8px;border-radius:20px;margin-left:6px">Only ${p.stock} left!</span>`:'';h+=`<div class="card"><img src="${p.image}" onerror="this.src='https://via.placeholder.com/200?text=No+Image'"><div style="flex:1"><div style="font-weight:700;font-size:13px;line-height:1.3">${p.name}${low}</div><div style="font-size:11px;color:#94a3b8;margin-top:4px">${p.category} • ${p.code}</div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px"><b style="font-size:16px">KSh ${p.price}</b><button class="btn" style="width:auto;padding:8px 18px;border-radius:20px;font-size:12px" onclick="add(${p.id})">${inC?'✓ '+inC.qty:'Add'}</button></div></div></div>`;}document.getElementById('plist').innerHTML=h||'<div class="card" style="display:block;text-align:center">No products found</div>';document.getElementById('pCount').innerText=list.length+' items';}
function add(id){let p=all.find(x=>x.id===id);let f=cart.find(c=>c.id===id);if(f)f.qty++;else cart.push({id:p.id,name:p.name,price:p.price,image:p.image,qty:1});save();filterProducts();}
function renderCart(){let cont=document.getElementById('cartItems'),sum=document.getElementById('cartSum'),empty=document.getElementById('emptyCart');if(cart.length===0){cont.innerHTML='';sum.style.display='none';empty.style.display='block';return;}empty.style.display='none';sum.style.display='block';let sub=0,items=0,html='';for(let it of cart){sub+=it.price*it.qty;items+=it.qty;html+=`<div class="card"><img src="${it.image}" style="width:60px;height:60px"><div style="flex:1"><b style="font-size:13px">${it.name}</b><div style="display:flex;gap:8px;align-items:center;margin-top:6px"><button onclick="chg(${it.id},-1)" style="width:28px;height:28px;border-radius:50%;border:1px solid #e2e8f0;background:#fff">-</button><span>${it.qty}</span><button onclick="chg(${it.id},1)" style="width:28px;height:28px;border-radius:50%;border:1px solid #e2e8f0;background:#fff">+</button><span style="margin-left:auto;font-weight:800">KSh ${it.price*it.qty}</span></div></div></div>`;}cont.innerHTML=html;let area=document.getElementById('area').value;let del=area==='CBD'?150:area==='Upcountry'?350:200;if(sub>=2000)del=0;let tot=sub+del;document.getElementById('sub').innerText=sub;document.getElementById('tItems').innerText=items;document.getElementById('delFee').innerText=del==0?'FREE':'KSh '+del;document.getElementById('tot').innerText=tot;document.getElementById('pay').innerText=tot;}
function chg(id,d){let f=cart.find(c=>c.id===id);if(!f)return;f.qty+=d;if(f.qty<=0)cart=cart.filter(c=>c.id!==id);save();renderCart();}
function show(id){document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('.bottom div').forEach(b=>b.classList.remove('active'));let btn=document.getElementById('b-'+id);if(btn)btn.classList.add('active');if(id==='cart')renderCart();closeMenu();window.scrollTo(0,0);}
async function loadP(){let r=await fetch('/api/products');all=await r.json();render(all);}
async function verify(){let c=document.getElementById('vcode').value.trim();let r=await fetch('/api/verify/'+c);let d=await r.json();document.getElementById('vres').innerText=d.valid?'✅ Authentic: '+d.product.name:'❌ Invalid Code';}
async function checkout(){let name=document.getElementById('custName').value.trim(),phone=document.getElementById('phone').value.trim(),area=document.getElementById('area').value,loc=document.getElementById('loc').value.trim();if(!name||!phone||!area||!loc||!document.getElementById('agree').checked){document.getElementById('ps').innerText='Fill all fields + agree to Terms';return;}let sub=0;for(let i of cart)sub+=i.price*i.qty;let del=area==='CBD'?150:area==='Upcountry'?350:200;if(sub>=2000)del=0;let tot=sub+del;document.getElementById('ps').innerText='Sending M-Pesa prompt...';let r=await fetch('/mpesa/stkpush',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone,amount:tot,cart,name,area,location:loc})});let d=await r.json();document.getElementById('ps').innerText=d.message;if(d.status==='ok'){myOrders.unshift({order_no:d.order_no,total:tot,status:'Pending',created:new Date().toLocaleString()});localStorage.setItem('my_orders',JSON.stringify(myOrders));document.getElementById('rcont').innerHTML=`<div style="font-size:50px">✅</div><h3>${d.order_no}</h3><p>Total KSh ${tot}</p><p style="font-size:12px;color:#64748b">Check phone for M-Pesa prompt</p>`;cart=[];localStorage.removeItem('lonma_cart');save();show('receipt');}}
async function loadOrders(){let ph=document.getElementById('phLookup').value.trim();let r=await fetch('/api/orders?phone='+ph);let data=await r.json();document.getElementById('olist').innerHTML=data.map(o=>`<div class="card" style="display:block"><div style="display:flex;justify-content:space-between"><b>${o.order_no}</b><span style="background:#f1f5f9;padding:4px 10px;border-radius:20px;font-size:11px">${o.status}</span></div><div style="margin-top:6px">KSh ${o.total} • ${o.created}</div></div>`).join('');document.getElementById('noOrd').style.display=data.length?'none':'block';}
async function adminLogin(){let p=document.getElementById('apass').value;if(p!=='lonma2024'){document.getElementById('ast').innerText='Wrong';return;}document.getElementById('acont').style.display='block';let r=await fetch('/api/admin/orders');let d=await r.json();document.getElementById('alist').innerHTML=d.map(o=>`<div class="card" style="display:block"><b>${o.order_no}</b> ${o.phone} - KSh ${o.total} - ${o.status}</div>`).join('');}
async function register(){let name=document.getElementById('rn').value.trim(),phone=document.getElementById('rp').value.trim(),pass=document.getElementById('rpass').value.trim();let r=await fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,phone,password:pass})});let d=await r.json();document.getElementById('rs').innerText=d.status==='ok'?'Created':'Error';if(d.status==='ok'){localStorage.setItem('lonma_user',JSON.stringify(d.user));show('products');}}
async function login(){let phone=document.getElementById('lp').value.trim(),pass=document.getElementById('lpass').value.trim();let r=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone,password:pass})});let d=await r.json();document.getElementById('ls').innerText=d.status==='ok'?'Welcome':'Wrong';if(d.status==='ok'){localStorage.setItem('lonma_user',JSON.stringify(d.user));show('products');}}
function logout(){localStorage.removeItem('lonma_user');show('account');}
document.getElementById('area')?.addEventListener('change',renderCart);
loadP();updateCount();
</script></body></html>
"""

@app.api_route("/",methods=["GET","HEAD"])
def home(): return HTMLResponse(HTML)
@app.get("/logo.png")
def logo():
    for f in ["logo.png","static/logo.png","./logo.png","images/logo.png"]:
        if os.path.exists(f): return FileResponse(f)
    return HTMLResponse("",200)

# keep-alive anti-sleep
def keep_alive():
    while True:
        time.sleep(500)
        try: requests.get("https://app.lonmaorbit.co.ke",timeout=5)
        except: pass
Thread(target=keep_alive, daemon=True).start()
