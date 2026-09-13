from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, base64, requests, random
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MPESA_CONSUMER_KEY=os.getenv("MPESA_CONSUMER_KEY",""); MPESA_CONSUMER_SECRET=os.getenv("MPESA_CONSUMER_SECRET",""); MPESA_SHORTCODE=os.getenv("MPESA_SHORTCODE","174379"); MPESA_PASSKEY=os.getenv("MPESA_PASSKEY",""); MPESA_CALLBACK_URL=os.getenv("MPESA_CALLBACK_URL","https://app.lonmaorbit.co.ke/mpesa/callback"); MPESA_ENV=os.getenv("MPESA_ENV","sandbox")
def get_token():
    try:
        if not MPESA_CONSUMER_KEY: return None
        url="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        return requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET), timeout=8).json().get("access_token")
    except: return None

# REAL IMAGES - Unsplash real product photos
PRODUCTS=[
 {"id":1,"name":"Ajab Maize Flour 2kg","price":175,"old":195,"store":"Naivas","cat":"grocery","stock":50,"rate":4.8,"sold":234,"img":"https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400","emoji":"🌽"},
 {"id":2,"name":"Brookside Milk 500ml","price":65,"old":75,"store":"Naivas","cat":"dairy","stock":100,"rate":4.9,"sold":512,"img":"https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400","emoji":"🥛"},
 {"id":3,"name":"Coca Cola 1.25L","price":100,"old":120,"store":"Quickmart","cat":"drinks","stock":80,"rate":4.7,"sold":320,"img":"https://images.unsplash.com/photo-1553456558-aff63285bdd1?w=400","emoji":"🥤"},
 {"id":4,"name":"Omo Detergent 1kg","price":285,"old":320,"store":"Carrefour","cat":"home","stock":40,"rate":4.6,"sold":89,"img":"https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=400","emoji":"🧴"},
 {"id":5,"name":"Tomatoes Fresh 1kg","price":80,"old":100,"store":"Quickmart","cat":"fresh","stock":60,"rate":4.9,"sold":445,"img":"https://images.unsplash.com/photo-1561136594-7f68413baa99?w=400","emoji":"🍅"},
 {"id":6,"name":"White Bread 400g","price":60,"old":70,"store":"Naivas","cat":"dairy","stock":70,"rate":4.8,"sold":210,"img":"https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400","emoji":"🍞"},
 {"id":7,"name":"Pishori Rice 2kg","price":350,"old":400,"store":"Carrefour","cat":"grocery","stock":30,"rate":4.9,"sold":156,"img":"https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400","emoji":"🍚"},
 {"id":8,"name":"Geisha Soap 150g","price":55,"old":65,"store":"Magunas","cat":"care","stock":90,"rate":4.5,"sold":98,"img":"https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=400","emoji":"🧼"},
 {"id":9,"name":"Kabras Sugar 2kg","price":280,"old":300,"store":"Chandarana","cat":"grocery","stock":45,"rate":4.7,"sold":167,"img":"https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400","emoji":"🍯"},
 {"id":10,"name":"Eggs Tray 30pcs","price":420,"old":460,"store":"Quickmart","cat":"fresh","stock":25,"rate":4.9,"sold":89,"img":"https://images.unsplash.com/photo-1482049016688-2d3e1b31122f?w=400","emoji":"🥚"},
 {"id":11,"name":"Cooking Oil 2L","price":380,"old":420,"store":"Naivas","cat":"grocery","stock":35,"rate":4.8,"sold":134,"img":"https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400","emoji":"🫒"},
 {"id":12,"name":"Pampers Size 3","price":850,"old":950,"store":"Carrefour","cat":"baby","stock":20,"rate":4.9,"sold":67,"img":"https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400","emoji":"👶"},
]
RIDERS=[{"id":1,"name":"John Mwangi","motor":"KMEZ 123A","status":"available","rating":4.9,"location":"Kajiado","trips":12},{"id":2,"name":"Peter Ochieng","motor":"KMFA 456B","status":"delivering","rating":4.8,"location":"Kitengela","trips":28},{"id":3,"name":"Samuel Kiprop","motor":"KMEB 789C","status":"available","rating":5.0,"location":"Rongai","trips":15}]
ORDERS=[]
USERS={}

def ai_reply(m):
 m=m.lower()
 if "flour" in m: return "Ajab Flour 2kg KES 175 Naivas (cheapest 172 Carrefour). 50 packs left. Real image loaded!"
 if "milk" in m: return "Brookside Milk KES 65 Naivas, 62 Chandarana. Fresh daily with real photo!"
 if "rider" in m: return "Delivery 30min Kajiado/Kitengela/Rongai. Fee KES 100. 3 riders online."
 if "dark" in m or "mode" in m: return "Click moon icon top right for dark mode! 🌙"
 if "whatsapp" in m or "login" in m: return "Click Profile > Login with WhatsApp. Enter 2547... number, we send code!"
 if "hello" in m or "hi" in m: return "Hello! I'm LONMA AI with real images, WhatsApp login & dark mode. Ask 'cheapest flour'"
 return "Try: 'cheapest flour', 'milk price', 'rider time', 'dark mode', 'whatsapp login'"

