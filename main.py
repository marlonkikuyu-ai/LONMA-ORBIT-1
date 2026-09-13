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

STORES=[{"id":"naivas","name":"NAIVAS","icon":"🟢","color":"#008000"},{"id":"quickmart","name":"QUICKMART","icon":"🔴","color":"#E30613"},{"id":"carrefour","name":"CARREFOUR","icon":"🔵","color":"#0047AB"},{"id":"chandarana","name":"CHANDARANA","icon":"🟠","color":"#FF8C00"},{"id":"magunas","name":"MAGUNAS","icon":"🟣","color":"#800080"}]
CATEGORIES=[{"id":"all","name":"All","icon":"🏪"},{"id":"fresh","name":"Fresh Food","icon":"🥬"},{"id":"grocery","name":"Grocery","icon":"🌽"},{"id":"beverages","name":"Beverages","icon":"🥤"},{"id":"dairy","name":"Dairy","icon":"🥛"},{"id":"household","name":"Household","icon":"🧹"},{"id":"personal","name":"Personal Care","icon":"🧴"},{"id":"baby","name":"Baby","icon":"👶"}]
PRODUCTS=[
    {"id":1,"name":"Ajab Maize Flour 2kg","price":175,"old_price":190,"store":"naivas","cat":"grocery","stock":50,"rating":4.8,"sold":234,"desc":"Best for ugali","image":"flour"},
    {"id":2,"name":"Brookside Milk 500ml","price":65,"old_price":70,"store":"naivas","cat":"dairy","stock":100,"rating":4.9,"sold":512,"desc":"Fresh daily milk","image":"milk"},
    {"id":3,"name":"Coca Cola 1.25L","price":100,"old_price":120,"store":"quickmart","cat":"beverages","stock":80,"rating":4.7,"sold":320,"desc":"Chilled soft drink","image":"coke"},
    {"id":4,"name":"Omo Detergent 1kg","price":285,"old_price":320,"store":"carrefour","cat":"household","stock":40,"rating":4.6,"sold":89,"desc":"Removes stains","image":"omo"},
    {"id":5,"name":"Tomatoes 1kg","price":80,"old_price":100,"store":"quickmart","cat":"fresh","stock":60,"rating":4.9,"sold":445,"desc":"Farm fresh","image":"tomato"},
    {"id":6,"name":"White Bread 400g","price":60,"old_price":65,"store":"naivas","cat":"dairy","stock":70,"rating":4.8,"sold":210,"desc":"Soft fresh bread","image":"bread"},
    {"id":7,"name":"Pishori Rice 2kg","price":350,"old_price":400,"store":"carrefour","cat":"grocery","stock":30,"rating":4.9,"sold":156,"desc":"Premium rice","image":"rice"},
    {"id":8,"name":"Geisha Soap 150g","price":55,"old_price":60,"store":"magunas","cat":"personal","stock":90,"rating":4.5,"sold":98,"desc":"Beauty soap","image":"soap"},
    {"id":9,"name":"Kabras Sugar 2kg","price":280,"old_price":300,"store":"chandarana","cat":"grocery","stock":45,"rating":4.7,"sold":167,"desc":"Sweet sugar","image":"sugar"},
    {"id":10,"name":"Eggs Tray 30pcs","price":420,"old_price":450,"store":"quickmart","cat":"fresh","stock":25,"rating":4.9,"sold":89,"desc":"Farm eggs","image":"eggs"},
    {"id":11,"name":"Cooking Oil 2L","price":380,"old_price":420,"store":"naivas","cat":"grocery","stock":35,"rating":4.8,"sold":134,"desc":"Fortified oil","image":"oil"},
    {"id":12,"name":"Pampers Baby Diapers","price":850,"old_price":950,"store":"carrefour","cat":"baby","stock":20,"rating":4.9,"sold":67,"desc":"Size 3, 30pcs","image":"diapers"},
]
RIDERS=[{"id":1,"name":"John Mwangi","phone":"254712345678","motor":"KMEZ 123A","status":"available","orders":12,"rating":4.9,"location":"Kajiado"},{"id":2,"name":"Peter Ochieng","phone":"254723456789","motor":"KMFA 456B","status":"delivering","orders":28,"rating":4.8,"location":"Kitengela"},{"id":3,"name":"Samuel Kiprop","phone":"254734567890","motor":"KMEB 789C","status":"available","orders":15,"rating":5.0,"location":"Rongai"}]
ORDERS=[]

