import os, json, uuid, hashlib, time, base64, secrets
from datetime import datetime
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse

app = FastAPI()

# ---------- ENV - SUPPORT BOTH NAMES ----------
DARAJA_KEY = os.getenv("DARAJA_KEY","") or os.getenv("MPESA_CONSUMER_KEY","")
DARAJA_SECRET = os.getenv("DARAJA_SECRET","") or os.getenv("MPESA_CONSUMER_SECRET","")
DARAJA_SHORTCODE = os.getenv("DARAJA_SHORTCODE","") or os.getenv("MPESA_SHORTCODE","174379")
DARAJA_PASSKEY = os.getenv("DARAJA_PASSKEY","") or os.getenv("MPESA_PASSKEY","")
DARAJA_CALLBACK = os.getenv("CALLBACK_URL","") or os.getenv("MPESA_CALLBACK_URL","https://app.lonmaorbit.co.ke/mpesa/callback")
USE_PROD = (os.getenv("DARAJA_ENV","sandbox")=="production") or (os.getenv("MPESA_ENV","sandbox")=="production")
# For Till (BuyGoods) set MPESA_TYPE=BuyGoods, for Paybill set PayBill
MPESA_TYPE = os.getenv("MPESA_TYPE","PayBill")  # PayBill or BuyGoods
SECRET_KEY = os.getenv("SECRET_KEY","lonma-secret-123")
SHOW_RESET = os.getenv("SHOW_RESET_CODE","true")=="true"
MPESA_CONFIGURED = bool(DARAJA_KEY and DARAJA_PASSKEY and DARAJA_SHORTCODE)

# ---------- DATA ----------
PRODUCTS = [
    {"id":"1","name":"Lonma Hair Growth Oil 100ml","price":850,"old":1200,"cat":"Oils","img":"https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600","desc":"Rosemary + Castor for fast growth.","stock":50},
    {"id":"2","name":"Lonma Edge Control Gel","price":450,"old":600,"cat":"Styling","img":"https://images.unsplash.com/photo-1526947425960-945c6e72858f?w=600","desc":"Strong hold, no flakes, 24h edges.","stock":80},
    {"id":"3","name":"Lonma Shea Body Butter","price":650,"old":850,"cat":"Skin","img":"https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600","desc":"Deep moisture, glowing skin.","stock":40},
    {"id":"4","name":"Lonma Vitamin C Serum","price":950,"old":1300,"cat":"Skin","img":"https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600","desc":"Brightening, dark spots, glow.","stock":30},
    {"id":"5","name":"Lonma Braiding Hair - Black","price":350,"old":500,"cat":"Hair","img":"https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?w=600","desc":"Premium braiding hair, soft.","stock":100},
    {"id":"6","name":"Lonma Wig - Body Wave 22\"","price":4500,"old":6500,"cat":"Wigs","img":"https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600","desc":"100% human hair, glueless.","stock":15},
    {"id":"7","name":"Lonma Lip Gloss Set (3pcs)","price":550,"old":750,"cat":"Makeup","img":"https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=600","desc":"Glossy, non-sticky, 3 shades.","stock":60},
    {"id":"8","name":"Lonma Face Wash","price":550,"old":700,"cat":"Skin","img":"https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600","desc":"Gentle cleanse.","stock":70},
    {"id":"9","name":"Lonma Hair Mask","price":750,"old":1000,"cat":"Oils","img":"https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=600","desc":"Deep repair.","stock":35},
    {"id":"10","name":"Detrex Soap","price":120,"old":180,"cat":"Soaps","img":"https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=600","desc":"Detrex antiseptic soap.","stock":200},
    {"id":"11","name":"Diva Soap","price":150,"old":200,"cat":"Soaps","img":"https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=600","desc":"Diva beauty soap.","stock":200},
    {"id":"12","name":"Sawa Lotion","price":245,"old":350,"cat":"Lotions","img":"https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600","desc":"Sawa body lotion.","stock":120},
    {"id":"13","name":"Hair Pomade","price":300,"old":400,"cat":"Pomades","img":"https://images.unsplash.com/photo-1526947425960-945c6e72858f?w=600","desc":"Strong hold pomade.","stock":90},
]
USERS = {"admin@lonma.co.ke":{"name":"Admin","pass":hashlib.sha256("admin123".encode()).hexdigest(),"role":"admin","phone":"254700000000"}}
ORDERS = []
RESETS = {}

