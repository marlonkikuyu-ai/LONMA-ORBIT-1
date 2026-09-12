from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, base64, requests, random
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "")
MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://app.lonmaorbit.co.ke/mpesa/callback")
MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")

def get_token():
    try:
        if not MPESA_CONSUMER_KEY or not MPESA_CONSUMER_SECRET: return None
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        r=requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET), timeout=10)
        return r.json().get("access_token")
    except: return None

STORES = [
    {"id":"naivas","name":"NAIVAS","color":"#008000"},
    {"id":"quickmart","name":"QUICKMART","color":"#FF0000"},
    {"id":"carrefour","name":"CARREFOUR","color":"#0047AB"},
    {"id":"chandarana","name":"CHANDARANA","color":"#FF8C00"},
    {"id":"magunas","name":"MAGUNAS","color":"#800080"},
]

CATEGORIES = [
    {"id":"fresh","name":"Fresh Food","icon":"🥬"},
    {"id":"grocery","name":"Grocery","icon":"🛒"},
    {"id":"beverages","name":"Beverages","icon":"🥤"},
    {"id":"dairy","name":"Dairy & Bakery","icon":"🥛"},
    {"id":"household","name":"Household","icon":"🧹"},
    {"id":"personal","name":"Personal Care","icon":"🧴"},
]

PRODUCTS=[
    {"id":1,"name":"Ajab Flour 2kg","price":175,"store":"naivas","category":"grocery","image":"https://via.placeholder.com/300/f0f0f0/000?text=Flour"},
    {"id":2,"name":"Brookside Milk 500ml","price":65,"store":"naivas","category":"dairy","image":"https://via.placeholder.com/300/fff/000?text=Milk"},
    {"id":3,"name":"Coca Cola 1.25L","price":100,"store":"quickmart","category":"beverages","image":"https://via.placeholder.com/300/FF0000/fff?text=Coke"},
    {"id":4,"name":"Omo 1kg","price":285,"store":"carrefour","category":"household","image":"https://via.placeholder.com/300/0047AB/fff?text=Omo"},
    {"id":5,"name":"Tomatoes 1kg","price":80,"store":"quickmart","category":"fresh","image":"https://via.placeholder.com/300/008000/fff?text=Tomatoes"},
    {"id":6,"name":"Bread 400g","price":60,"store":"naivas","category":"dairy","image":"https://via.placeholder.com/300/FFD700/000?text=Bread"},
]

RIDERS = [
    {"id":1,"name":"John Mwangi","phone":"254712345678","motor":"KMEZ 123A","status":"available","orders":12,"rating":4.9,"location":"Kajiado Town"},
    {"id":2,"name":"Peter Ochieng","phone":"254723456789","motor":"KMFA 456B","status":"delivering","orders":28,"rating":4.8,"location":"Kitengela"},
    {"id":3,"name":"Samuel Kiprop","phone":"254734567890","motor":"KMEB 789C","status":"available","orders":15,"rating":5.0,"location":"Ongata Rongai"},
]

ORDERS = [] # in-memory orders