def ai_response(msg):
    m=msg.lower()
    if "flour" in m: return "We have Ajab Maize Flour 2kg at KES 175 at Naivas (cheapest KES 172 at Carrefour). 50 packs in stock. Add to cart?"
    if "milk" in m: return "Brookside Milk 500ml is KES 65 at Naivas and KES 62 at Chandarana - fresh daily. 100 in stock."
    if "rider" in m or "delivery" in m: return "Rider delivery in 30 minutes within Kajiado, Kitengela, Rongai. Fee KES 100. 3 riders available."
    if "hello" in m or "hi" in m: return "Hello! I am LONMA AI. I compare prices from 5 supermarkets, check stock, and track riders. What do you need?"
    if "help" in m: return "Ask me: 'cheapest flour', 'milk price', 'rider time', 'what is in stock', 'compare prices'"
    found=[p for p in PRODUCTS if any(w in p["name"].lower() for w in m.split())]
    if found: p=found[0]; return f"Found {p['name']} - KES {p['price']} at {p['store'].upper()} ({p['stock']} left). Rating {p['rating']} stars. Add to cart?"
    return "Try: 'cheapest flour', 'milk price', 'rider delivery', 'help'"

@app.get("/", response_class=HTMLResponse)
async def home():
    return '''
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><title>LONMA ORBIT - Super App</title>
<style>
*{margin:0;padding:0;box-sizing:border-box} body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial;background:#f2f3f7;padding-bottom:80px}
.top-bar{background:#0A8EA8;padding:10px 16px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;color:#fff}
.top-bar.left{display:flex;align-items:center;gap:10px}.top-bar img{height:36px;background:#fff;border-radius:8px;padding:2px}
.top-bar.location{font-size:11px;line-height:1.2}.top-bar.location b{font-size:13px;display:block}
.top-bar.right{display:flex;gap:8px}.top-bar.icon-btn{width:36px;height:36px;background:rgba(255,255,255,0.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;cursor:pointer}
.search-bar{padding:10px 16px;background:#0A8EA8;display:flex;gap:8px}
.search-bar.input{flex:1;background:#fff;border-radius:12px;padding:10px 14px;display:flex;align-items:center;gap:8px}
.search-bar input{border:none;outline:none;flex:1;font-size:13px}.search-bar.filter{width:44px;height:44px;background:#000;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px}
.banner{margin:12px 16px;background:linear-gradient(135deg,#0A8EA8,#00c6a7);border-radius:16px;padding:16px;color:#fff;display:flex;justify-content:space-between;align-items:center}
.banner h2{font-size:16px;line-height:1.2}.banner p{font-size:11px;opacity:0.9;margin-top:4px}.banner.badge{background:#fff;color:#0A8EA8;padding:8px 14px;border-radius:20px;font-weight:900;font-size:11px}
.store-row{display:flex;gap:10px;overflow-x:auto;padding:0 16px 8px;scrollbar-width:none}.store-row::-webkit-scrollbar{display:none}
.store-chip{min-width:90px;background:#fff;border-radius:14px;padding:10px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);cursor:pointer;border:2px solid transparent}.store-chip.active{border-color:#0A8EA8}.store-chip.icon{font-size:22px}.store-chip b{font-size:10px;display:block;margin-top:4px}.store-chip small{font-size:9px;color:#666}
.cat-row{display:flex;gap:10px;overflow-x:auto;padding:8px 16px;scrollbar-width:none}.cat-row::-webkit-scrollbar{display:none}
.cat-chip{min-width:68px;text-align:center;cursor:pointer}.cat-chip.ic{width:56px;height:56px;background:#fff;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);margin:0 auto}.cat-chip.active.ic{background:#0A8EA8;color:#fff}.cat-chip b{font-size:10px;margin-top:6px;display:block}
.section{padding:12px 16px}.section-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}.section-head h3{font-size:15px;font-weight:800}.section-head a{font-size:11px;color:#0A8EA8;font-weight:700;text-decoration:none}
.prod-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.06);position:relative}
.card.img{height:120px;background:linear-gradient(135deg,#f0f0f0,#e0e0e0);display:flex;align-items:center;justify-content:center;font-size:32px;position:relative}
.card.off{position:absolute;top:8px;left:8px;background:#ff3b30;color:#fff;font-size:9px;font-weight:800;padding:3px 6px;border-radius:6px}
.card.fav{position:absolute;top:8px;right:8px;width:26px;height:26px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(0,0,0,0.1);cursor:pointer}
.card.info{padding:10px}.card.store{font-size:8px;font-weight:800;color:#0A8EA8;letter-spacing:0.5px}.card h4{font-size:11px;font-weight:700;margin:3px 0;line-height:1.3;height:28px;overflow:hidden}.card.meta{display:flex;gap:6px;font-size:9px;color:#888;margin:4px 0}.card.meta span{display:flex;align-items:center;gap:2px}
.card.price-row{display:flex;justify-content:space-between;align-items:center;margin-top:6px}.card.price b{font-size:13px}.card.price small{font-size:9px;color:#999;text-decoration:line-through;margin-left:4px}.card.add{width:30px;height:30px;background:#000;color:#fff;border:none;border-radius:9px;font-size:16px;font-weight:900;cursor:pointer}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #eee;display:flex;justify-content:space-around;padding:8px 0 12px;z-index:100}
.bottom-nav.tab{text-align:center;cursor:pointer;flex:1}.bottom-nav.tab.ic{font-size:22px}.bottom-nav.tab.active{color:#0A8EA8}.bottom-nav.tab b{font-size:9px;display:block;margin-top:2px}.bottom-nav.cart-badge{position:absolute;top:-6px;right:18px;background:#ff3b30;color:#fff;font-size:9px;font-weight:800;width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center}
#aiBtn{position:fixed;bottom:85px;right:16px;width:56px;height:56px;background:#0A8EA8;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:26px;box-shadow:0 6px 20px rgba(10,142,168,0.4);cursor:pointer;z-index:90}
#aiChat{display:none;position:fixed;bottom:150px;right:12px;left:12px;max-width:400px;margin:0 auto;height:60vh;background:#fff;border-radius:20px;box-shadow:0 12px 40px rgba(0,0,0,0.2);z-index:95;flex-direction:column;overflow:hidden} #aiChat.open{display:flex}
.ai-h{background:#0A8EA8;color:#fff;padding:14px 16px;display:flex;justify-content:space-between;align-items:center}.ai-msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:#f8f9fa}.msg{max-width:80%;padding:10px 14px;border-radius:16px;font-size:12px;line-height:1.4}.msg.user{align-self:flex-end;background:#0A8EA8;color:#fff;border-bottom-right-radius:4px}.msg.bot{align-self:flex-start;background:#fff;border:1px solid #eee;border-bottom-left-radius:4px}.ai-in{display:flex;gap:8px;padding:12px;border-top:1px solid #eee;background:#fff}.ai-in input{flex:1;padding:12px 14px;border-radius:24px;border:1px solid #ddd;font-size:12px;outline:none}.ai-in button{padding:12px 16px;background:#0A8EA8;color:#fff;border:none;border-radius:24px;font-weight:800}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);backdrop-filter:blur(4px);justify-content:center;align-items:end;z-index:200}.modal.open{display:flex}
.sheet{background:#fff;width:100%;max-width:480px;margin:0 auto;border-radius:24px 24px 0 0;max-height:85vh;overflow-y:auto;animation:slideUp 0.3s} @keyframes slideUp{from{transform:translateY(100%)}to{transform:translateY(0)}}
.sheet-h{padding:16px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #eee;position:sticky;top:0;background:#fff;border-radius:24px 24px 0 0;z-index:1}.sheet-c{padding:16px}
.btn{width:100%;padding:14px;border:none;border-radius:14px;font-weight:800;font-size:13px;cursor:pointer;margin-top:10px}.btn-black{background:#000;color:#fff}.btn-teal{background:#0A8EA8;color:#fff}.btn-green{background:#00a651;color:#fff}.btn-gray{background:#f2f3f7;color:#333}
.input{width:100%;padding:12px 14px;border-radius:12px;border:1px solid #e0e0e0;font-size:13px;margin:6px 0;outline:none}.input:focus{border-color:#0A8EA8}
.cart-item{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid #f0f0f0}.cart-item.img{width:56px;height:56px;background:#f5f5f5;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px}.cart-item.info{flex:1}.cart-item h4{font-size:12px}.cart-item.qty{display:flex;align-items:center;gap:8px;margin-top:6px}.cart-item.qty button{width:26px;height:26px;border-radius:8px;border:1px solid #ddd;background:#fff;font-weight:800}
.rider-card{background:#fff;border-radius:16px;padding:12px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:10px}
</style></head><body>

<div class="top-bar">
<div class="left"><img src="/logo.png"><div class="location"><b>Kajiado Town</b>Deliver in 30 min • 📍 Change</div></div>
<div class="right"><div class="icon-btn" onclick="openSearch()">🔍</div><div class="icon-btn" onclick="openNotifs()">🔔</div></div>
</div>

<div class="search-bar"><div class="input"><span>🔍</span><input id="searchInput" placeholder="Search flour, milk, bread..." oninput="searchProd(this.value)"></div><div class="filter" onclick="openFilter()">☰</div></div>

<div class="banner"><div><h2>Free Delivery<br>on First 3 Orders</h2><p>Use code: LONMA30 • Valid today</p></div><div class="badge">ORDER NOW</div></div>

<div class="store-row" id="storeRow"></div>
<div class="cat-row" id="catRow"></div>

<div class="section"><div class="section-head"><h3>🔥 Best Deals Today</h3><a onclick="showAll()">See All</a></div><div class="prod-grid" id="prodGrid"></div></div>

<div class="section"><div class="section-head"><h3>⚡ Flash Sale - Ends in 2 Hours</h3><a style="color:#ff3b30">02:14:33</a></div><div class="prod-grid" id="flashGrid"></div></div>

<div class="bottom-nav">
<div class="tab active" onclick="switchTab('home')"><div class="ic">🏠</div><b>Home</b></div>
<div class="tab" onclick="switchTab('categories')"><div class="ic">🗂️</div><b>Categories</b></div>
<div class="tab" onclick="openCart()" style="position:relative"><div class="ic">🛒</div><b>Cart</b><div class="cart-badge" id="cartBadge">0</div></div>
<div class="tab" onclick="openRider()"><div class="ic">🏍️</div><b>Rider</b></div>
<div class="tab" onclick="openProfile()"><div class="ic">👤</div><b>Profile</b></div>
</div>

<div id="aiBtn" onclick="toggleAI()">🤖</div>
<div id="aiChat"><div class="ai-h"><div><b>🤖 LONMA AI</b><br><small style="opacity:0.8">Online • Knows 5 stores</small></div><div style="cursor:pointer" onclick="toggleAI()">✕</div></div><div class="ai-msgs" id="aiMsgs"><div class="msg bot">Hello! I am your AI shopping assistant.<br><br>I compare prices from Naivas, Quickmart, Carrefour, Chandarana, Magunas.<br><br>Try: "cheapest flour", "milk price", "rider time"</div></div><div class="ai-in"><input id="aiInput" placeholder="Ask anything..." onkeypress="if(event.key==='Enter') sendAI()"><button onclick="sendAI()">Send</button></div></div>

<!-- CART SHEET -->
<div id="cartModal" class="modal"><div class="sheet"><div class="sheet-h"><h3>Shopping Cart (<span id="cartCount">0</span>)</h3><div onclick="closeModals()" style="width:32px;height:32px;background:#f2f3f7;border-radius:10px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="sheet-c"><div id="cartItems"></div><div style="background:#f8f9fa;border-radius:14px;padding:12px;margin:12px 0"><div style="display:flex;justify-content:space-between;font-size:12px;margin:4px 0"><span>Subtotal</span><b>KES <span id="subTotal">0</span></b></div><div style="display:flex;justify-content:space-between;font-size:12px;margin:4px 0"><span>Delivery Fee</span><b>KES 100</b></div><div style="display:flex;justify-content:space-between;font-size:13px;font-weight:800;margin:8px 0;padding-top:8px;border-top:1px solid #e0e0e0"><span>Total</span><b>KES <span id="grandTotal">0</span></b></div></div><input id="custName" class="input" placeholder="Full Name"><input id="custPhone" class="input" value="254" placeholder="M-Pesa Phone"><input id="custLocation" class="input" placeholder="Delivery Location - e.g. Kajiado, House No"><select id="payMethod" class="input"><option value="mpesa">Lipa na M-Pesa</option><option value="cod">Cash on Delivery</option></select><button class="btn btn-green" onclick="checkout()">Place Order - Rider in 30min</button><div id="checkoutStatus" style="text-align:center;font-size:11px;font-weight:700;margin-top:8px"></div><div id="tracking" style="display:none;margin-top:12px;background:#e8f5e9;border-radius:14px;padding:12px"><b>Order <span id="orderId"></span> Placed!</b><p style="font-size:11px;margin-top:4px" id="riderAssigned">Finding nearest rider...</p></div></div></div></div>

<!-- RIDER SHEET -->
<div id="riderModal" class="modal"><div class="sheet"><div class="sheet-h"><h3>🏍️ Rider App</h3><div onclick="closeModals()" style="width:32px;height:32px;background:#f2f3f7;border-radius:10px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="sheet-c"><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px"><div style="background:#e0f7fa;padding:12px;border-radius:14px;text-align:center"><b id="rStat1">3</b><br><small style="font-size:10px">Available Riders</small></div><div style="background:#fff3cd;padding:12px;border-radius:14px;text-align:center"><b id="rStat2">0</b><br><small style="font-size:10px">Active Orders</small></div><div style="background:#d4edda;padding:12px;border-radius:14px;text-align:center"><b id="rStat3">KES 0</b><br><small style="font-size:10px">Today Sales</small></div></div><div id="riderList"></div><div id="riderOrders"></div></div></div></div>

<!-- PROFILE SHEET -->
<div id="profileModal" class="modal"><div class="sheet"><div class="sheet-h"><h3>👤 Profile</h3><div onclick="closeModals()" style="width:32px;height:32px;background:#f2f3f7;border-radius:10px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="sheet-c"><div style="text-align:center;padding:20px"><div style="width:72px;height:72px;background:#0A8EA8;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:32px;color:#fff;margin:0 auto">👤</div><h3 style="margin-top:12px">Guest User</h3><small style="color:#888">Kajiado, Kenya</small></div><div style="display:grid;gap:8px"><div class="rider-card"><span>📦 My Orders</span><span>›</span></div><div class="rider-card"><span>❤️ Wishlist</span><span>›</span></div><div class="rider-card"><span>📍 Addresses</span><span>›</span></div><div class="rider-card" onclick="openAdmin()"><span>📊 Admin Dashboard</span><span>›</span></div><div class="rider-card"><span>🤖 AI Chat History</span><span>›</span></div><div class="rider-card"><span>⚙️ Settings</span><span>›</span></div></div></div></div></div>

<!-- ADMIN SHEET -->
<div id="adminModal" class="modal"><div class="sheet"><div class="sheet-h"><h3>📊 Admin Dashboard</h3><div onclick="closeModals()" style="width:32px;height:32px;background:#f2f3f7;border-radius:10px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="sheet-c"><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px" id="adminStats"></div><h4 style="margin:14px 0 8px;font-size:12px">Recent Orders</h4><div id="adminOrders"></div></div></div></div>

<script>
const STORES=[{"id":"naivas","name":"NAIVAS","icon":"🟢","color":"#008000"},{"id":"quickmart","name":"QUICKMART","icon":"🔴","color":"#E30613"},{"id":"carrefour","name":"CARREFOUR","icon":"🔵","color":"#0047AB"},{"id":"chandarana","name":"CHANDARANA","icon":"🟠","color":"#FF8C00"},{"id":"magunas","name":"MAGUNAS","icon":"🟣","color":"#800080"}];
const CATS=[{"id":"all","name":"All","icon":"🏪"},{"id":"fresh","name":"Fresh","icon":"🥬"},{"id":"grocery","name":"Grocery","icon":"🌽"},{"id":"beverages","name":"Drinks","icon":"🥤"},{"id":"dairy","name":"Dairy","icon":"🥛"},{"id":"household","name":"Home","icon":"🧹"},{"id":"personal","name":"Care","icon":"🧴"},{"id":"baby","name":"Baby","icon":"👶"}];
const PRODS=[{"id":1,"name":"Ajab Maize Flour 2kg","price":175,"old_price":190,"store":"naivas","cat":"grocery","stock":50,"rating":4.8,"sold":234,"desc":"Best for ugali"},{"id":2,"name":"Brookside Milk 500ml","price":65,"old_price":70,"store":"naivas","cat":"dairy","stock":100,"rating":4.9,"sold":512,"desc":"Fresh daily milk"},{"id":3,"name":"Coca Cola 1.25L","price":100,"old_price":120,"store":"quickmart","cat":"beverages","stock":80,"rating":4.7,"sold":320,"desc":"Chilled soft drink"},{"id":4,"name":"Omo Detergent 1kg","price":285,"old_price":320,"store":"carrefour","cat":"household","stock":40,"rating":4.6,"sold":89,"desc":"Removes stains"},{"id":5,"name":"Tomatoes 1kg","price":80,"old_price":100,"store":"quickmart","cat":"fresh","stock":60,"rating":4.9,"sold":445,"desc":"Farm fresh"},{"id":6,"name":"White Bread 400g","price":60,"old_price":65,"store":"naivas","cat":"dairy","stock":70,"rating":4.8,"sold":210,"desc":"Soft fresh bread"},{"id":7,"name":"Pishori Rice 2kg","price":350,"old_price":400,"store":"carrefour","cat":"grocery","stock":30,"rating":4.9,"sold":156,"desc":"Premium rice"},{"id":8,"name":"Geisha Soap 150g","price":55,"old_price":60,"store":"magunas","cat":"personal","stock":90,"rating":4.5,"sold":98,"desc":"Beauty soap"},{"id":9,"name":"Kabras Sugar 2kg","price":280,"old_price":300,"store":"chandarana","cat":"grocery","stock":45,"rating":4.7,"sold":167,"desc":"Sweet sugar"},{"id":10,"name":"Eggs Tray 30pcs","price":420,"old_price":450,"store":"quickmart","cat":"fresh","stock":25,"rating":4.9,"sold":89,"desc":"Farm eggs"},{"id":11,"name":"Cooking Oil 2L","price":380,"old_price":420,"store":"naivas","cat":"grocery","stock":35,"rating":4.8,"sold":134,"desc":"Fortified oil"},{"id":12,"name":"Pampers Diapers","price":850,"old_price":950,"store":"carrefour","cat":"baby","stock":20,"rating":4.9,"sold":67,"desc":"Size 3, 30pcs"}];

let cart=[], total=0, activeStore='all', activeCat='all';

function renderStores(){
 let h=`<div class="store-chip active" onclick="filterStore('all',this)"><div class="icon">🏪</div><b>ALL STORES</b><small>12 items</small></div>`;
 STORES.forEach(s=>h+=`<div class="store-chip" onclick="filterStore('${s.id}',this)"><div class="icon">${s.icon}</div><b>${s.name}</b><small>${s.id}</small></div>`);
 document.getElementById('storeRow').innerHTML=h;
}
function renderCats(){
 let h='';
 CATS.forEach(c=>h+=`<div class="cat-chip ${c.id=='all'?'active':''}" onclick="filterCat('${c.id}',this)"><div class="ic">${c.icon}</div><b>${c.name}</b></div>`);
 document.getElementById('catRow').innerHTML=h;
}
function renderProds(list, target='prodGrid'){
 let h='';
 list.forEach(p=>{
  let disc=Math.round((p.old_price-p.price)/p.old_price*100);
  h+=`<div class="card" data-store="${p.store}" data-cat="${p.cat}" data-name="${p.name.toLowerCase()}">
   <div class="img">🛒<div class="off">-${disc}%</div><div class="fav">♡</div></div>
   <div class="info"><div class="store">${p.store.toUpperCase()}</div><h4>${p.name}</h4><div class="meta"><span>⭐ ${p.rating}</span><span>• ${p.sold} sold</span><span>• ${p.stock} left</span></div><div class="price-row"><div class="price"><b>KES ${p.price}</b><small>KES ${p.old_price}</small></div><button class="add" onclick="addToCart(${p.id},'${p.name}',${p.price})">+</button></div></div></div>`;
 });
 document.getElementById(target).innerHTML=h;
}

function filterStore(id, el){
 activeStore=id;
 document.querySelectorAll('.store-chip').forEach(c=>c.classList.remove('active')); el.classList.add('active');
 applyFilters();
}
function filterCat(id, el){
 activeCat=id;
 document.querySelectorAll('.cat-chip').forEach(c=>c.classList.remove('active')); el.classList.add('active');
 applyFilters();
}
function applyFilters(){
 let filtered=PRODS.filter(p=>(activeStore=='all'||p.store==activeStore)&&(activeCat=='all'||p.cat==activeCat));
 renderProds(filtered,'prodGrid');
}
function searchProd(q){
 if(!q){renderProds(PRODS,'prodGrid'); return}
 let f=PRODS.filter(p=>p.name.toLowerCase().includes(q.toLowerCase())||p.desc.toLowerCase().includes(q.toLowerCase())||p.store.includes(q.toLowerCase()));
 renderProds(f,'prodGrid');
}
function addToCart(id,name,price){cart.push({id,name,price}); total+=price; document.getElementById('cartBadge').innerText=cart.length; document.getElementById('cartCount').innerText=cart.length; if(navigator.vibrate) navigator.vibrate(30)}
function openCart(){
 let d=document.getElementById('cartItems'); d.innerHTML='';
 if(cart.length==0) d.innerHTML='<p style="text-align:center;padding:20px;color:#888">Cart is empty - add items</p>';
 cart.forEach((c,i)=>d.innerHTML+=`<div class="cart-item"><div class="img">🛒</div><div class="info"><h4>${c.name}</h4><small>KES ${c.price}</small><div class="qty"><button onclick="removeCart(${i})">-</button><span>${1}</span><button onclick="addToCart(${c.id},'${c.name}',${c.price}); openCart()">+</button></div></div><b>KES ${c.price}</b></div>`);
 document.getElementById('subTotal').innerText=total;
 document.getElementById('grandTotal').innerText=total+100;
 document.getElementById('cartModal').classList.add('open');
}
function removeCart(i){total-=cart[i].price; cart.splice(i,1); document.getElementById('cartBadge').innerText=cart.length; openCart()}
function openRider(){document.getElementById('riderModal').classList.add('open'); loadRiders()}
function openProfile(){document.getElementById('profileModal').classList.add('open')}
function openAdmin(){closeModals(); document.getElementById('adminModal').classList.add('open'); loadAdmin()}
function closeModals(){document.querySelectorAll('.modal').forEach(m=>m.classList.remove('open'))}
function switchTab(t){document.querySelectorAll('.bottom-nav.tab').forEach(x=>x.classList.remove('active')); event.currentTarget.classList.add('active'); if(t=='categories') document.getElementById('catRow').scrollIntoView({behavior:'smooth'})}
function toggleAI(){document.getElementById('aiChat').classList.toggle('open')}
async function sendAI(){
 let input=document.getElementById('aiInput'); let msg=input.value.trim(); if(!msg) return;
 let box=document.getElementById('aiMsgs'); box.innerHTML+=`<div class="msg user">${msg}</div>`; input.value=''; box.scrollTop=box.scrollHeight;
 let r=await fetch('/ai/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
 let data=await r.json(); box.innerHTML+=`<div class="msg bot">${data.reply}</div>`; box.scrollTop=box.scrollHeight;
}
async function checkout(){
 let phone=document.getElementById('custPhone').value; let loc=document.getElementById('custLocation').value;
 if(!loc){alert('Enter delivery location'); return}
 document.getElementById('checkoutStatus').innerText='Placing order...';
 let r=await fetch('/mpesa/stkpush',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone,amount:total+100,location:loc,cart})});
 let d=await r.json();
 document.getElementById('orderId').innerText=d.order_id;
 document.getElementById('checkoutStatus').innerText='Order '+d.order_id+' placed! Rider coming in 30min';
 document.getElementById('tracking').style.display='block';
 document.getElementById('riderAssigned').innerText='Rider John Mwangi KMEZ 123A assigned - 2.5km away - Call 0712345678';
 cart=[]; total=0; document.getElementById('cartBadge').innerText=0;
}
async function loadRiders(){
 let r=await fetch('/riders'); let riders=await r.json();
 let h=''; riders.forEach(rd=>h+=`<div class="rider-card"><div><b>${rd.name} ⭐${rd.rating}</b><br><small>${rd.motor} • ${rd.location} • ${rd.orders} trips</small></div><div style="padding:6px 10px;border-radius:10px;background:${rd.status=='available'?'#d4edda':'#fff3cd'};font-size:10px;font-weight:800">${rd.status}</div></div>`);
 document.getElementById('riderList').innerHTML=h;
 let ro=await fetch('/orders'); let orders=await ro.json();
 document.getElementById('rStat2').innerText=orders.length;
 document.getElementById('rStat3').innerText='KES '+orders.reduce((s,o)=>s+o.amount,0);
 let oh='<h4 style="margin:12px 0 8px;font-size:12px">Active Orders</h4>'; orders.slice(0,5).forEach(o=>oh+=`<div class="rider-card"><div><b>${o.id}</b> - KES ${o.amount}<br><small>${o.location}</small></div><button onclick="acceptOrder('${o.id}')" style="padding:8px 12px;background:#00a651;color:#fff;border:none;border-radius:10px;font-size:11px;font-weight:800">Accept</button></div>`);
 document.getElementById('riderOrders').innerHTML=oh;
}
async function loadAdmin(){
 let r=await fetch('/orders'); let orders=await r.json();
 document.getElementById('adminStats').innerHTML=`<div style="background:#fff;padding:14px;border-radius:14px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06)"><b style="font-size:20px">${orders.length}</b><br><small>Orders</small></div><div style="background:#fff;padding:14px;border-radius:14px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06)"><b style="font-size:20px">KES ${orders.reduce((s,o)=>s+o.amount,0)}</b><br><small>Sales</small></div>`;
 let oh=''; orders.slice(0,8).forEach(o=>oh+=`<div class="rider-card"><div><b>${o.id}</b> - ${o.status}<br><small>${o.location} • KES ${o.amount}</small></div><small>${o.phone}</small></div>`);
 document.getElementById('adminOrders').innerHTML=oh;
}
async function acceptOrder(id){await fetch('/rider/accept/'+id,{method:'POST'}); alert('Accepted '+id); loadRiders()}
function openSearch(){document.getElementById('searchInput').focus()}
function openNotifs(){alert('No new notifications - 3 orders delivered today!')}
function openFilter(){alert('Filter: Sort by Price, Rating, Store')}
function showAll(){renderProds(PRODS,'prodGrid')}

renderStores(); renderCats(); renderProds(PRODS,'prodGrid'); renderProds([...PRODS].sort(()=>0.5-Math.random()).slice(0,4),'flashGrid');
</script></body></html>
'''

@app.post("/ai/chat")
async def ai_chat(req: Request):
    b=await req.json()
    return {"reply": ai_response(b.get("message",""))}

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
        data=r.json(); data["order_id"]=order_id; return data
    except Exception as e:
        return {"error":str(e),"ResponseCode":"1","order_id":f"ORD{random.randint(1000,9999)}"}

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
async def cb_post(req: Request): return {"ResultCode":0,"ResultDesc":"Accepted"}
@app.get("/logo.png")
async def logo(): return FileResponse("logo.png") if os.path.exists("logo.png") else {"error":"no logo"}
@app.get("/favicon.ico")
async def fav(): return FileResponse("logo.png") if os.path.exists("logo.png") else {}
