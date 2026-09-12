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

STORES=[{"id":"naivas","name":"NAIVAS","color":"#008000"},{"id":"quickmart","name":"QUICKMART","color":"#FF0000"},{"id":"carrefour","name":"CARREFOUR","color":"#0047AB"},{"id":"chandarana","name":"CHANDARANA","color":"#FF8C00"},{"id":"magunas","name":"MAGUNAS","color":"#800080"}]
CATEGORIES=[{"id":"fresh","name":"Fresh","icon":"🥬"},{"id":"grocery","name":"Grocery","icon":"🛒"},{"id":"beverages","name":"Drinks","icon":"🥤"},{"id":"dairy","name":"Dairy","icon":"🥛"},{"id":"household","name":"Home","icon":"🧹"},{"id":"personal","name":"Care","icon":"🧴"}]
PRODUCTS=[
    {"id":1,"name":"Ajab Flour 2kg","price":175,"store":"naivas","category":"grocery","image":"https://via.placeholder.com/300/f0f0f0/000?text=Flour","stock":50},
    {"id":2,"name":"Brookside Milk 500ml","price":65,"store":"naivas","category":"dairy","image":"https://via.placeholder.com/300/fff/000?text=Milk","stock":100},
    {"id":3,"name":"Coke 1.25L","price":100,"store":"quickmart","category":"beverages","image":"https://via.placeholder.com/300/FF0000/fff?text=Coke","stock":80},
    {"id":4,"name":"Omo 1kg","price":285,"store":"carrefour","category":"household","image":"https://via.placeholder.com/300/0047AB/fff?text=Omo","stock":40},
    {"id":5,"name":"Tomatoes 1kg","price":80,"store":"quickmart","category":"fresh","image":"https://via.placeholder.com/300/008000/fff?text=Tomato","stock":60},
    {"id":6,"name":"Bread 400g","price":60,"store":"naivas","category":"dairy","image":"https://via.placeholder.com/300/FFD700/000?text=Bread","stock":70},
    {"id":7,"name":"Rice 2kg","price":350,"store":"carrefour","category":"grocery","image":"https://via.placeholder.com/300/fff/000?text=Rice","stock":30},
    {"id":8,"name":"Geisha Soap","price":55,"store":"magunas","category":"personal","image":"https://via.placeholder.com/300/FF69B4/fff?text=Soap","stock":90},
]
RIDERS=[
    {"id":1,"name":"John Mwangi","phone":"254712345678","motor":"KMEZ 123A","status":"available","orders":12,"rating":4.9,"location":"Kajiado","lat":-1.85,"lng":36.78},
    {"id":2,"name":"Peter Ochieng","phone":"254723456789","motor":"KMFA 456B","status":"delivering","orders":28,"rating":4.8,"location":"Kitengela","lat":-1.47,"lng":36.94},
    {"id":3,"name":"Samuel Kiprop","phone":"254734567890","motor":"KMEB 789C","status":"available","orders":15,"rating":5.0,"location":"Rongai","lat":-1.39,"lng":36.75},
]
ORDERS=[]