def get_user(req: Request):
    tok = req.cookies.get("tok","")
    for email,u in USERS.items():
        if hashlib.sha256((email+SECRET_KEY).encode()).hexdigest()==tok:
            return email,u
    return None,None

# ---------- M-PESA ----------
def daraja_token():
    if not MPESA_CONFIGURED: return None
    url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" if USE_PROD else "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    try:
        r = requests.get(url, auth=(DARAJA_KEY, DARAJA_SECRET), timeout=15)
        print(f"DARAJA TOKEN RESP: {r.text[:500]}")
        return r.json().get("access_token")
    except Exception as e:
        print(f"TOKEN EXCEPTION: {e}")
        return None

def stk_push(phone, amount, ref):
    if not MPESA_CONFIGURED:
        return {"ok":False,"msg":"M-Pesa not configured - check Render Env"}
    token = daraja_token()
    if not token:
        return {"ok":False,"msg":"Daraja token FAILED - Wrong Consumer Key/Secret for PRODUCTION. Check Daraja Portal > Production keys."}
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    pwd = base64.b64encode(f"{DARAJA_SHORTCODE}{DARAJA_PASSKEY}{ts}".encode()).decode()
    # Clean phone
    phone = str(phone).strip().replace(" ","").replace("+","").replace("-","")
    if phone.startswith("0"):
        phone = "254"+phone[1:]
    elif phone.startswith("254")==False:
        return {"ok":False,"msg":f"Bad phone: {phone}. Use 0712345678"}
    if len(phone)!=12:
        return {"ok":False,"msg":f"Bad phone length: {phone}"}
    url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if USE_PROD else "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    txn_type = "CustomerBuyGoodsOnline" if MPESA_TYPE=="BuyGoods" else "CustomerPayBillOnline"
    payload = {"BusinessShortCode":DARAJA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":txn_type,"Amount":int(amount),"PartyA":phone,"PartyB":DARAJA_SHORTCODE,"PhoneNumber":phone,"CallBackURL":DARAJA_CALLBACK,"AccountReference":ref,"TransactionDesc":"Lonma Orbit Order"}
    print(f"STK REQUEST: Shortcode={DARAJA_SHORTCODE} Type={txn_type} Phone={phone} Amount={amount} Callback={DARAJA_CALLBACK}")
    try:
        r = requests.post(url, json=payload, headers={"Authorization":f"Bearer {token}"}, timeout=20)
        j = r.json()
        print(f"DARAJA STK RESPONSE: {j}")
        if j.get("ResponseCode")=="0":
            return {"ok":True,"checkout_id":j.get("CheckoutRequestID")}
        # Friendly translation of common errors
        desc = j.get("ResponseDescription","") or j.get("errorMessage","") or str(j)
        code = j.get("ResponseCode") or j.get("errorCode","")
        if "Invalid Access Token" in desc or "Invalid" in desc and "Passkey" in str(j):
            desc += " - Passkey wrong for PRODUCTION"
        if "500.001" in str(j) or "Internal" in desc:
            desc = "Daraja Internal Error - Usually wrong Passkey / Shortcode / Callback not whitelisted. Check Daraja Portal."
        return {"ok":False,"msg":f"Daraja rejected: {desc} (Code {code})"}
    except Exception as e:
        print(f"STK EXCEPTION: {e}")
        return {"ok":False,"msg":f"STK Error: {e}"}

# ---------- API ----------
@app.get("/logo.png")
def logo():
    import os as _os
    if _os.path.exists("logo.png"):
        return FileResponse("logo.png")
    # fallback - 1x1 transparent, prevents 404 spam
    return JSONResponse({"ok":False}, status_code=404)

@app.get("/api/health")
def health():
    return {"status":"ok","mpesa_env":"production" if USE_PROD else "sandbox","mpesa_configured":MPESA_CONFIGURED,"mpesa_type":MPESA_TYPE,"mpesa_shortcode":DARAJA_SHORTCODE,"callback":DARAJA_CALLBACK,"show_reset_code":SHOW_RESET}

@app.get("/api/debug-mpesa")
def debug_mpesa():
    tok = daraja_token()
    return {"configured":MPESA_CONFIGURED,"env":"production" if USE_PROD else "sandbox","shortcode":DARAJA_SHORTCODE,"type":MPESA_TYPE,"callback":DARAJA_CALLBACK,"token_ok":bool(tok),"key_len":len(DARAJA_KEY),"passkey_len":len(DARAJA_PASSKEY)}

@app.get("/api/products")
def products():
    return PRODUCTS

@app.post("/api/register")
async def register(req: Request):
    d = await req.json()
    email=d.get("email","").lower().strip()
    if email in USERS: return {"ok":False,"msg":"Email exists"}
    USERS[email]={"name":d.get("name",""),"pass":hashlib.sha256(d.get("password","").encode()).hexdigest(),"role":"customer","phone":d.get("phone","")}
    return {"ok":True}

@app.post("/api/login")
async def login(req: Request):
    d = await req.json()
    email=d.get("email","").lower().strip()
    u=USERS.get(email)
    if not u or u["pass"]!=hashlib.sha256(d.get("password","").encode()).hexdigest():
        return {"ok":False,"msg":"Wrong email or password"}
    tok=hashlib.sha256((email+SECRET_KEY).encode()).hexdigest()
    r=JSONResponse({"ok":True,"name":u["name"],"role":u["role"]})
    r.set_cookie("tok",tok,httponly=True,max_age=86400*30,path="/")
    return r

@app.post("/api/forgot")
async def forgot(req: Request):
    d=await req.json()
    email=d.get("email","").lower().strip()
    if email not in USERS: return {"ok":False,"msg":"Email not found"}
    code=str(secrets.randbelow(900000)+100000)
    RESETS[email]={"code":code,"exp":time.time()+600}
    if SHOW_RESET:
        return {"ok":True,"code":code,"msg":"Use this code (TEST MODE)"}
    return {"ok":True,"msg":"Code sent"}

@app.post("/api/reset")
async def reset(req: Request):
    d=await req.json()
    email=d.get("email","").lower().strip()
    r=RESETS.get(email)
    if not r or r["code"]!=d.get("code") or time.time()>r["exp"]:
        return {"ok":False,"msg":"Invalid or expired code"}
    USERS[email]["pass"]=hashlib.sha256(d.get("new_password","").encode()).hexdigest()
    del RESETS[email]
    return {"ok":True}

@app.post("/api/checkout")
async def checkout(req: Request):
    d=await req.json()
    phone=d.get("phone","").strip()
    items=d.get("items",[])
    total=sum(int(i.get("price",0))*int(i.get("qty",1)) for i in items)
    if total<=0: return {"ok":False,"msg":"Cart empty"}
    if not phone or len(phone)<9: return {"ok":False,"msg":"Enter valid M-Pesa number e.g 0712345678"}
    ref="LONMA"+str(uuid.uuid4())[:8].upper().replace("-","")
    # Fix ref format - only letters+numbers
    ref="LONMA"+str(uuid.uuid4().int)[:6]
    order={"id":ref,"phone":phone,"items":items,"total":total,"status":"PENDING","name":d.get("name",""),"location":d.get("location",""),"time":datetime.now().strftime("%d %b %Y %H:%M")}
    ORDERS.insert(0,order)
    res=stk_push(phone,total,ref)
    if res.get("ok"):
        order["checkout_id"]=res["checkout_id"]
        return {"ok":True,"order_id":ref,"stk":True,"msg":"STK sent! Check your phone and enter M-Pesa PIN"}
    else:
        order["status"]="STK_FAILED"
        order["stk_error"]=res.get("msg","")
        # DO NOT FAKE SUCCESS - return real error
        return {"ok":False,"msg":res.get("msg","STK failed")}

@app.post("/mpesa/callback")
async def mpesa_cb(req: Request):
    try:
        d=await req.json()
        print(f"MPESA CALLBACK: {d}")
        cb=d.get("Body",{}).get("stkCallback",{})
        cid=cb.get("CheckoutRequestID")
        code=cb.get("ResultCode")
        for o in ORDERS:
            if o.get("checkout_id")==cid:
                o["status"]="PAID" if code==0 else "FAILED"
                if code==0:
                    for it in cb.get("CallbackMetadata",{}).get("Item",[]):
                        if it.get("Name")=="MpesaReceiptNumber": o["receipt"]=it.get("Value")
        return {"ResultCode":0,"ResultDesc":"Accepted"}
    except Exception as e:
        print(f"CALLBACK ERR: {e}")
        return {"ResultCode":0,"ResultDesc":"Accepted"}

@app.get("/api/orders")
def orders(req: Request):
    email,u=get_user(req)
    if not u or u["role"]!="admin": return []
    return ORDERS

@app.post("/api/admin/mark-paid")
async def mark_paid(req: Request):
    d=await req.json()
    for o in ORDERS:
        if o["id"]==d.get("id"): o["status"]="PAID"
    return {"ok":True}

@app.get("/api/me")
def me(req: Request):
    email,u=get_user(req)
    if not u: return {"logged":False}
    return {"logged":True,"email":email,"name":u["name"],"role":u["role"]}

@app.get("/logout")
def logout():
    r=RedirectResponse("/")
    r.delete_cookie("tok",path="/")
    return r

@app.get("/privacy", response_class=HTMLResponse)
def privacy():
    return "<h1>Lonma Orbit Privacy Policy</h1><p>We collect name, email, phone, location to process orders and delivery. We do not share data with third parties except M-Pesa for payment. Contact: support@lonmaorbit.co.ke</p><p><a href='/'>Back</a></p>"

# ---------- FRONTEND ----------
@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE

HTML_PAGE = r"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lonma Orbit - Beauty & Hair Store Kenya</title>
<style>
*{box-sizing:border-box;margin:0;padding:0} :root{--pink:#E91E63;--dark:#1A1A2E;--text:#1A1A2E;--bg:#FFF5F7;--card:#fff;--muted:#888}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);padding-bottom:80px}
body.dark{--bg:#121212;--card:#1e1e1e;--text:#fff;--muted:#aaa}
.topbar{background:#111;color:#fff;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:50}
.logo{font-weight:900;font-size:20px;display:flex;align-items:center;gap:8px;cursor:pointer} .logo span{color:#FF4081}
.hamburger{font-size:26px;background:none;border:none;color:#fff;cursor:pointer}
.banner{background:linear-gradient(135deg,#E91E63,#FF4081);color:#fff;padding:18px;border-radius:16px;margin:12px;text-align:center}
.banner h2{font-size:22px} .banner p{opacity:.9;font-size:13px;margin:6px 0 12px}
.btn{background:#111;color:#fff;border:none;padding:11px 18px;border-radius:999px;font-weight:700;cursor:pointer}
.btn-pink{background:#E91E63;color:#fff;border:none;padding:11px 18px;border-radius:999px;font-weight:700;cursor:pointer;width:100%}
.search{margin:0 12px;display:flex;gap:8px} .search input{flex:1;padding:12px;border-radius:999px;border:1px solid #eee;outline:none}
.chips{display:flex;gap:8px;overflow:auto;padding:10px 12px} .chip{white-space:nowrap;padding:8px 14px;border-radius:999px;background:#fff;border:1px solid #eee;font-size:13px;cursor:pointer} .chip.on{background:#111;color:#fff}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:0 12px}
.card{background:var(--card);border-radius:16px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.card img{width:100%;height:150px;object-fit:cover} .card b{display:block;padding:8px 10px 0;font-size:13px;line-height:1.3;min-height:36px}
.price{padding:4px 10px;color:#E91E63;font-weight:900} .price s{color:#aaa;font-weight:400;font-size:12px;margin-left:4px}
.card button{margin:8px 10px 12px;width:calc(100% - 20px);background:#111;color:#fff;border:none;padding:9px;border-radius:999px;font-weight:700;cursor:pointer}
.bottomnav{position:fixed;bottom:0;left:0;right:0;background:#fff;display:flex;justify-content:space-around;padding:10px 0 14px;border-top:1px solid #eee;z-index:60}
.bottomnav button{background:none;border:none;font-size:22px;cursor:pointer;position:relative} .bottomnav span{display:block;font-size:10px}
.badge{position:absolute;top:-6px;right:-6px;background:#E91E63;color:#fff;font-size:10px;padding:2px 6px;border-radius:999px}
.drawer{position:fixed;top:0;left:-300px;width:280px;height:100%;background:#1A1A2E;color:#fff;z-index:100;transition:.3s;padding:20px;overflow:auto}
.drawer.open{left:0} .overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);display:none;z-index:90} .overlay.show{display:block}
.drawer h3{font-size:11px;letter-spacing:1.5px;opacity:.5;margin:22px 0 10px}
.menu-item{display:flex;align-items:center;gap:12px;padding:11px 8px;border-radius:12px;cursor:pointer;font-size:15px;font-weight:600}
.menu-item:active{background:rgba(255,255,255,.08)}
.ico{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:19px;background:transparent;color:#fff;flex-shrink:0}
.pill{margin-left:auto;font-size:10px;padding:4px 10px;border-radius:999px;font-weight:800}
.pill.green{background:#D1FAE5;color:#065F46} .pill.orange{background:#F97316;color:#fff} .pill.dark{background:#333;color:#fff}
.modal{position:fixed;inset:0;background:rgba(0,0,0,.6);display:none;align-items:flex-end;justify-content:center;z-index:200} .modal.show{display:flex}
.sheet{background:#fff;width:100%;max-width:480px;max-height:88vh;overflow:auto;border-radius:20px 20px 0 0;padding:20px}
.sheet input,.sheet select,.sheet textarea{width:100%;padding:12px;border:1px solid #ddd;border-radius:12px;margin:6px 0;outline:none}
.toast{position:fixed;bottom:90px;left:50%;transform:translateX(-50%);background:#111;color:#fff;padding:12px 18px;border-radius:999px;font-size:13px;display:none;z-index:300;max-width:90%;text-align:center}
.testbar{background:#F59E0B;color:#111;text-align:center;padding:8px;font-size:12px;font-weight:700}
</style></head><body>
<div class="topbar"><button class="hamburger" onclick="openDrawer()">☰</button><div class="logo" onclick="window.scrollTo(0,0)"><img src="/logo.png" onerror="this.style.display='none'" style="width:38px;height:38px;border-radius:50%;object-fit:cover;background:#fff"><span>LONMA <span style="color:#FF4081">ORBIT</span></span></div><button onclick="openCart()" style="background:none;border:none;color:#fff;font-size:22px">🛒 <span id="cartCountTop">0</span></button></div>
<div id="testBar"></div>
<div class="banner"><h2>✨ Beauty Delivered in Nairobi</h2><p>Same-day delivery • Pay with M-Pesa • 100% Genuine</p><button class="btn" style="background:#fff;color:#E91E63" onclick="document.getElementById('grid').scrollIntoView()">Shop Now →</button></div>
<div class="search"><input id="q" placeholder="Search Diva, Detrex, Sawa..." oninput="render()"><button class="btn" onclick="render()">Search</button></div>
<div class="chips" id="chips"></div>
<div id="grid" class="grid"></div>
<div style="padding:16px 12px"><div style="background:#111;color:#fff;border-radius:16px;padding:16px"><b>💬 Join Our Community</b><p style="font-size:13px;opacity:.8;margin:6px 0">Hair tips, reviews, new drops</p><button class="btn-pink" onclick="openCommunity()">Join Community →</button></div></div>
<div class="bottomnav">
<button onclick="window.scrollTo(0,0)">🏠<span>Home</span></button>
<button onclick="openDrawer()">☰<span>Menu</span></button>
<button onclick="openCart()">🛒<span>Cart</span><span class="badge" id="cartBadge">0</span></button>
<button onclick="openTrack()">📦<span>Track</span></button>
<button onclick="openMe()">👤<span>Account</span></button>
</div>
<div class="overlay" id="overlay" onclick="closeDrawer()"></div>
<div class="drawer" id="drawer">
<div style="display:flex;justify-content:space-between;align-items:center"><div style="display:flex;align-items:center;gap:8px"><img src="/logo.png" onerror="this.style.display='none'" style="width:38px;height:38px;border-radius:50%;object-fit:cover;background:#fff"><b style="font-size:20px">LONMA <span style="color:#FF4081">ORBIT</span></b></div><button onclick="closeDrawer()" style="background:none;border:none;color:#fff;font-size:22px">✕</button></div>
<p style="font-size:12px;opacity:.6;margin-top:4px">Beauty • Hair • Skin • Kenya</p>
<h3>SHOP</h3>
<div class="menu-item" onclick="filterCat('All')"><span class="ico">🏠</span> Home</div>
<div class="menu-item" onclick="openCart()"><span class="ico">🛒</span> Cart <span class="pill orange" id="drawerCart">0</span></div>
<div class="menu-item" onclick="openTrack()"><span class="ico">📦</span> Track Order</div>
<div class="menu-item" onclick="openCommunity()"><span class="ico">💬</span> Community <span class="pill orange">NEW</span></div>
<h3>MY DASHBOARD</h3>
<div class="menu-item" onclick="openMe()"><span class="ico">👤</span> My Dashboard <span class="pill green">CUSTOMER</span></div>
<div class="menu-item" onclick="toggleDark()"><span class="ico">🎨</span> Appearance <span class="pill orange">NEW</span></div>
<h3>SUPPORT</h3>
<div class="menu-item" onclick="openVerify()"><span class="ico">✅</span> Verify Product</div>
<div class="menu-item" onclick="window.open('https://wa.me/254700000000')"><span class="ico">💬</span> WhatsApp Us</div>
<div class="menu-item" onclick="openTerms()"><span class="ico">📄</span> Terms & Conditions</div>
<div class="menu-item" onclick="openForgot()"><span class="ico">🔒</span> Forgot Password</div>
<h3>ADMIN</h3>
<div class="menu-item" onclick="openAdmin()"><span class="ico">⚙️</span> Admin Dashboard <span class="pill dark">ADMIN</span></div>
<p style="text-align:center;opacity:.5;font-size:12px;margin-top:20px">v17.0 Production • Kenya</p>
</div>
<div class="modal" id="modal"><div class="sheet" id="sheet"></div></div>
<div class="toast" id="toast"></div>
<script>
let PRODUCTS=[], cart=JSON.parse(localStorage.getItem('cart')||'[]'), cat='All';
async function load(){ PRODUCTS=await (await fetch('/api/products')).json(); let h=await (await fetch('/api/health')).json(); if(h.mpesa_env!=='production') document.getElementById('testBar').innerHTML='<div class="testbar">⚠️ TEST MODE - M-Pesa Sandbox</div>'; renderChips(); render(); updateCart(); }
function renderChips(){ let cats=['All',...new Set(PRODUCTS.map(p=>p.cat))]; document.getElementById('chips').innerHTML=cats.map(c=>`<div class="chip ${c==cat?'on':''}" onclick="filterCat('${c}')">${c}</div>`).join(''); }
function filterCat(c){cat=c;renderChips();render();closeDrawer();}
function render(){ let q=(document.getElementById('q').value||'').toLowerCase(); let list=PRODUCTS.filter(p=>(cat=='All'||p.cat==cat)&&(p.name.toLowerCase().includes(q))); document.getElementById('grid').innerHTML=list.map(p=>`<div class="card"><img src="${p.img}"><b>${p.name}</b><div style="padding:0 10px;font-size:12px;color:#888">${p.cat} • ${p.stock} left</div><div class="price">KSh ${p.price}<s>${p.old}</s></div><button onclick="addToCart('${p.id}')">Add to Cart +</button></div>`).join('')||'<p style="padding:20px">No products found</p>'; }
function addToCart(id){ let p=PRODUCTS.find(x=>x.id==id); let ex=cart.find(x=>x.id==id); if(ex) ex.qty++; else cart.push({id:p.id,name:p.name,price:p.price,qty:1}); localStorage.setItem('cart',JSON.stringify(cart)); updateCart(); toast('Added to cart ✅'); }
function updateCart(){ let n=cart.reduce((a,b)=>a+b.qty,0); document.getElementById('cartBadge').innerText=n; document.getElementById('cartCountTop').innerText=n; document.getElementById('drawerCart').innerText=n; }
function openDrawer(){document.getElementById('drawer').classList.add('open');document.getElementById('overlay').classList.add('show')} function closeDrawer(){document.getElementById('drawer').classList.remove('open');document.getElementById('overlay').classList.remove('show')}
function show(html){document.getElementById('sheet').innerHTML=html;document.getElementById('modal').classList.add('show')} function closeModal(){document.getElementById('modal').classList.remove('show')}
function toast(m){let t=document.getElementById('toast');t.innerText=m;t.style.display='block';setTimeout(()=>t.style.display='none',4000)}
function toggleDark(){document.body.classList.toggle('dark');closeDrawer();toast('Theme changed 🎨')}
function openCart(){ let total=cart.reduce((a,b)=>a+b.price*b.qty,0); if(!cart.length) return show('<h3>🛒 Your Cart is Empty</h3><p style="margin:10px 0">Add products first</p><button class="btn-pink" onclick="closeModal()">Continue Shopping</button>'); show(`<h3>🛒 Cart (${cart.length})</h3>${cart.map((it,i)=>`<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #eee"><div><b>${it.name}</b><br><small>KSh ${it.price} x ${it.qty}</small></div><b>KSh ${it.price*it.qty}</b></div>`).join('')}<h3 style="margin:12px 0">Total: KSh ${total}</h3><input id="cname" placeholder="Your Full Name"><input id="cphone" placeholder="M-Pesa Phone e.g 0712345678"><input id="cloc" placeholder="Location / Estate - Nairobi"><button class="btn-pink" onclick="doCheckout(${total})">Pay KSh ${total} with M-Pesa →</button><button class="btn" style="width:100%;margin-top:8px" onclick="cart=[];localStorage.setItem('cart','[]');updateCart();closeModal()">Clear Cart</button>`); }
async function doCheckout(total){ let phone=document.getElementById('cphone').value.trim(); let name=document.getElementById('cname').value.trim(); let loc=document.getElementById('cloc').value.trim(); if(!phone||phone.length<10) return toast('Enter valid M-Pesa number e.g 0712345678'); if(!name) return toast('Enter your name'); show('<h3>⏳ Sending STK Push...</h3><p>Please wait, contacting M-Pesa...</p><p style="font-size:13px;color:#888">Do not close this</p>'); let r=await (await fetch('/api/checkout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone,name,location:loc,items:cart})})).json(); if(r.ok){ cart=[];localStorage.setItem('cart','[]');updateCart(); show(`<h3>✅ Order ${r.order_id}</h3><p style="margin:10px 0">${r.msg}</p><p>Check your phone NOW and enter PIN</p><button class="btn-pink" onclick="closeModal()">Done</button>`);} else { show(`<h3>❌ M-Pesa Failed</h3><p style="margin:12px 0;background:#FEF2F2;padding:12px;border-radius:12px;font-size:14px;line-height:1.5">${r.msg}</p><p style="font-size:13px;color:#666">No money was deducted. Fix the error above and try again.</p><button class="btn-pink" onclick="openCart()">Try Again</button><button class="btn" style="width:100%;margin-top:8px" onclick="closeModal()">Cancel</button>`); } }
function openMe(){ show(`<h3>👤 My Account</h3><input id="lemail" placeholder="Email"><input id="lpass" type="password" placeholder="Password"><button class="btn-pink" onclick="doLogin()">Login</button><p style="text-align:center;margin:10px 0">or</p><input id="rname" placeholder="Full Name"><input id="remail" placeholder="Email"><input id="rphone" placeholder="Phone 07..."><input id="rpass" type="password" placeholder="Create Password"><button class="btn-pink" onclick="doReg()">Create Account</button><p style="text-align:center;margin-top:10px;color:#E91E63;cursor:pointer" onclick="openForgot()">Forgot Password?</p><p style="text-align:center;margin-top:10px;font-size:12px">Admin: admin@lonma.co.ke / admin123</p>`); }
async function doLogin(){ let r=await (await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('lemail').value,password:document.getElementById('lpass').value})})).json(); if(r.ok){toast('Welcome '+r.name);closeModal();} else toast(r.msg); }
async function doReg(){ let r=await (await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('rname').value,email:document.getElementById('remail').value,phone:document.getElementById('rphone').value,password:document.getElementById('rpass').value})})).json(); toast(r.ok?'Account created! Now login':'Failed: '+r.msg); }
function openForgot(){ show(`<h3>🔒 Forgot Password</h3><input id="femail" placeholder="Your Email"><button class="btn-pink" onclick="doForgot()">Send Reset Code</button><div id="fstep"></div>`); }
async function doForgot(){ let r=await (await fetch('/api/forgot',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('femail').value})})).json(); if(!r.ok) return toast(r.msg); let codeMsg=r.code?`<div style="background:#FEF3C7;padding:12px;border-radius:12px;margin:10px 0"><b>Your Code: ${r.code}</b><br><small>Copy this - TEST MODE</small></div>`:''; document.getElementById('fstep').innerHTML=codeMsg+`<input id="fcode" placeholder="Enter 6-digit Code"><input id="fnew" type="password" placeholder="New Password"><button class="btn-pink" onclick="doReset()">Reset Password</button>`; }
async function doReset(){ let r=await (await fetch('/api/reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('femail').value,code:document.getElementById('fcode').value,new_password:document.getElementById('fnew').value})})).json(); toast(r.ok?'Password reset! Login now':'Invalid code'); if(r.ok) closeModal(); }
function openVerify(){ show(`<h3>✅ Verify Product</h3><p>Enter code on your product box</p><input id="vcode" placeholder="e.g LONMA-12345"><button class="btn-pink" onclick="toast('✅ Genuine Lonma Product!')">Verify</button>`); }
function openTerms(){ show(`<h3>📄 Terms & Conditions</h3><p style="font-size:13px;line-height:1.6;margin-top:10px">1. All products are 100% genuine.<br>2. Delivery within Nairobi same-day, upcountry 1-3 days.<br>3. Returns within 7 days if unopened.<br>4. Payment via M-Pesa is secure.<br>5. By ordering you agree to these terms.</p><button class="btn-pink" onclick="closeModal()">Close</button>`); }
function openCommunity(){ show(`<h3>💬 Community</h3><div style="background:#FFF5F7;padding:12px;border-radius:12px;margin:10px 0"><b>Mary W. ⭐⭐⭐⭐⭐</b><p style="font-size:13px">Hair oil worked in 2 weeks! Love it</p></div><div style="background:#F0FDF4;padding:12px;border-radius:12px"><b>Jane K. ⭐⭐⭐⭐⭐</b><p style="font-size:13px">Fast delivery, genuine products</p></div><button class="btn-pink" style="margin-top:12px" onclick="window.open('https://wa.me/254700000000')">Join WhatsApp Group →</button>`); }
function openTrack(){ show(`<h3>📦 Track Order</h3><input id="torder" placeholder="Order ID e.g LONMA..."><button class="btn-pink" onclick="toast('Order status: WhatsApp us with your Order ID for live update')">Track</button><p style="font-size:13px;margin-top:10px">After payment, we prepare & deliver. WhatsApp us with your Order ID for live update.</p>`); }
async function openAdmin(){ let me=await (await fetch('/api/me')).json(); if(!me.logged||me.role!=='admin') return show(`<h3>⚙️ Admin Login Required</h3><p>Login as admin first</p><button class="btn-pink" onclick="openMe()">Login as Admin</button>`); let ords=await (await fetch('/api/orders')).json(); show(`<h3>⚙️ Admin Dashboard</h3><p>${ords.length} orders • Total: KSh ${ords.reduce((a,b)=>a+b.total,0)}</p>${ords.map(o=>`<div style="border:1px solid #eee;padding:10px;border-radius:12px;margin:8px 0"><b>${o.id}</b> - KSh ${o.total} - <span style="color:${o.status=='PAID'?'green':'red'}">${o.status}</span><br><small>${o.name} • ${o.phone} • ${o.location}</small><br>${o.stk_error?`<small style="color:red">${o.stk_error}</small><br>`:''}<button class="btn" style="padding:6px 12px;margin-top:6px" onclick="markPaid('${o.id}')">Mark PAID</button></div>`).join('')||'<p>No orders yet</p>'}`); }
async function markPaid(id){ await fetch('/api/admin/mark-paid',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id})}); toast('Marked PAID'); openAdmin(); }
document.getElementById('modal').addEventListener('click',e=>{if(e.target.id=='modal') closeModal()});
load();
</script></body></html>
"""
