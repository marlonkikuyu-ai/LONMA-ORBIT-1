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
        if not MPESA_CONSUMER_KEY or not MPESA_CONSUMER_SECRET:
            return None
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        r = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET), timeout=10)
        return r.json().get("access_token")
    except:
        return None

STORES=[{"id":"naivas","name":"NAIVAS","color":"#008000"},{"id":"quickmart","name":"QUICKMART","color":"#FF0000"},{"id":"carrefour","name":"CARREFOUR","color":"#0047AB"},{"id":"chandarana","name":"CHANDARANA","color":"#FF8C00"},{"id":"magunas","name":"MAGUNAS","color":"#800080"}]
PRODUCTS=[
    {"id":1,"name":"Ajab Maize Flour 2kg","price":175,"store":"naivas","category":"grocery","stock":50,"desc":"Best for ugali, fortified"},
    {"id":2,"name":"Brookside Milk 500ml","price":65,"store":"naivas","category":"dairy","stock":100,"desc":"Fresh milk daily"},
    {"id":3,"name":"Coca Cola 1.25L","price":100,"store":"quickmart","category":"beverages","stock":80,"desc":"Chilled coke"},
    {"id":4,"name":"Omo Detergent 1kg","price":285,"store":"carrefour","category":"household","stock":40,"desc":"Removes tough stains"},
    {"id":5,"name":"Tomatoes 1kg","price":80,"store":"quickmart","category":"fresh","stock":60,"desc":"Fresh from farm"},
    {"id":6,"name":"White Bread 400g","price":60,"store":"naivas","category":"dairy","stock":70,"desc":"Soft bread"},
    {"id":7,"name":"Pishori Rice 2kg","price":350,"store":"carrefour","category":"grocery","stock":30,"desc":"Premium rice"},
    {"id":8,"name":"Geisha Soap 150g","price":55,"store":"magunas","category":"personal","stock":90,"desc":"Beauty soap"},
]
RIDERS=[
    {"id":1,"name":"John Mwangi","phone":"254712345678","motor":"KMEZ 123A","status":"available","orders":12,"rating":4.9,"location":"Kajiado"},
    {"id":2,"name":"Peter Ochieng","phone":"254723456789","motor":"KMFA 456B","status":"delivering","orders":28,"rating":4.8,"location":"Kitengela"},
    {"id":3,"name":"Samuel Kiprop","phone":"254734567890","motor":"KMEB 789C","status":"available","orders":15,"rating":5.0,"location":"Rongai"},
]
ORDERS=[]
CHAT_HISTORY=[]

def ai_response(message):
    msg = message.lower()
    if any(word in msg for word in ["flour","maize","ajab"]):
        return "We have Ajab Maize Flour 2kg at KES 175 at Naivas. The cheapest is KES 172 at Carrefour. 50 packs in stock. Would you like me to add it to your cart?"
    if "milk" in msg:
        return "Brookside Milk 500ml is KES 65 at Naivas (100 in stock) and KES 62 at Chandarana - fresh daily. Would you like to add it to your cart?"
    if "bread" in msg:
        return "White Bread 400g is KES 60 at Naivas - soft and fresh. 70 loaves available. Goes well with milk!"
    if "soda" in msg or "coke" in msg or "drink" in msg:
        return "Coca Cola 1.25L is KES 100 at Quickmart and KES 99 at Magunas. Chilled! 80 bottles available."
    if "price" in msg or "compare" in msg or "cheap" in msg:
        return "I compare prices across 5 stores: Naivas, Quickmart, Carrefour, Chandarana, and Magunas. Tell me what you need and I will find the cheapest price."
    if "rider" in msg or "delivery" in msg or "how long" in msg:
        return "Rider delivery takes 30 minutes within Kajiado, Kitengela, and Rongai. Delivery fee is KES 100. 3 riders available: John (4.9 stars), Peter (4.8), Samuel (5.0). Order now!"
    if "tomato" in msg:
        return "Fresh Tomatoes 1kg is KES 80 at Quickmart - farm fresh. 60kg available today."
    if "omo" in msg or "detergent" in msg:
        return "Omo Detergent 1kg is KES 285 at Carrefour (cheapest) vs KES 290 at Naivas. 40 packs left."
    if "hello" in msg or "hi" in msg:
        return "Hello! I am LONMA AI - your supermarket assistant. I can find cheapest prices, check stock, track rider, and recommend products. What do you need today?"
    if "cart" in msg or "order" in msg:
        return "Add products by clicking Add, then click the cart icon top right to checkout. You can pay M-Pesa or Cash on Delivery. Delivery in 30 minutes!"
    if "stock" in msg:
        stock_list = ", ".join([f"{p['name']} ({p['stock']} left)" for p in PRODUCTS[:4]])
        return f"Current stock: {stock_list}. Which item do you need?"
    if "help" in msg:
        return "I can help you with:\n- Finding products: say 'flour' or 'milk'\n- Comparing prices: 'cheapest soda'\n- Delivery: 'rider delivery time'\n- Tracking: 'where is my order'\n- Recipes: 'what to cook with tomatoes'\nWhat do you need?"
    found = [p for p in PRODUCTS if any(w in p["name"].lower() for w in msg.split())]
    if found:
        p = found[0]
        return f"Found {p['name']} - KES {p['price']} at {p['store'].upper()} ({p['stock']} in stock). {p['desc']}. Add to cart?"
    return "I did not understand that. Try: 'cheapest flour', 'milk price', 'rider delivery time', 'what is in stock', or 'help'."