@app.get("/", response_class=HTMLResponse)
async def home():
    store_tabs="".join([f'<button class="store-tab" onclick="filterStore(\'{s["id"]}\')"><span style="background:{s["color"]}">{s["name"][0]}</span>{s["name"]}</button>' for s in STORES])
    cat_cards="".join([f'<div class="cat-card" onclick="filterCat(\'{c["id"]}\')"><div>{c["icon"]}</div><h4>{c["name"]}</h4></div>' for c in CATEGORIES])
    prod_cards="".join([f'<div class="prod-card" data-store="{p["store"]}" data-cat="{p["category"]}"><img src="{p["image"]}"><div class="store-badge" style="background:{[s["color"] for s in STORES if s["id"]==p["store"]][0]}">{p["store"].upper()}</div><span class="stock">{p["stock"]} left</span><h4>{p["name"]}</h4><div class="price-row"><span class="price">KSH {p["price"]}</span><button onclick="addToCart({p["id"]},\'{p["name"]}\',{p["price"]})">Add</button></div></div>' for p in PRODUCTS])
    return f'''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT Super App</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{font-family:Arial;background:#f5f6fa}} header{{background:#0A8EA8;padding:10px 15px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100}} header img{{height:50px}}.nav{{display:flex;gap:6px}}.nav button{{padding:7px 10px;background:#fff;color:#0A8EA8;border:none;border-radius:18px;font-weight:900;font-size:10px;cursor:pointer}}
.hero{{background:#fff;padding:12px 15px;border-bottom:1px solid #eee}}.hero h1{{font-size:16px;font-weight:900}}.hero p{{font-size:11px;color:#666}}
.store-tabs{{display:flex;gap:6px;overflow-x:auto;padding:8px 12px;background:#fff;border-bottom:1px solid #eee}}.store-tab{{display:flex;align-items:center;gap:5px;padding:5px 9px;border:1.5px solid #ddd;border-radius:18px;background:#fff;white-space:nowrap;font-weight:900;font-size:10px;cursor:pointer}}.store-tab span{{width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:10px}}
.section{{padding:12px}}.section h3{{font-size:14px;font-weight:900;margin-bottom:8px}}
.cat-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}}.cat-card{{background:#fff;border-radius:10px;padding:10px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.05);cursor:pointer}}.cat-card div{{font-size:20px}}.cat-card h4{{font-size:10px;font-weight:900;margin-top:3px}}
.prod-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:6px}}.prod-card{{background:#fff;border-radius:10px;padding:6px;position:relative;box-shadow:0 1px 3px rgba(0,0,0,0.05)}}.prod-card img{{width:100%;border-radius:8px;aspect-ratio:1;object-fit:cover}}.store-badge{{position:absolute;top:8px;left:8px;font-size:7px;padding:2px 5px;border-radius:6px;font-weight:900;color:#fff}}.stock{{position:absolute;top:8px;right:8px;font-size:7px;background:rgba(0,0,0,0.6);color:#fff;padding:2px 5px;border-radius:6px}}.prod-card h4{{font-size:10px;margin:5px 0;height:24px;overflow:hidden}}.price-row{{display:flex;justify-content:space-between;align-items:center}}.price{{font-weight:900;color:#0A8EA8;font-size:11px}}.price-row button{{padding:4px 8px;background:#000;color:#fff;border:none;border-radius:10px;font-weight:700;font-size:9px}}
footer{{background:#000;color:#fff;padding:12px;text-align:center;margin-top:10px}} footer img{{height:40px}}
.modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);justify-content:center;align-items:center;z-index:200;overflow-y:auto;padding:10px}}.box{{background:#fff;padding:14px;border-radius:12px;width:100%;max-width:380px;max-height:92vh;overflow-y:auto}}.box input,.box select{{width:100%;padding:10px;margin:6px 0;border-radius:8px;border:1px solid #ddd;font-size:12px}}.btn{{width:100%;padding:11px;border:none;border-radius:8px;font-weight:900;cursor:pointer;margin-top:6px;font-size:12px}}.btn-green{{background:#00a651;color:#fff}}.btn-teal{{background:#0A8EA8;color:#fff}}.btn-black{{background:#000;color:#fff}}.btn-gray{{background:#eee;color:#333}}
.rider-card{{background:#fff;border-radius:10px;padding:10px;margin-bottom:8px;border-left:3px solid #0A8EA8;display:flex;justify-content:space-between;align-items:center;box-shadow:0 1px 3px rgba(0,0,0,0.05)}}.status{{padding:3px 6px;border-radius:8px;font-size:8px;font-weight:900}}.available{{background:#d4edda;color:#155724}}.delivering{{background:#fff3cd;color:#856404}}.offline{{background:#f8d7da;color:#721c24}}
.order-card{{background:#fff;border-radius:10px;padding:10px;margin-bottom:8px;border:1px solid #eee}}.map{{width:100%;height:180px;background:linear-gradient(45deg,#e0f7fa,#b2ebf2);border-radius:10px;display:flex;align-items:center;justify-content:center;margin:8px 0;position:relative;overflow:hidden}}.pin{{position:absolute;font-size:20px;animation:bounce 1s infinite}} @keyframes bounce{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-5px)}}}}
.step{{display:flex;gap:8px;margin:6px 0}}.dot{{width:18px;height:18px;border-radius:50%;background:#ddd;display:flex;align-items:center;justify-content:center;font-size:9px;flex-shrink:0}}.dot.active{{background:#0A8EA8;color:#fff}}.dot.done{{background:#00a651;color:#fff}}
.cart-item{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #eee;font-size:11px}}
</style></head><body>
<header><img src="/logo.png"><div class="nav"><button onclick="openAdmin()">📊 ADMIN</button><button onclick="openRider()">🏍️ RIDER</button><button onclick="openCart()">🛒 <span id="cartCount">0</span></button></div></header>
<div class="hero"><h1>🛒 LONMA ORBIT • 5 Stores • Rider in 30min</h1><p>Naivas | Quickmart | Carrefour | Chandarana | Magunas</p></div>
<div class="store-tabs"><button class="store-tab" onclick="filterStore('ALL')"><span style="background:#000">A</span>ALL</button>{store_tabs}</div>
<div class="section"><div class="cat-grid">{cat_cards}</div></div>
<div class="section"><h3>🔥 Best Deals Today</h3><div class="prod-grid" id="prodGrid">{prod_cards}</div></div>
<footer><img src="/logo.png"><p style="font-weight:900;font-size:11px;letter-spacing:1px">LONMA ORBIT SUPER APP • KAJIADO • 2026</p></footer>

<div id="cartModal" class="modal"><div class="box"><h3>🛒 Cart (<span id="cartNum">0</span>)</h3><div id="cartItems"></div><p style="font-weight:900;margin:8px 0">Total: KSH <span id="cartTotal">0</span> + Delivery KSH 100</p><input id="custName" placeholder="Your Name"><input id="custPhone" value="254" placeholder="M-Pesa Phone"><input id="custLocation" placeholder="Delivery Location e.g. Kajiado Town, House No."><select id="payMethod"><option value="mpesa">Lipa na M-Pesa</option><option value="cod">Cash on Delivery</option></select><button class="btn btn-green" onclick="checkout()">Order Now + Rider Delivery</button><button class="btn btn-gray" onclick="closeModals()">Continue Shopping</button><p id="checkoutStatus" style="text-align:center;font-weight:700;margin-top:6px;font-size:11px"></p><div id="tracking" style="display:none"><div class="map"><div class="pin" style="top:40%;left:45%">🏍️</div><div class="pin" style="top:60%;left:55%">📍</div><p style="font-size:10px;background:#fff;padding:4px 8px;border-radius:10px">Rider Live Location</p></div><div class="step"><div class="dot done">✓</div><div><b>Order Placed</b><p style="font-size:10px;color:#666">Order ID: <span id="orderId"></span></p></div></div><div class="step"><div class="dot active" id="dot2">2</div><div><b>Rider Assigned</b><p style="font-size:10px" id="riderAssigned">Finding nearest rider...</p></div></div><div class="step"><div class="dot" id="dot3">3</div><div><b>On The Way - <span id="eta">30 min</span></b><p style="font-size:10px" id="riderPhoneTrack"></p></div></div><div class="step"><div class="dot" id="dot4">4</div><div><b>Delivered ✓</b><p style="font-size:10px">Rate your rider</p></div></div><button class="btn btn-teal" onclick="openWhatsApp()">💬 WhatsApp Rider</button><button class="btn btn-black" onclick="openRider()">📍 Track Rider Live</button></div></div></div>

<div id="riderModal" class="modal"><div class="box"><h3>🏍️ Rider App</h3><input id="riderPhone" placeholder="Rider Phone 2547..."><button class="btn btn-teal" onclick="riderLogin()">Login as Rider</button><div id="riderProfile" style="margin-top:10px"></div><div id="riderStats" style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:10px 0"></div><div id="riderOrders"></div><button class="btn btn-gray" onclick="closeModals()">Close</button></div></div>

<div id="adminModal" class="modal"><div class="box"><h3>📊 Admin Dashboard</h3><div id="adminStats" style="display:grid;grid-template-columns:repeat(2,1fr);gap:6px;margin:10px 0"></div><h4 style="font-size:12px;margin-top:10px">📦 All Orders</h4><div id="adminOrders"></div><h4 style="font-size:12px;margin-top:10px">🏍️ Riders Performance</h4><div id="adminRiders"></div><button class="btn btn-gray" onclick="closeModals()">Close</button></div></div>

<script>
let cart=[], total=0, currentOrder=null;
function addToCart(id,name,price){{cart.push({{id,name,price}}); total+=price; document.getElementById('cartCount').innerText=cart.length;}}
function openCart(){{let d=document.getElementById('cartItems'); d.innerHTML=''; cart.forEach(c=>d.innerHTML+=`<div class="cart-item"><span>${{c.name}}</span><b>KSH ${{c.price}}</b></div>`); document.getElementById('cartNum').innerText=cart.length; document.getElementById('cartTotal').innerText=total; document.getElementById('cartModal').style.display='flex'}}
function openRider(){{document.getElementById('riderModal').style.display='flex'; loadRiders()}}
function openAdmin(){{document.getElementById('adminModal').style.display='flex'; loadAdmin()}}
function closeModals(){{document.querySelectorAll('.modal').forEach(m=>m.style.display='none')}}
async function checkout(){{let name=document.getElementById('custName').value; let phone=document.getElementById('custPhone').value; let loc=document.getElementById('custLocation').value; let method=document.getElementById('payMethod').value; if(!loc||!phone){{alert('Enter phone & location'); return}} document.getElementById('checkoutStatus').innerText=method=='mpesa'?'Sending M-Pesa...':'Placing order...'; let r=await fetch('/mpesa/stkpush',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{phone,amount:total+100,location:loc,cart,name,payment_method:method}})}}); let d=await r.json(); if(d.ResponseCode=='0'||method=='cod'){{currentOrder=d.order_id; document.getElementById('orderId').innerText=d.order_id; document.getElementById('checkoutStatus').innerText=method=='mpesa'?'✅ Check phone to pay!':'✅ Order placed - COD'; startTracking()}} else {{document.getElementById('checkoutStatus').innerText=d.error||'Error'}}}}
function startTracking(){{document.getElementById('tracking').style.display='block'; setTimeout(()=>{{document.getElementById('dot2').classList.add('done'); document.getElementById('dot2').innerText='✓'; document.getElementById('riderAssigned').innerText='John Mwangi • KMEZ 123A • 4.9★ • Kajiado'; document.getElementById('riderPhoneTrack').innerText='📞 0712345678 • On bike, 2.5km away'; document.getElementById('dot3').classList.add('active')}},2000); setTimeout(()=>{{document.getElementById('dot3').classList.add('done'); document.getElementById('dot3').innerText='✓'; document.getElementById('dot4').classList.add('active'); document.getElementById('eta').innerText='Delivered soon';}},6000)}}
function openWhatsApp(){{let msg=`Hi, I'm tracking order ${{currentOrder}}. Where are you?`; window.open(`https://wa.me/254712345678?text=${{encodeURIComponent(msg)}}`,'_blank')}}
async function loadRiders(){{let r=await fetch('/riders'); let riders=await r.json(); let h=''; riders.forEach(rd=>{{h+=`<div class="rider-card"><div><b>${{rd.name}} ⭐${{rd.rating}}</b><br><small>${{rd.motor}} • ${{rd.location}} • ${{rd.orders}} trips</small></div><span class="status ${{rd.status}}">${{rd.status}}</span></div>`}}); document.getElementById('riderProfile').innerHTML=h; let ro=await fetch('/orders'); let orders=await ro.json(); let oh=''; orders.slice(-10).forEach(o=>{{oh+=`<div class="order-card"><b>${{o.id}}</b> - KSH ${{o.amount}}<br><small>${{o.location}} • ${{o.phone}}</small><br><small>Status: ${{o.status}}</small><div style="display:flex;gap:4px;margin-top:6px"><button onclick="acceptOrder('${{o.id}}')" style="flex:1;padding:5px;background:#00a651;color:#fff;border:none;border-radius:6px;font-size:10px">Accept</button><button onclick="deliverOrder('${{o.id}}')" style="flex:1;padding:5px;background:#0A8EA8;color:#fff;border:none;border-radius:6px;font-size:10px">Delivered</button></div></div>`}}); document.getElementById('riderOrders').innerHTML='<h4 style="font-size:11px;margin:10px 0">Active Orders ('+orders.length+')</h4>'+oh; document.getElementById('riderStats').innerHTML=`<div style="background:#d4edda;padding:8px;border-radius:8px;text-align:center"><b>${{orders.length}}</b><br><small>Orders</small></div><div style="background:#cce5ff;padding:8px;border-radius:8px;text-align:center"><b>${{riders.filter(r=>r.status=='available').length}}</b><br><small>Available</small></div><div style="background:#fff3cd;padding:8px;border-radius:8px;text-align:center"><b>KSH ${{orders.reduce((s,o)=>s+o.amount,0)}}</b><br><small>Sales</small></div>`}}
async function loadAdmin(){{let r=await fetch('/orders'); let orders=await r.json(); let ridersRes=await fetch('/riders'); let riders=await ridersRes.json(); document.getElementById('adminStats').innerHTML=`<div style="background:#fff;padding:10px;border-radius:8px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1)"><b style="font-size:18px">${{orders.length}}</b><br><small>Total Orders</small></div><div style="background:#fff;padding:10px;border-radius:8px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1)"><b style="font-size:18px">KSH ${{orders.reduce((s,o)=>s+o.amount,0)}}</b><br><small>Revenue</small></div><div style="background:#fff;padding:10px;border-radius:8px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1)"><b style="font-size:18px">${{riders.length}}</b><br><small>Riders</small></div><div style="background:#fff;padding:10px;border-radius:8px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1)"><b style="font-size:18px">${{orders.filter(o=>o.status=='paid').length}}</b><br><small>Pending</small></div>`; let oh=''; orders.slice(-10).forEach(o=>oh+=`<div class="order-card"><b>${{o.id}}</b> - KSH ${{o.amount}} - ${{o.status}}<br><small>${{o.location}} | ${{o.phone}}</small></div>`); document.getElementById('adminOrders').innerHTML=oh; let rh=''; riders.forEach(rd=>rh+=`<div class="rider-card"><div><b>${{rd.name}}</b> - ⭐${{rd.rating}}<br><small>${{rd.orders}} deliveries</small></div><span class="status ${{rd.status}}">${{rd.status}}</span></div>`); document.getElementById('adminRiders').innerHTML=rh}}
async function riderLogin(){{let phone=document.getElementById('riderPhone').value; alert('Rider '+phone+' logged in!'); loadRiders()}}
async function acceptOrder(id){{await fetch('/rider/accept/'+id,{{method:'POST'}}); alert('Accepted '+id); loadRiders(); loadAdmin()}}
async function deliverOrder(id){{await fetch('/rider/deliver/'+id,{{method:'POST'}}); alert('Delivered '+id+'! Customer notified.'); loadRiders(); loadAdmin()}}
function filterStore(s){{document.querySelectorAll('.prod-card').forEach(c=>c.style.display=(s=='ALL'||c.dataset.store==s)?'block':'none')}}
function filterCat(c){{document.querySelectorAll('.prod-card').forEach(p=>p.style.display=p.dataset.cat==c?'block':'none')}}
</script></body></html>
'''

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    try:
        b=await req.json(); order_id=f"ORD{random.randint(1000,9999)}"; ORDERS.append({"id":order_id,"phone":b.get("phone"),"amount":b.get("amount",1),"location":b.get("location","Kajiado"),"cart":b.get("cart",[]),"name":b.get("name","Customer"),"status":"paid","rider":random.choice(RIDERS)["name"],"payment_method":b.get("payment_method","mpesa"),"time":datetime.now().isoformat()})
        token=get_token()
        if not token: return {"ResponseCode":"0","order_id":order_id,"message":"COD Order saved"}
        ts=datetime.now().strftime("%Y%m%d%H%M%S"); pwd=base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{ts}".encode()).decode()
        url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        r=requests.post(url,json={"BusinessShortCode":MPESA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":int(b.get("amount",1)),"PartyA":b.get("phone"),"PartyB":MPESA_SHORTCODE,"PhoneNumber":b.get("phone"),"CallBackURL":MPESA_CALLBACK_URL,"AccountReference":order_id,"TransactionDesc":"LONMA"},headers={"Authorization":f"Bearer {token}"},timeout=10)
        data=r.json(); data["order_id"]=order_id; return data
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
@app.post("/rider/deliver/{order_id}")
async def deliver(order_id: str):
    for o in ORDERS:
        if o["id"]==order_id: o["status"]="delivered"
    return {"success":True}
@app.get("/mpesa/callback")
async def cb_get(): return {"ResultCode":0,"ResultDesc":"OK"}
@app.post("/mpesa/callback")
async def cb_post(req: Request): print(await req.json());return {"ResultCode":0,"ResultDesc":"Accepted"}
@app.get("/logo.png")
async def logo(): return FileResponse("logo.png") if os.path.exists("logo.png") else {"error":"logo.png missing"}
@app.get("/favicon.ico")
async def fav(): return FileResponse("logo.png") if os.path.exists("logo.png") else {}
@app.get("/admin")
async def admin_redirect(): return HTMLResponse('<script>window.location.href="/"</script>')