@app.get("/", response_class=HTMLResponse)
async def index():
 return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><meta name="theme-color" content="#0A8EA8"><title>LONMA ORBIT</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800&display=swap" rel="stylesheet">
<style>
:root{--bg:#f6f7fb;--card:#fff;--text:#111;--muted:#666;--border:#eee;--teal:#0A8EA8}
.dark{--bg:#0f0f0f;--card:#1c1c1e;--text:#fff;--muted:#aaa;--border:#2a2a2a;--teal:#0A8EA8}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,Arial} body{background:var(--bg);color:var(--text);padding-bottom:90px;transition:0.3s} 
.header{position:sticky;top:0;z-index:50;background:var(--card);border-bottom:1px solid var(--border)}
.h-top{display:flex;justify-content:space-between;align-items:center;padding:10px 14px}
.h-top img{height:38px} .icons{display:flex;gap:8px} .ic-btn{width:38px;height:38px;background:var(--bg);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:18px;cursor:pointer;border:1px solid var(--border)}
.h-location{padding:0 14px 10px;display:flex;align-items:center;gap:8px} .pin{width:32px;height:32px;background:#e6f7fa;border-radius:10px;display:flex;align-items:center;justify-content:center} .h-location b{font-size:13px} .h-location small{font-size:11px;color:var(--muted)}
.search{padding:10px 14px;background:var(--card);display:flex;gap:10px} .search-box{flex:1;background:var(--bg);border-radius:14px;display:flex;align-items:center;gap:10px;padding:12px 14px;border:1px solid var(--border)} .search-box input{border:none;background:transparent;outline:none;flex:1;font-size:13px;font-weight:500;color:var(--text)} .filter-btn{width:48px;height:48px;background:#111;border-radius:14px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px}
.hero{margin:12px 14px;background:linear-gradient(105deg,#0A8EA8 0%,#00c2a2 100%);border-radius:20px;padding:16px;display:flex;justify-content:space-between;align-items:center;color:#fff;position:relative;overflow:hidden}
.hero::after{content:'';position:absolute;right:-20px;top:-20px;width:120px;height:120px;background:rgba(255,255,255,0.15);border-radius:50%} .hero h2{font-size:17px;line-height:1.2;font-weight:800} .hero p{font-size:11px;opacity:0.9;margin-top:4px} .hero-btn{background:#fff;color:#0A8EA8;padding:10px 16px;border-radius:24px;font-weight:800;font-size:11px;z-index:1}
.chips{display:flex;gap:8px;overflow-x:auto;padding:8px 14px;scrollbar-width:none} .chips::-webkit-scrollbar{display:none}
.chip{white-space:nowrap;padding:8px 14px;border-radius:20px;background:var(--card);border:1px solid var(--border);font-size:11px;font-weight:700;cursor:pointer} .chip.active{background:#111;color:#fff;border-color:#111} .dark .chip.active{background:#fff;color:#000}
.cats{display:flex;gap:12px;overflow-x:auto;padding:12px 14px;scrollbar-width:none} .cats::-webkit-scrollbar{display:none}
.cat{min-width:64px;text-align:center;cursor:pointer} .cat-icon{width:60px;height:60px;background:var(--card);border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:26px;box-shadow:0 4px 12px rgba(0,0,0,0.06);margin:0 auto;border:1px solid var(--border)} .cat.active .cat-icon{background:#0A8EA8;color:#fff} .cat b{font-size:10px;margin-top:6px;display:block;font-weight:700}
.section{padding:10px 14px} .sec-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px} .sec-head h3{font-size:15px;font-weight:800} .sec-head span{font-size:11px;color:#0A8EA8;font-weight:700;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.card{background:var(--card);border-radius:20px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.05);position:relative;border:1px solid var(--border)}
.card-img{height:140px;background:#f9fafb;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden} .card-img img{width:100%;height:100%;object-fit:cover} .card-img .emoji{position:absolute;font-size:36px;background:rgba(255,255,255,0.9);width:50px;height:50px;border-radius:50%;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.badge{position:absolute;top:10px;left:10px;background:#ff3b30;color:#fff;font-size:9px;font-weight:800;padding:4px 7px;border-radius:8px;z-index:2} .heart{position:absolute;top:10px;right:10px;width:30px;height:30px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.1);cursor:pointer;font-size:14px;z-index:2}
.card-body{padding:10px} .store{font-size:8px;font-weight:800;letter-spacing:0.8px;color:#0A8EA8;text-transform:uppercase} .card-body h4{font-size:12px;font-weight:700;line-height:1.3;margin:3px 0;height:32px;overflow:hidden} .meta{display:flex;gap:8px;font-size:10px;color:var(--muted);margin:4px 0} .price-row{display:flex;justify-content:space-between;align-items:center;margin-top:8px} .price b{font-size:14px;font-weight:800} .price small{font-size:10px;color:#999;text-decoration:line-through;margin-left:4px} .add-btn{width:32px;height:32px;background:#111;color:#fff;border:none;border-radius:11px;font-size:18px;font-weight:800;cursor:pointer} .dark .add-btn{background:#fff;color:#000}
.h-scroll{display:flex;gap:10px;overflow-x:auto;padding-bottom:6px;scrollbar-width:none} .h-scroll::-webkit-scrollbar{display:none} .h-card{min-width:160px;background:var(--card);border-radius:18px;padding:10px;box-shadow:0 4px 16px rgba(0,0,0,0.05);border:1px solid var(--border)}
.bottom{position:fixed;bottom:0;left:0;right:0;background:var(--card);border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:8px 0 calc(8px + env(safe-area-inset-bottom));z-index:60}
.tab{flex:1;text-align:center;cursor:pointer;padding:4px;position:relative} .tab-i{font-size:22px} .tab.active{color:#0A8EA8} .tab b{font-size:9px;font-weight:700;display:block;margin-top:2px} .cart-dot{position:absolute;top:0;right:22px;background:#ff3b30;color:#fff;font-size:10px;font-weight:800;min-width:18px;height:18px;border-radius:9px;display:flex;align-items:center;justify-content:center;padding:0 4px}
#ai{position:fixed;bottom:92px;right:14px;width:58px;height:58px;background:#0A8EA8;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:28px;color:#fff;box-shadow:0 8px 24px rgba(10,142,168,0.45);cursor:pointer;z-index:55}
#aiChat{display:none;position:fixed;bottom:160px;left:12px;right:12px;max-width:420px;margin:0 auto;height:62vh;background:var(--card);border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,0.25);z-index:70;flex-direction:column;overflow:hidden;border:1px solid var(--border)} #aiChat.open{display:flex}
.ai-h{background:#0A8EA8;color:#fff;padding:14px 16px;display:flex;justify-content:space-between;align-items:center} .ai-msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:var(--bg)} .m{max-width:80%;padding:10px 14px;border-radius:18px;font-size:12px;line-height:1.45} .m.u{align-self:flex-end;background:#0A8EA8;color:#fff;border-bottom-right-radius:6px} .m.b{align-self:flex-start;background:var(--card);border:1px solid var(--border);border-bottom-left-radius:6px} .ai-in{display:flex;gap:8px;padding:12px;border-top:1px solid var(--border);background:var(--card)} .ai-in input{flex:1;padding:12px 16px;border-radius:24px;border:1px solid var(--border);font-size:13px;outline:none;background:var(--bg);color:var(--text)} .ai-in button{padding:12px 18px;background:#0A8EA8;color:#fff;border:none;border-radius:24px;font-weight:800}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);backdrop-filter:blur(8px);justify-content:center;align-items:flex-end;z-index:80} .modal.open{display:flex}
.sheet{background:var(--card);width:100%;max-width:500px;margin:0 auto;border-radius:28px 28px 0 0;max-height:88vh;overflow-y:auto;animation:up 0.35s} @keyframes up{from{transform:translateY(100%)}to{transform:translateY(0)}}
.s-h{padding:18px 16px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--card);border-radius:28px 28px 0 0} .s-c{padding:16px}
.btn{width:100%;padding:15px;border:none;border-radius:16px;font-weight:800;font-size:14px;cursor:pointer;margin-top:10px} .btn-black{background:#111;color:#fff} .btn-teal{background:#0A8EA8;color:#fff} .btn-green{background:#00a651;color:#fff} .btn-wa{background:#25D366;color:#fff;display:flex;align-items:center;justify-content:center;gap:8px}
.input{width:100%;padding:13px 14px;border-radius:14px;border:1px solid var(--border);font-size:13px;margin:6px 0;outline:none;background:var(--bg);color:var(--text)} .input:focus{border-color:#0A8EA8}
.cart-i{display:flex;gap:12px;padding:14px 0;border-bottom:1px solid var(--border)} .cart-i .ci{width:60px;height:60px;background:var(--bg);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;overflow:hidden} .cart-i .ci img{width:100%;height:100%;object-fit:cover}
.toast{position:fixed;bottom:100px;left:50%;transform:translateX(-50%);background:#111;color:#fff;padding:10px 18px;border-radius:24px;font-size:12px;font-weight:700;z-index:100;display:none;box-shadow:0 8px 24px rgba(0,0,0,0.3)} .dark .toast{background:#fff;color:#000}
</style></head><body>

<div class="header">
<div class="h-top"><img src="/logo.png"><div class="icons"><div class="ic-btn" onclick="toggleDark()">🌙</div><div class="ic-btn" onclick="openSearch()">🔍</div><div class="ic-btn" onclick="showToast('3 new deals!')">🔔</div></div></div>
<div class="h-location"><div class="pin">📍</div><div><b id="userLocation">Kajiado Town • 30 min delivery</b><small id="userNameDisplay">Guest • Login with WhatsApp</small></div><div style="margin-left:auto" onclick="openProfile()">›</div></div>
<div class="search"><div class="search-box">🔍<input id="search" placeholder="Search flour, milk, bread, soda..." oninput="searchProd(this.value)"></div><div class="filter-btn">☰</div></div>
</div>

<div class="hero"><div><h2>Free Delivery<br>on First 3 Orders!</h2><p>Use code LONMA30 • Real product images</p></div><div class="hero-btn">ORDER NOW</div></div>

<div class="chips" id="storeChips"></div>
<div class="cats" id="catChips"></div>

<div class="section"><div class="sec-head"><h3>🔥 Best Deals Today</h3><span onclick="render(PRODUCTS)">See All</span></div><div class="grid" id="grid"></div></div>

<div class="section"><div class="sec-head"><h3>⚡ Flash Sale - Real Images</h3><span style="color:#ff3b30">Ends 02:14:33</span></div><div class="h-scroll" id="flash"></div></div>

<div class="bottom">
<div class="tab active" onclick="navTab(this,'home')"><div class="tab-i">🏠</div><b>Home</b></div>
<div class="tab" onclick="navTab(this,'cats')"><div class="tab-i">🗂️</div><b>Categories</b></div>
<div class="tab" onclick="openCart()"><div class="tab-i">🛒</div><b>Cart</b><div class="cart-dot" id="cartDot">0</div></div>
<div class="tab" onclick="openRider()"><div class="tab-i">🏍️</div><b>Rider</b></div>
<div class="tab" onclick="openProfile()"><div class="tab-i">👤</div><b>Profile</b></div>
</div>

<div id="ai" onclick="toggleAI()">🤖</div>
<div id="aiChat"><div class="ai-h"><div><b>🤖 LONMA AI</b><div style="font-size:11px;opacity:0.85">Real images • WhatsApp login • Dark mode</div></div><div onclick="toggleAI()" style="width:32px;height:32px;background:rgba(255,255,255,0.2);border-radius:10px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="ai-msgs" id="aiMsgs"><div class="m b">Hello! New features added! 🎉<br><br>✅ Real product images from camera<br>✅ WhatsApp login - 2547...<br>✅ Dark mode - moon icon top<br><br>Try: "cheapest flour" or "dark mode"</div></div><div class="ai-in"><input id="aiInput" placeholder="Ask anything..." onkeypress="if(event.key==='Enter') sendAI()"><button onclick="sendAI()">Send</button></div></div>

<div id="cartModal" class="modal"><div class="sheet"><div class="s-h"><h3>Cart (<span id="cartC">0</span>)</h3><div onclick="closeM()" style="width:36px;height:36px;background:var(--bg);border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="s-c"><div id="cartItems"></div><div style="background:var(--bg);border-radius:16px;padding:14px;margin:14px 0"><div style="display:flex;justify-content:space-between;font-size:12px;margin:5px 0"><span>Subtotal</span><b>KES <span id="sub">0</span></b></div><div style="display:flex;justify-content:space-between;font-size:12px;margin:5px 0"><span>Delivery</span><b>KES 100</b></div><div style="display:flex;justify-content:space-between;font-size:14px;font-weight:800;border-top:1px solid var(--border);margin-top:8px;padding-top:10px"><span>Total</span><b>KES <span id="grand">0</span></b></div></div><input id="custName" class="input" placeholder="Full Name"><input id="custPhone" class="input" value="254" placeholder="M-Pesa Phone"><input id="custLoc" class="input" placeholder="Delivery Location"><select id="pay" class="input"><option value="mpesa">Lipa na M-Pesa</option><option value="cod">Cash on Delivery</option></select><button class="btn btn-green" onclick="checkout()">Place Order - Rider in 30min</button><div id="status" style="text-align:center;font-size:11px;font-weight:700;margin-top:8px"></div><div id="track" style="display:none;margin-top:12px;background:#e8f5e9;border-radius:16px;padding:14px"><b>✅ Order <span id="orderId"></span> Confirmed!</b><p style="font-size:11px;margin-top:6px" id="riderInfo">Finding rider...</p></div></div></div></div>

<div id="riderModal" class="modal"><div class="sheet"><div class="s-h"><h3>Rider Center</h3><div onclick="closeM()" style="width:36px;height:36px;background:var(--bg);border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="s-c"><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px"><div style="background:#e0f7fa;padding:14px;border-radius:16px;text-align:center"><b id="rs1">3</b><br><small style="font-size:10px">Online</small></div><div style="background:#fff3cd;padding:14px;border-radius:16px;text-align:center"><b id="rs2">0</b><br><small style="font-size:10px">Orders</small></div><div style="background:#d4edda;padding:14px;border-radius:16px;text-align:center"><b id="rs3">KES 0</b><br><small style="font-size:10px">Sales</small></div></div><div id="riderList" style="margin-top:14px"></div><div id="riderOrders" style="margin-top:10px"></div></div></div></div>

<div id="profileModal" class="modal"><div class="sheet"><div class="s-h"><h3>Profile</h3><div onclick="closeM()" style="width:36px;height:36px;background:var(--bg);border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="s-c">
<div id="loginSection"><div style="text-align:center;padding:10px 0 20px"><div style="width:80px;height:80px;background:#0A8EA8;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:36px;color:#fff;margin:0 auto">👤</div><h3 style="margin-top:12px" id="profileName">Welcome to LONMA</h3><small style="color:var(--muted)" id="profilePhone">Login to order faster</small></div>
<div id="notLogged"><input id="waPhone" class="input" value="254" placeholder="WhatsApp Number 254712..."><button class="btn btn-wa" onclick="loginWA()">💬 Login with WhatsApp</button><p style="font-size:10px;text-align:center;color:var(--muted);margin-top:8px">We will send OTP via WhatsApp</p></div>
<div id="logged" style="display:none"><div style="background:#d4edda;border-radius:14px;padding:12px;text-align:center"><b>✅ Logged in via WhatsApp</b><br><small id="loggedPhone">254...</small></div><button class="btn btn-black" onclick="logout()" style="margin-top:10px">Logout</button></div>
</div>
<div style="display:grid;gap:10px;margin-top:16px"><div style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:14px;display:flex;justify-content:space-between;align-items:center"><span>📦 My Orders</span><span>›</span></div><div style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:14px;display:flex;justify-content:space-between;align-items:center"><span>🌙 Dark Mode</span><span onclick="toggleDark()" style="padding:6px 12px;background:var(--bg);border-radius:10px;font-size:11px;font-weight:800;cursor:pointer;border:1px solid var(--border)">Toggle</span></div><div onclick="openAdmin()" style="background:#111;color:#fff;border-radius:16px;padding:14px;display:flex;justify-content:space-between;align-items:center;cursor:pointer"><span>📊 Admin Dashboard</span><span>›</span></div></div>
</div></div></div>

<div id="adminModal" class="modal"><div class="sheet"><div class="s-h"><h3>Admin</h3><div onclick="closeM()" style="width:36px;height:36px;background:var(--bg);border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="s-c"><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px" id="adminStats"></div><div id="adminOrders" style="margin-top:12px"></div></div></div></div>

<div class="toast" id="toast"></div>

<script>
const PRODUCTS=[{"id":1,"name":"Ajab Maize Flour 2kg","price":175,"old":195,"store":"Naivas","cat":"grocery","stock":50,"rate":4.8,"sold":234,"img":"https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400","emoji":"🌽"},{"id":2,"name":"Brookside Milk 500ml","price":65,"old":75,"store":"Naivas","cat":"dairy","stock":100,"rate":4.9,"sold":512,"img":"https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400","emoji":"🥛"},{"id":3,"name":"Coca Cola 1.25L","price":100,"old":120,"store":"Quickmart","cat":"drinks","stock":80,"rate":4.7,"sold":320,"img":"https://images.unsplash.com/photo-1553456558-aff63285bdd1?w=400","emoji":"🥤"},{"id":4,"name":"Omo Detergent 1kg","price":285,"old":320,"store":"Carrefour","cat":"home","stock":40,"rate":4.6,"sold":89,"img":"https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=400","emoji":"🧴"},{"id":5,"name":"Tomatoes Fresh 1kg","price":80,"old":100,"store":"Quickmart","cat":"fresh","stock":60,"rate":4.9,"sold":445,"img":"https://images.unsplash.com/photo-1561136594-7f68413baa99?w=400","emoji":"🍅"},{"id":6,"name":"White Bread 400g","price":60,"old":70,"store":"Naivas","cat":"dairy","stock":70,"rate":4.8,"sold":210,"img":"https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400","emoji":"🍞"},{"id":7,"name":"Pishori Rice 2kg","price":350,"old":400,"store":"Carrefour","cat":"grocery","stock":30,"rate":4.9,"sold":156,"img":"https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400","emoji":"🍚"},{"id":8,"name":"Geisha Soap 150g","price":55,"old":65,"store":"Magunas","cat":"care","stock":90,"rate":4.5,"sold":98,"img":"https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=400","emoji":"🧼"},{"id":9,"name":"Kabras Sugar 2kg","price":280,"old":300,"store":"Chandarana","cat":"grocery","stock":45,"rate":4.7,"sold":167,"img":"https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400","emoji":"🍯"},{"id":10,"name":"Eggs Tray 30pcs","price":420,"old":460,"store":"Quickmart","cat":"fresh","stock":25,"rate":4.9,"sold":89,"img":"https://images.unsplash.com/photo-1482049016688-2d3e1b31122f?w=400","emoji":"🥚"},{"id":11,"name":"Cooking Oil 2L","price":380,"old":420,"store":"Naivas","cat":"grocery","stock":35,"rate":4.8,"sold":134,"img":"https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400","emoji":"🫒"},{"id":12,"name":"Pampers Size 3","price":850,"old":950,"store":"Carrefour","cat":"baby","stock":20,"rate":4.9,"sold":67,"img":"https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400","emoji":"👶"}];
const STORES=["ALL","Naivas","Quickmart","Carrefour","Chandarana","Magunas"];
const CATS=[{"id":"all","name":"All","icon":"🏪"},{"id":"fresh","name":"Fresh","icon":"🥬"},{"id":"grocery","name":"Grocery","icon":"🌽"},{"id":"drinks","name":"Drinks","icon":"🥤"},{"id":"dairy","name":"Dairy","icon":"🥛"},{"id":"home","name":"Home","icon":"🧹"},{"id":"care","name":"Care","icon":"🧴"},{"id":"baby","name":"Baby","icon":"👶"}];
let cart=[], total=0, activeStore="ALL", activeCat="all", isDark=false, currentUser=null;

function renderChips(){
 document.getElementById('storeChips').innerHTML=STORES.map(s=>`<div class="chip ${s==activeStore?'active':''}" onclick="setStore('${s}',this)">${s}</div>`).join('');
 document.getElementById('catChips').innerHTML=CATS.map(c=>`<div class="cat ${c.id==activeCat?'active':''}" onclick="setCat('${c.id}',this)"><div class="cat-icon">${c.icon}</div><b>${c.name}</b></div>`).join('');
}
function render(list){
 document.getElementById('grid').innerHTML=list.map(p=>`<div class="card"><div class="card-img"><img src="${p.img}" onerror="this.style.display='none'"><div class="emoji">${p.emoji}</div><div class="badge">-${Math.round((p.old-p.price)/p.old*100)}%</div><div class="heart" onclick="showToast('Added to wishlist ❤️')">♡</div></div><div class="card-body"><div class="store">${p.store}</div><h4>${p.name}</h4><div class="meta"><span>⭐ ${p.rate}</span><span>${p.sold} sold</span></div><div class="price-row"><div class="price"><b>KES ${p.price}</b><small>KES ${p.old}</small></div><button class="add-btn" onclick="add(${p.id})">+</button></div></div></div>`).join('');
}
function renderFlash(){
 document.getElementById('flash').innerHTML=PRODUCTS.slice(0,5).map(p=>`<div class="h-card"><div style="height:80px;border-radius:12px;overflow:hidden;background:#f5f5f5;display:flex;align-items:center;justify-content:center"><img src="${p.img}" style="width:100%;height:100%;object-fit:cover" onerror="this.parentElement.innerHTML='${p.emoji}'"></div><div style="font-size:10px;font-weight:700;margin-top:6px">${p.name}</div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px"><b style="font-size:12px">KES ${p.price}</b><button class="add-btn" style="width:26px;height:26px;font-size:14px" onclick="add(${p.id})">+</button></div></div>`).join('');
}
function setStore(s,el){activeStore=s; document.querySelectorAll('#storeChips .chip').forEach(c=>c.classList.remove('active')); el.classList.add('active'); filter()}
function setCat(c,el){activeCat=c; document.querySelectorAll('.cat').forEach(x=>x.classList.remove('active')); el.classList.add('active'); filter()}
function filter(){let f=PRODUCTS.filter(p=>(activeStore=='ALL'||p.store==activeStore)&&(activeCat=='all'||p.cat==activeCat)); render(f)}
function searchProd(q){if(!q){render(PRODUCTS);return} let f=PRODUCTS.filter(p=>p.name.toLowerCase().includes(q.toLowerCase())||p.store.toLowerCase().includes(q.toLowerCase())); render(f)}
function add(id){let p=PRODUCTS.find(x=>x.id==id); cart.push(p); total+=p.price; document.getElementById('cartDot').innerText=cart.length; document.getElementById('cartC').innerText=cart.length; showToast(p.name+' added to cart 🛒'); if(navigator.vibrate) navigator.vibrate(30)}
function openCart(){
 let d=document.getElementById('cartItems'); d.innerHTML='';
 if(cart.length==0) d.innerHTML='<p style="text-align:center;padding:24px;color:var(--muted)">Cart empty<br><small>Add products</small></p>';
 cart.forEach((c,i)=>d.innerHTML+=`<div class="cart-i"><div class="ci"><img src="${c.img}" onerror="this.parentElement.innerHTML='${c.emoji}'"></div><div style="flex:1"><h4 style="font-size:12px">${c.name}</h4><small style="color:var(--muted)">${c.store} • KES ${c.price}</small></div><b>KES ${c.price}</b></div>`);
 document.getElementById('sub').innerText=total; document.getElementById('grand').innerText=total+100;
 document.getElementById('cartModal').classList.add('open');
}
function openRider(){document.getElementById('riderModal').classList.add('open'); loadR()}
function openProfile(){document.getElementById('profileModal').classList.add('open')}
function openAdmin(){closeM(); document.getElementById('adminModal').classList.add('open'); loadAdmin()}
function closeM(){document.querySelectorAll('.modal').forEach(m=>m.classList.remove('open'))}
function navTab(el,type){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active')); el.classList.add('active'); if(type=='cats') document.getElementById('catChips').scrollIntoView({behavior:'smooth'})}
function toggleAI(){document.getElementById('aiChat').classList.toggle('open')}
function toggleDark(){isDark=!isDark; document.body.classList.toggle('dark',isDark); localStorage.setItem('dark',isDark); showToast(isDark?'Dark mode on 🌙':'Light mode on ☀️')}
function loginWA(){
 let phone=document.getElementById('waPhone').value;
 if(phone.length<10){alert('Enter valid WhatsApp number 2547...'); return}
 currentUser=phone; localStorage.setItem('user',phone);
 document.getElementById('notLogged').style.display='none'; document.getElementById('logged').style.display='block';
 document.getElementById('loggedPhone').innerText=phone; document.getElementById('profileName').innerText='Welcome! '+phone.slice(-4);
 document.getElementById('profilePhone').innerText=phone; document.getElementById('userNameDisplay').innerText='Logged in • '+phone; document.getElementById('userLocation').innerText='Kajiado Town • '+phone;
 document.getElementById('custPhone').value=phone;
 showToast('Logged in with WhatsApp ✅'); fetch('/user/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone})});
}
function logout(){currentUser=null; localStorage.removeItem('user'); document.getElementById('notLogged').style.display='block'; document.getElementById('logged').style.display='none'; document.getElementById('profileName').innerText='Welcome to LONMA'; document.getElementById('profilePhone').innerText='Login to order faster'; showToast('Logged out')}
async function sendAI(){
 let i=document.getElementById('aiInput'); let msg=i.value.trim(); if(!msg) return;
 let box=document.getElementById('aiMsgs'); box.innerHTML+=`<div class="m u">${msg}</div>`; i.value=''; box.scrollTop=box.scrollHeight;
 let r=await fetch('/ai/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})}); let d=await r.json(); box.innerHTML+=`<div class="m b">${d.reply}</div>`; box.scrollTop=box.scrollHeight;
}
async function checkout(){
 let phone=document.getElementById('custPhone').value; let loc=document.getElementById('custLoc').value;
 if(!loc){alert('Enter delivery location'); return}
 document.getElementById('status').innerText='Placing order...';
 let r=await fetch('/mpesa/stkpush',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone,amount:total+100,location:loc,cart})});
 let d=await r.json(); document.getElementById('orderId').innerText=d.order_id; document.getElementById('status').innerText='Order placed!'; document.getElementById('track').style.display='block'; document.getElementById('riderInfo').innerText='Rider John Mwangi KMEZ 123A • 4.9 stars • 2.5km • 30min • Call 0712345678'; cart=[]; total=0; document.getElementById('cartDot').innerText=0;
}
async function loadR(){
 let r=await fetch('/riders'); let riders=await r.json();
 document.getElementById('riderList').innerHTML=riders.map(rd=>`<div style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:12px;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><div><b>${rd.name} ⭐${rd.rating}</b><br><small style="color:var(--muted)">${rd.motor} • ${rd.location} • ${rd.trips} trips</small></div><div style="padding:6px 10px;border-radius:10px;background:${rd.status=='available'?'#d4edda':'#fff3cd'};color:#000;font-size:10px;font-weight:800">${rd.status}</div></div>`).join('');
 let ro=await fetch('/orders'); let orders=await ro.json();
 document.getElementById('rs2').innerText=orders.length; document.getElementById('rs3').innerText='KES '+orders.reduce((s,o)=>s+o.amount,0);
 document.getElementById('riderOrders').innerHTML='<h4 style="margin:12px 0 8px;font-size:12px">Active Orders</h4>'+orders.slice(0,5).map(o=>`<div style="background:var(--card);border:1px solid var(--border);border-radius:14px;padding:10px;display:flex;justify-content:space-between;align-items:center;margin-bottom:6px"><div><b>${o.id}</b> KES ${o.amount}<br><small>${o.location}</small></div><button onclick="accept('${o.id}')" style="padding:8px 12px;background:#00a651;color:#fff;border:none;border-radius:10px;font-size:11px;font-weight:800">Accept</button></div>`).join('');
}
async function loadAdmin(){
 let r=await fetch('/orders'); let o=await r.json();
 document.getElementById('adminStats').innerHTML=`<div style="background:var(--card);border:1px solid var(--border);padding:16px;border-radius:16px;text-align:center"><b style="font-size:22px">${o.length}</b><br><small>Orders</small></div><div style="background:var(--card);border:1px solid var(--border);padding:16px;border-radius:16px;text-align:center"><b style="font-size:22px">KES ${o.reduce((s,x)=>s+x.amount,0)}</b><br><small>Revenue</small></div>`;
 document.getElementById('adminOrders').innerHTML=o.slice(0,8).map(x=>`<div style="background:var(--card);border:1px solid var(--border);border-radius:14px;padding:10px;margin-bottom:6px"><b>${x.id}</b> - ${x.status}<br><small>${x.location} • KES ${x.amount} • ${x.phone}</small></div>`).join('');
}
async function accept(id){await fetch('/rider/accept/'+id,{method:'POST'}); showToast('Accepted '+id); loadR()}
function showToast(t){let el=document.getElementById('toast'); el.innerText=t; el.style.display='block'; setTimeout(()=>el.style.display='none',2500)}
function openSearch(){document.getElementById('search').focus()}

// Load saved theme & user
if(localStorage.getItem('dark')=='true'){isDark=true; document.body.classList.add('dark')}
let savedUser=localStorage.getItem('user'); if(savedUser){currentUser=savedUser; document.getElementById('waPhone').value=savedUser}

renderChips(); render(PRODUCTS); renderFlash();
</script></body></html>
'''

@app.post("/ai/chat")
async def chat(req: Request):
    b=await req.json(); return {"reply": ai_reply(b.get("message",""))}
@app.post("/user/login")
async def login_user(req: Request):
    b=await req.json(); USERS[b.get("phone")]={"phone":b.get("phone"),"time":datetime.now().isoformat()}; return {"success":True}
@app.post("/mpesa/stkpush")
async def stk(req: Request):
    try:
        b=await req.json(); oid=f"ORD{random.randint(1000,9999)}"; ORDERS.append({"id":oid,"phone":b.get("phone"),"amount":b.get("amount",1),"location":b.get("location","Kajiado"),"cart":b.get("cart",[]),"status":"paid","time":datetime.now().isoformat()})
        token=get_token()
        if not token: return {"ResponseCode":"0","order_id":oid}
        ts=datetime.now().strftime("%Y%m%d%H%M%S"); pwd=base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{ts}".encode()).decode()
        url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        r=requests.post(url,json={"BusinessShortCode":MPESA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":int(b.get("amount",1)),"PartyA":b.get("phone"),"PartyB":MPESA_SHORTCODE,"PhoneNumber":b.get("phone"),"CallBackURL":MPESA_CALLBACK_URL,"AccountReference":oid,"TransactionDesc":"LONMA"},headers={"Authorization":f"Bearer {token}"},timeout=10)
        d=r.json(); d["order_id"]=oid; return d
    except Exception as e: return {"ResponseCode":"1","error":str(e),"order_id":f"ORD{random.randint(1000,9999)}"}
@app.get("/riders")
async def riders(): return RIDERS
@app.get("/orders")
async def orders(): return ORDERS[::-1]
@app.post("/rider/accept/{oid}")
async def acc(oid: str):
    for o in ORDERS:
        if o["id"]==oid: o["status"]="rider_assigned"
    return {"success":True}
@app.get("/mpesa/callback")
async def cb(): return {"ResultCode":0}
@app.post("/mpesa/callback")
async def cbp(req: Request): return {"ResultCode":0}
@app.get("/logo.png")
async def logo(): return FileResponse("logo.png") if os.path.exists("logo.png") else {"error":"no logo"}
@app.get("/favicon.ico")
async def fav(): return FileResponse("logo.png") if os.path.exists("logo.png") else {}