@app.get("/", response_class=HTMLResponse)
async def home():
    store_tabs="".join([f'<button class="store-tab" onclick="filterStore(\'{s["id"]}\')"><span style="background:{s["color"]}">{s["name"][0]}</span>{s["name"]}</button>' for s in STORES])
    prod_cards="".join([f'<div class="prod-card" data-store="{p["store"]}" data-name="{p["name"].lower()}"><img src="https://via.placeholder.com/300/f0f0f0/000?text={p["name"].replace(" ","+")}" alt=""><div class="store-badge" style="background:{[s["color"] for s in STORES if s["id"]==p["store"]][0]}">{p["store"].upper()}</div><h4>{p["name"]}</h4><p style="font-size:9px;color:#666">{p["desc"]}</p><div class="price-row"><span class="price">KES {p["price"]}</span><button onclick="addToCart({p["id"]},\'{p["name"]}\',{p["price"]})">Add</button></div></div>' for p in PRODUCTS])
    return f'''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{font-family:Arial;background:#f5f6fa}} header{{background:#0A8EA8;padding:10px 15px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100}} header img{{height:50px}}.nav{{display:flex;gap:5px}}.nav button{{padding:6px 9px;background:#fff;color:#0A8EA8;border:none;border-radius:16px;font-weight:900;font-size:9px;cursor:pointer}}
.store-tabs{{display:flex;gap:6px;overflow-x:auto;padding:8px 12px;background:#fff;border-bottom:1px solid #eee}}.store-tab{{display:flex;align-items:center;gap:4px;padding:5px 8px;border:1.5px solid #ddd;border-radius:16px;background:#fff;white-space:nowrap;font-weight:900;font-size:9px;cursor:pointer}}.store-tab span{{width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff}}
.section{{padding:12px}}.section h3{{font-size:13px;font-weight:900;margin-bottom:8px}}
.prod-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:6px}}.prod-card{{background:#fff;border-radius:10px;padding:6px;position:relative;box-shadow:0 1px 3px rgba(0,0,0,0.05)}}.prod-card img{{width:100%;border-radius:6px;aspect-ratio:1;object-fit:cover}}.store-badge{{position:absolute;top:6px;left:6px;font-size:7px;padding:2px 5px;border-radius:5px;font-weight:900;color:#fff}}.prod-card h4{{font-size:10px;margin:4px 0}}.price-row{{display:flex;justify-content:space-between;align-items:center;margin-top:4px}}.price{{font-weight:900;color:#0A8EA8;font-size:11px}}.price-row button{{padding:4px 8px;background:#000;color:#fff;border:none;border-radius:10px;font-weight:700;font-size:9px}}
#aiBtn{{position:fixed;bottom:20px;right:15px;width:60px;height:60px;background:#0A8EA8;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;box-shadow:0 4px 12px rgba(0,0,0,0.3);cursor:pointer;z-index:150;animation:pulse 2s infinite}} @keyframes pulse{{0%{{transform:scale(1)}}50%{{transform:scale(1.05)}}100%{{transform:scale(1)}}}}
#aiChat{{display:none;position:fixed;bottom:85px;right:10px;width:92%;max-width:360px;height:70vh;background:#fff;border-radius:16px;box-shadow:0 8px 24px rgba(0,0,0,0.3);z-index:150;flex-direction:column;overflow:hidden}} #aiChat.open{{display:flex}}
.ai-header{{background:#0A8EA8;color:#fff;padding:12px 15px;display:flex;justify-content:space-between;align-items:center}}.ai-header h4{{font-size:13px}}.ai-messages{{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px;background:#f8f9fa}}.msg{{max-width:82%;padding:9px 12px;border-radius:14px;font-size:12px;line-height:1.4}}.msg.user{{align-self:flex-end;background:#0A8EA8;color:#fff;border-bottom-right-radius:4px}}.msg.bot{{align-self:flex-start;background:#fff;border:1px solid #e0e0e0;border-bottom-left-radius:4px}}.ai-input{{display:flex;gap:6px;padding:10px;border-top:1px solid #eee;background:#fff}}.ai-input input{{flex:1;padding:10px 12px;border-radius:20px;border:1px solid #ddd;font-size:12px}}.ai-input button{{padding:10px 14px;background:#0A8EA8;color:#fff;border:none;border-radius:20px;font-weight:900;font-size:12px}}
.quick{{display:flex;gap:5px;flex-wrap:wrap;margin-top:6px}}.quick button{{padding:5px 9px;background:#e0f7fa;color:#0A8EA8;border:1px solid #0A8EA8;border-radius:12px;font-size:9px;font-weight:700;cursor:pointer}}
footer{{background:#000;color:#fff;padding:12px;text-align:center}} footer img{{height:40px}}
.modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);justify-content:center;align-items:center;z-index:200;padding:10px}}.box{{background:#fff;padding:14px;border-radius:12px;width:100%;max-width:380px;max-height:90vh;overflow-y:auto}}.box input,.box select{{width:100%;padding:10px;margin:6px 0;border-radius:8px;border:1px solid #ddd;font-size:12px}}.btn{{width:100%;padding:11px;border:none;border-radius:8px;font-weight:900;cursor:pointer;margin-top:6px;font-size:12px}}.btn-green{{background:#00a651;color:#fff}}.btn-teal{{background:#0A8EA8;color:#fff}}.btn-gray{{background:#eee}}
</style></head><body>
<header><img src="/logo.png"><div class="nav"><button onclick="openAdmin()">ADMIN</button><button onclick="openRider()">RIDER</button><button onclick="openCart()">CART <span id="cartCount">0</span></button></div></header>
<div class="store-tabs"><button class="store-tab" onclick="filterStore('ALL')"><span style="background:#000">A</span>ALL</button>{store_tabs}</div>
<div class="section"><h3>Best Deals - Rider Delivery in 30 Minutes</h3><div class="prod-grid" id="prodGrid">{prod_cards}</div></div>
<footer><img src="/logo.png"><p style="font-weight:900;font-size:11px">LONMA ORBIT - AI POWERED - 2026</p></footer>
<div id="aiBtn" onclick="toggleAI()">🤖</div>
<div id="aiChat"><div class="ai-header"><div><h4>🤖 LONMA AI Assistant</h4><small>Online - Knows 5 supermarkets + rider</small></div><button onclick="toggleAI()" style="background:rgba(255,255,255,0.2);border:none;color:#fff;padding:6px 10px;border-radius:10px;font-weight:900">X</button></div><div class="ai-messages" id="aiMessages"><div class="msg bot">Hello! I am your AI shopping assistant!<br><br>I check prices from Naivas, Quickmart, Carrefour, Chandarana and Magunas.<br><br>Try asking:<br>- "cheapest flour"<br>- "milk price"<br>- "rider how long"<br>- "what to cook"<div class="quick"><button onclick="askAI('cheapest flour')">Cheapest Flour</button><button onclick="askAI('milk price')">Milk Price</button><button onclick="askAI('rider delivery')">Rider Time</button><button onclick="askAI('help')">Help</button></div></div></div><div class="ai-input"><input id="aiInput" placeholder="Ask me anything... e.g. cheapest flour" onkeypress="if(event.key==='Enter') sendAI()"><button onclick="sendAI()">Send</button></div></div>
<div id="cartModal" class="modal"><div class="box"><h3>Cart (<span id="cartNum">0</span>)</h3><div id="cartItems"></div><p style="font-weight:900;margin:8px 0">Total: KES <span id="cartTotal">0</span> + KES 100 delivery</p><input id="custName" placeholder="Your Name"><input id="custPhone" value="254" placeholder="M-Pesa Phone"><input id="custLocation" placeholder="Delivery Location"><select id="payMethod"><option value="mpesa">M-Pesa</option><option value="cod">Cash on Delivery</option></select><button class="btn btn-green" onclick="checkout()">Order Now</button><button class="btn btn-gray" onclick="closeModals()">Continue Shopping</button><p id="checkoutStatus" style="text-align:center;font-weight:700;font-size:11px;margin-top:6px"></p><div id="tracking" style="display:none"><p style="font-weight:900">Tracking: <span id="orderId"></span></p><p style="font-size:11px" id="riderAssigned">Finding rider...</p></div></div></div>
<div id="riderModal" class="modal"><div class="box"><h3>Rider App</h3><input id="riderPhone" placeholder="Rider Phone 2547..."><button class="btn btn-teal" onclick="loadRiders()">Login</button><div id="riderProfile"></div><div id="riderOrders"></div><button class="btn btn-gray" onclick="closeModals()">Close</button></div></div>
<div id="adminModal" class="modal"><div class="box"><h3>Admin Dashboard</h3><div id="adminStats" style="display:grid;grid-template-columns:repeat(2,1fr);gap:6px"></div><div id="adminOrders"></div><button class="btn btn-gray" onclick="closeModals()">Close</button></div></div>
<script>
let cart=[], total=0, currentOrder=null;
function addToCart(id,name,price){{cart.push({{id,name,price}}); total+=price; document.getElementById('cartCount').innerText=cart.length;}}
function openCart(){{let d=document.getElementById('cartItems'); d.innerHTML=''; cart.forEach(c=>d.innerHTML+=`<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #eee;font-size:11px"><span>${{c.name}}</span><b>KES ${{c.price}}</b></div>`); document.getElementById('cartNum').innerText=cart.length; document.getElementById('cartTotal').innerText=total; document.getElementById('cartModal').style.display='flex'}}
function openRider(){{document.getElementById('riderModal').style.display='flex'; loadRiders()}}
function openAdmin(){{document.getElementById('adminModal').style.display='flex'; loadAdmin()}}
function closeModals(){{document.querySelectorAll('.modal').forEach(m=>m.style.display='none')}}
async function checkout(){{let phone=document.getElementById('custPhone').value; let loc=document.getElementById('custLocation').value; if(!loc){{alert('Enter location'); return}} let r=await fetch('/mpesa/stkpush',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{phone,amount:total+100,location:loc,cart}})}}); let d=await r.json(); document.getElementById('orderId').innerText=d.order_id; document.getElementById('checkoutStatus').innerText='Order '+d.order_id+' placed!'; document.getElementById('tracking').style.display='block'; document.getElementById('riderAssigned').innerText='Rider John KMEZ 123A assigned - 30 minutes';}}
function toggleAI(){{let c=document.getElementById('aiChat'); c.classList.toggle('open')}}
function askAI(text){{document.getElementById('aiInput').value=text; sendAI()}}
async function sendAI(){{let input=document.getElementById('aiInput'); let msg=input.value.trim(); if(!msg) return; let box=document.getElementById('aiMessages'); box.innerHTML+=`<div class="msg user">${{msg}}</div>`; input.value=''; box.scrollTop=box.scrollHeight; let r=await fetch('/ai/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:msg,cart:cart}})}}); let data=await r.json(); box.innerHTML+=`<div class="msg bot">${{data.reply}}${{data.quick?'<div class="quick">'+data.quick.map(q=>`<button onclick="askAI('${{q}}')">${{q}}</button>`).join('')+'</div>':''}}</div>`; box.scrollTop=box.scrollHeight}}
async function loadRiders(){{let r=await fetch('/riders'); let riders=await r.json(); let h=''; riders.forEach(rd=>h+=`<div style="background:#fff;padding:8px;border-radius:8px;margin:6px 0;border-left:3px solid #0A8EA8"><b>${{rd.name}} - ${{rd.rating}} stars</b><br><small>${{rd.motor}} - ${{rd.location}}</small></div>`); document.getElementById('riderProfile').innerHTML=h; let ro=await fetch('/orders'); let orders=await ro.json(); let oh=''; orders.slice(-5).forEach(o=>oh+=`<div style="background:#fff;padding:8px;border-radius:8px;margin:6px 0"><b>${{o.id}}</b> KES ${{o.amount}}<br><small>${{o.location}}</small> <button onclick="acceptOrder('${{o.id}}')" style="padding:4px 8px;background:#00a651;color:#fff;border:none;border-radius:6px;font-size:10px;float:right">Accept</button></div>`); document.getElementById('riderOrders').innerHTML=oh}}
async function loadAdmin(){{let r=await fetch('/orders'); let orders=await r.json(); document.getElementById('adminStats').innerHTML=`<div style="background:#fff;padding:10px;border-radius:8px;text-align:center"><b>${{orders.length}}</b><br><small>Orders</small></div><div style="background:#fff;padding:10px;border-radius:8px;text-align:center"><b>KES ${{orders.reduce((s,o)=>s+o.amount,0)}}</b><br><small>Sales</small></div>`; let oh=''; orders.slice(-5).forEach(o=>oh+=`<div style="background:#fff;padding:8px;border-radius:8px;margin:4px 0"><small>${{o.id}} - ${{o.amount}} - ${{o.location}}</small></div>`); document.getElementById('adminOrders').innerHTML=oh}}
async function acceptOrder(id){{await fetch('/rider/accept/'+id,{{method:'POST'}}); alert('Accepted '+id); loadRiders()}}
function filterStore(s){{document.querySelectorAll('.prod-card').forEach(c=>c.style.display=(s=='ALL'||c.dataset.store==s)?'block':'none')}}
</script></body></html>
'''