@app.get("/", response_class=HTMLResponse)
async def home():
    store_tabs="".join([f'<button class="store-tab" onclick="filterStore(\'{s["id"]}\')"><span style="background:{s["color"]}">{s["name"][0]}</span>{s["name"]}</button>' for s in STORES])
    cat_cards="".join([f'<div class="cat-card" onclick="filterCat(\'{c["id"]}\')"><div>{c["icon"]}</div><h4>{c["name"]}</h4></div>' for c in CATEGORIES])
    prod_cards="".join([f'<div class="prod-card" data-store="{p["store"]}" data-cat="{p["category"]}"><img src="{p["image"]}"><div class="store-badge" style="background:{[s["color"] for s in STORES if s["id"]==p["store"]][0]}">{p["store"].upper()}</div><h4>{p["name"]}</h4><div class="price-row"><span class="price">KSH {p["price"]}</span><button onclick="addToCart({p["id"]},\'{p["name"]}\',{p["price"]})">Add</button></div></div>' for p in PRODUCTS])
    return f'''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{font-family:Arial;background:#f5f6fa}}
header{{background:#0A8EA8;padding:10px 15px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100}} header img{{height:55px}}
.nav-btns{{display:flex;gap:8px}}.nav-btn{{padding:8px 12px;background:#fff;color:#0A8EA8;border:none;border-radius:20px;font-weight:900;font-size:11px;cursor:pointer}}
.hero{{background:#fff;padding:15px;border-bottom:1px solid #eee}}.hero h1{{font-size:18px;font-weight:900}}.hero p{{font-size:12px;color:#666}}
.store-tabs{{display:flex;gap:8px;overflow-x:auto;padding:10px 15px;background:#fff;border-bottom:1px solid #eee}}.store-tab{{display:flex;align-items:center;gap:6px;padding:6px 10px;border:2px solid #ddd;border-radius:20px;background:#fff;white-space:nowrap;font-weight:900;font-size:11px;cursor:pointer}}.store-tab span{{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff}}
.section{{padding:15px}}.section h3{{font-size:15px;font-weight:900;margin-bottom:10px}}
.cat-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}.cat-card{{background:#fff;border-radius:12px;padding:12px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.05);cursor:pointer}}.cat-card div{{font-size:24px}}.cat-card h4{{font-size:11px;font-weight:900;margin-top:4px}}
.prod-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}}.prod-card{{background:#fff;border-radius:12px;padding:8px;position:relative;box-shadow:0 1px 4px rgba(0,0,0,0.05)}}.prod-card img{{width:100%;border-radius:8px;aspect-ratio:1;object-fit:cover}}.store-badge{{position:absolute;top:10px;left:10px;font-size:8px;padding:3px 6px;border-radius:8px;font-weight:900;color:#fff}}.prod-card h4{{font-size:11px;margin:6px 0;height:26px;overflow:hidden}}.price-row{{display:flex;justify-content:space-between;align-items:center}}.price{{font-weight:900;color:#0A8EA8;font-size:12px}}.price-row button{{padding:5px 10px;background:#000;color:#fff;border:none;border-radius:12px;font-weight:700;font-size:10px}}
footer{{background:#000;color:#fff;padding:15px;text-align:center;margin-top:15px}} footer img{{height:45px}}
.modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);justify-content:center;align-items:center;z-index:200;overflow-y:auto;padding:15px}}.box{{background:#fff;padding:18px;border-radius:14px;width:100%;max-width:380px;max-height:90vh;overflow-y:auto}}.box input{{width:100%;padding:11px;margin:8px 0;border-radius:8px;border:1px solid #ddd}}
.rider-card{{background:#fff;border-radius:12px;padding:12px;margin-bottom:10px;border-left:4px solid #0A8EA8;display:flex;justify-content:space-between;align-items:center}}.rider-info h4{{font-size:13px}}.rider-info p{{font-size:11px;color:#666}}.status{{padding:4px 8px;border-radius:10px;font-size:9px;font-weight:900}}.available{{background:#d4edda;color:#155724}}.delivering{{background:#fff3cd;color:#856404}}
.order-status{{background:#fff;border-radius:12px;padding:15px;margin-top:10px;border:1px solid #0A8EA8}}.step{{display:flex;gap:10px;margin:8px 0}}.dot{{width:20px;height:20px;border-radius:50%;background:#ddd;display:flex;align-items:center;justify-content:center;font-size:10px}}.dot.active{{background:#0A8EA8;color:#fff}}
.cart-item{{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;font-size:12px}}
</style></head><body>
<header><img src="/logo.png"><div class="nav-btns"><button class="nav-btn" onclick="openRiderLogin()">🏍️ RIDER</button><button class="nav-btn" onclick="openCart()">🛒 <span id="cartCount">0</span></button></div></header>
<div class="hero"><h1>🛒 Compare • Order • Delivered</h1><p>Naivas | Quickmart | Carrefour | Chandarana | Magunas + Rider Delivery</p></div>
<div class="store-tabs"><button class="store-tab" onclick="filterStore('ALL')">ALL STORES</button>{store_tabs}</div>
<div class="section"><div class="cat-grid">{cat_cards}</div></div>
<div class="section"><h3>Best Deals - Rider Delivers in 30min</h3><div class="prod-grid" id="prodGrid">{prod_cards}</div></div>
<footer><img src="/logo.png"><p style="font-weight:900;font-size:12px;letter-spacing:1px">LONMA ORBIT • RIDER DELIVERY</p></footer>

<!-- CART MODAL -->
<div id="cartModal" class="modal"><div class="box"><h3>🛒 Cart (<span id="cartNum">0</span>)</h3><div id="cartItems"></div><p style="font-weight:900;margin-top:10px">Total: KSH <span id="cartTotal">0</span></p><input id="custPhone" value="254" placeholder="Your M-Pesa Phone"><input id="custLocation" placeholder="Delivery Location - e.g. Kajiado Town"><button onclick="checkout()" style="width:100%;padding:12px;background:#00a651;color:#fff;border:none;border-radius:8px;font-weight:900;margin-top:8px">Lipa na M-Pesa + Rider Delivery</button><button onclick="closeModals()" style="width:100%;margin-top:8px;padding:10px;background:#eee;border:none;border-radius:8px">Continue Shopping</button><p id="checkoutStatus" style="text-align:center;font-weight:700;margin-top:8px"></p><div id="tracking" style="display:none" class="order-status"><h4>📦 Order Tracking</h4><div class="step"><div class="dot active">✓</div><div><b>Order Placed</b><p style="font-size:11px">We received your order</p></div></div><div class="step"><div class="dot" id="dot2">2</div><div><b>Rider Assigned</b><p style="font-size:11px" id="riderAssigned">Finding rider...</p></div></div><div class="step"><div class="dot" id="dot3">3</div><div><b>On The Way</b><p style="font-size:11px">Rider is delivering</p></div></div><div class="step"><div class="dot" id="dot4">4</div><div><b>Delivered</b><p style="font-size:11px">Enjoy!</p></div></div><button onclick="openRiderLogin()" style="width:100%;margin-top:10px;padding:10px;background:#0A8EA8;color:#fff;border:none;border-radius:8px;font-weight:700">Track Rider Live</button></div></div></div>

<!-- RIDER MODAL -->
<div id="riderModal" class="modal"><div class="box"><h3>🏍️ Rider Dashboard</h3><div style="display:flex;gap:8px;margin:10px 0"><input id="riderPhone" placeholder="Enter Rider Phone e.g. 2547..." style="flex:1"><button onclick="riderLogin()" style="padding:11px 15px;background:#0A8EA8;color:#fff;border:none;border-radius:8px;font-weight:900">Login</button></div><div id="riderInfo"></div><div id="riderOrders"></div><button onclick="closeModals()" style="width:100%;margin-top:10px;padding:10px;background:#eee;border:none;border-radius:8px">Close</button></div></div>

<script>
let cart=[], total=0;
function addToCart(id,name,price){{cart.push({{id,name,price}}); total+=price; document.getElementById('cartCount').innerText=cart.length; alert(name+' added!')}}
function openCart(){{let itemsDiv=document.getElementById('cartItems'); itemsDiv.innerHTML=''; cart.forEach(c=>{{itemsDiv.innerHTML+=`<div class="cart-item"><span>${{c.name}}</span><b>KSH ${{c.price}}</b></div>`}}); document.getElementById('cartNum').innerText=cart.length; document.getElementById('cartTotal').innerText=total; document.getElementById('cartModal').style.display='flex'}}
function closeModals(){{document.getElementById('cartModal').style.display='none'; document.getElementById('riderModal').style.display='none'}}
async function checkout(){{let phone=document.getElementById('custPhone').value; let loc=document.getElementById('custLocation').value; if(!loc){{alert('Enter delivery location'); return}} document.getElementById('checkoutStatus').innerText='Processing M-Pesa...'; let r=await fetch('/mpesa/stkpush',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{phone,amount:total,location:loc,cart}})}}); let d=await r.json(); if(d.ResponseCode=='0'){{document.getElementById('checkoutStatus').innerText='✅ Pay on phone! Rider will be assigned.'; startTracking()}} else {{document.getElementById('checkoutStatus').innerText=d.error||JSON.stringify(d)}}}}
function startTracking(){{document.getElementById('tracking').style.display='block'; setTimeout(()=>{{document.getElementById('dot2').classList.add('active'); document.getElementById('riderAssigned').innerText='John Mwangi - KMEZ 123A - 4.9★ - Coming!';}},2000); setTimeout(()=>{{document.getElementById('dot3').classList.add('active')}},5000)}}
function openRiderLogin(){{document.getElementById('riderModal').style.display='flex'; loadRiders()}}
async function loadRiders(){{let r=await fetch('/riders'); let riders=await r.json(); let html=''; riders.forEach(rd=>{{html+=`<div class="rider-card"><div class="rider-info"><h4>${{rd.name}} ⭐${{rd.rating}}</h4><p>${{rd.motor}} • ${{rd.location}} • ${{rd.orders}} deliveries</p></div><span class="status ${{rd.status}}">${{rd.status.toUpperCase()}}</span></div>`}}); document.getElementById('riderInfo').innerHTML=html; let ro=await fetch('/orders'); let orders=await ro.json(); let oh='<h4 style="margin-top:15px">📦 Active Orders</h4>'; orders.slice(-5).forEach(o=>{{oh+=`<div class="rider-card"><div><b>KSH ${{o.amount}}</b> - ${{o.location}}<br><small>${{o.phone}}</small></div><button onclick="acceptOrder('${{o.id}}')" style="padding:6px 12px;background:#00a651;color:#fff;border:none;border-radius:12px;font-size:11px">Accept</button></div>`}}); document.getElementById('riderOrders').innerHTML=oh}}
async function riderLogin(){{let phone=document.getElementById('riderPhone').value; alert('Rider '+phone+' logged in! Check orders below.'); loadRiders()}}
async function acceptOrder(id){{await fetch('/rider/accept/'+id,{{method:'POST'}}); alert('Order '+id+' accepted! Customer notified.'); loadRiders()}}
function filterStore(store){{document.querySelectorAll('.prod-card').forEach(c=>{{if(store=='ALL'||c.dataset.store==store) c.style.display='block'; else c.style.display='none'}})}}
function filterCat(cat){{document.querySelectorAll('.prod-card').forEach(c=>{{if(c.dataset.cat==cat) c.style.display='block'; else c.style.display='none'}})}}
</script></body></html>
'''

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    try:
        b=await req.json(); token=get_token()
        # Save order
        order_id = f"ORD{random.randint(1000,9999)}"
        ORDERS.append({"id":order_id,"phone":b.get("phone"),"amount":b.get("amount",1),"location":b.get("location","Kajiado"),"cart":b.get("cart",[]),"status":"paid","rider":random.choice(RIDERS)["name"],"time":datetime.now().isoformat()})
        if not token: return {"error":"M-Pesa keys not set - order saved as COD","ResponseCode":"0","order_id":order_id}
        ts=datetime.now().strftime("%Y%m%d%H%M%S"); pwd=base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{ts}".encode()).decode()
        url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        r=requests.post(url,json={"BusinessShortCode":MPESA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":int(b.get("amount",1)),"PartyA":b.get("phone"),"PartyB":MPESA_SHORTCODE,"PhoneNumber":b.get("phone"),"CallBackURL":MPESA_CALLBACK_URL,"AccountReference":order_id,"TransactionDesc":"LONMA RIDER"},headers={"Authorization":f"Bearer {token}"},timeout=10)
        data=r.json(); data["order_id"]=order_id
        return data
    except Exception as e: return {"error":str(e),"ResponseCode":"1"}

@app.get("/riders")
async def get_riders(): return RIDERS

@app.get("/orders")
async def get_orders(): return ORDERS[::-1]

@app.post("/rider/accept/{order_id}")
async def accept(order_id: str):
    for o in ORDERS:
        if o["id"]==order_id: o["status"]="rider_assigned"
    return {"success":True}

@app.get("/mpesa/callback")
async def cb_get(): return {"ResultCode":0,"ResultDesc":"OK"}
@app.post("/mpesa/callback")
async def cb_post(req: Request): print(await req.json());return {"ResultCode":0,"ResultDesc":"Accepted"}
@app.get("/logo.png")
async def logo(): return FileResponse("logo.png") if os.path.exists("logo.png") else {"error":"logo.png missing"}
@app.get("/favicon.ico")
async def fav(): return FileResponse("logo.png") if os.path.exists("logo.png") else {}
@app.get("/rider")
async def rider_page():
    return HTMLResponse('<script>window.location.href="/#rider"</script><meta http-equiv="refresh" content="0;url=/#">')