@app.post("/ai/chat")
async def ai_chat(req: Request):
    try:
        b=await req.json()
        msg=b.get("message","")
        reply = ai_response(msg)
        quick = []
        if "flour" in msg.lower():
            quick = ["Add flour to cart","milk price","cheapest rice"]
        elif "milk" in msg.lower():
            quick = ["Add milk to cart","bread price","cheapest flour"]
        elif "rider" in msg.lower():
            quick = ["Track order","delivery fee","help"]
        else:
            quick = ["cheapest flour","milk price","rider delivery","help"]
        CHAT_HISTORY.append({"user":msg,"bot":reply,"time":datetime.now().isoformat()})
        return {"reply":reply.replace("\n","<br>"),"quick":quick}
    except Exception as e:
        return {"reply":f"Error: {str(e)}","quick":["help","cheapest flour"]}

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    try:
        b=await req.json()
        order_id=f"ORD{random.randint(1000,9999)}"
        ORDERS.append({"id":order_id,"phone":b.get("phone"),"amount":b.get("amount",1),"location":b.get("location","Kajiado"),"cart":b.get("cart",[]),"status":"paid","time":datetime.now().isoformat()})
        token=get_token()
        if not token:
            return {"ResponseCode":"0","order_id":order_id}
        ts=datetime.now().strftime("%Y%m%d%H%M%S")
        pwd=base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{ts}".encode()).decode()
        url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        r=requests.post(url,json={"BusinessShortCode":MPESA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":int(b.get("amount",1)),"PartyA":b.get("phone"),"PartyB":MPESA_SHORTCODE,"PhoneNumber":b.get("phone"),"CallBackURL":MPESA_CALLBACK_URL,"AccountReference":order_id,"TransactionDesc":"LONMA"},headers={"Authorization":f"Bearer {token}"},timeout=10)
        data=r.json()
        data["order_id"]=order_id
        return data
    except Exception as e:
        return {"error":str(e),"ResponseCode":"1"}

@app.get("/riders")
async def get_riders():
    return RIDERS

@app.get("/orders")
async def get_orders():
    return ORDERS[::-1]

@app.get("/ai/history")
async def history():
    return CHAT_HISTORY[::-1][:20]

@app.post("/rider/accept/{order_id}")
async def accept(order_id: str):
    for o in ORDERS:
        if o["id"]==order_id:
            o["status"]="rider_assigned"
    return {"success":True}

@app.get("/mpesa/callback")
async def cb_get():
    return {"ResultCode":0,"ResultDesc":"OK"}

@app.post("/mpesa/callback")
async def cb_post(req: Request):
    return {"ResultCode":0,"ResultDesc":"Accepted"}

@app.get("/logo.png")
async def logo():
    return FileResponse("logo.png") if os.path.exists("logo.png") else {"error":"logo.png missing"}

@app.get("/favicon.ico")
async def fav():
    return FileResponse("logo.png") if os.path.exists("logo.png") else {}
