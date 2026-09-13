from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, base64, requests, random
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MPESA_CONSUMER_KEY=os.getenv("MPESA_CONSUMER_KEY","")
MPESA_CONSUMER_SECRET=os.getenv("MPESA_CONSUMER_SECRET","")
MPESA_SHORTCODE=os.getenv("MPESA_SHORTCODE","174379")
MPESA_PASSKEY=os.getenv("MPESA_PASSKEY","")
MPESA_CALLBACK_URL=os.getenv("MPESA_CALLBACK_URL","https://app.lonmaorbit.co.ke/mpesa/callback")
MPESA_ENV=os.getenv("MPESA_ENV","sandbox")

def get_token():
    try:
        if not MPESA_CONSUMER_KEY:
            return None
        url="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        return requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET), timeout=8).json().get("access_token")
    except:
        return None

PRODUCTS=[
 {"id":1,"name":"Ajab Maize Flour 2kg","price":175,"old":195,"store":"Naivas","cat":"grocery","stock":50,"rate":4.8,"sold":234,"emoji":"🌽","color":"#FFF8E1"},
 {"id":2,"name":"Brookside Milk 500ml","price":65,"old":75,"store":"Naivas","cat":"dairy","stock":100,"rate":4.9,"sold":512,"emoji":"🥛","color":"#E3F2FD"},
 {"id":3,"name":"Coca Cola 1.25L","price":100,"old":120,"store":"Quickmart","cat":"drinks","stock":80,"rate":4.7,"sold":320,"emoji":"🥤","color":"#FFEBEE"},
 {"id":4,"name":"Omo Detergent 1kg","price":285,"old":320,"store":"Carrefour","cat":"home","stock":40,"rate":4.6,"sold":89,"emoji":"🧴","color":"#E8F5E9"},
 {"id":5,"name":"Tomatoes Fresh 1kg","price":80,"old":100,"store":"Quickmart","cat":"fresh","stock":60,"rate":4.9,"sold":445,"emoji":"🍅","color":"#FFF3E0"},
 {"id":6,"name":"White Bread 400g","price":60,"old":70,"store":"Naivas","cat":"dairy","stock":70,"rate":4.8,"sold":210,"emoji":"🍞","color":"#FFF8E1"},
 {"id":7,"name":"Pishori Rice 2kg","price":350,"old":400,"store":"Carrefour","cat":"grocery","stock":30,"rate":4.9,"sold":156,"emoji":"🍚","color":"#F3E5F5"},
 {"id":8,"name":"Geisha Soap 150g","price":55,"old":65,"store":"Magunas","cat":"care","stock":90,"rate":4.5,"sold":98,"emoji":"🧼","color":"#E0F7FA"},
]
RIDERS=[
 {"id":1,"name":"John Mwangi","motor":"KMEZ 123A","status":"available","rating":4.9,"location":"Kajiado","trips":12},
 {"id":2,"name":"Peter Ochieng","motor":"KMFA 456B","status":"delivering","rating":4.8,"location":"Kitengela","trips":28},
 {"id":3,"name":"Samuel Kiprop","motor":"KMEB 789C","status":"available","rating":5.0,"location":"Rongai","trips":15}
]
ORDERS=[]

def smart_ai_reply(message, cart_count=0):
    msg=message.lower().strip()
    if any(w in msg for w in ["hello","hi","hey","jambo","habari"]):
        return "Hello! 👋 I'm LONMA AI!\nI know prices from 5 stores.\nWhat do you need?"
    if any(w in msg for w in ["help","assist","guide"]):
        return "I can help:\n🛒 Find cheapest products\n💰 Compare prices\n🏍️ Delivery info\n📦 How to order"
    if any(w in msg for w in ["deliver","delivery","bring"]):
        return "Yes! We deliver in 30 mins 🏍️\nAreas: Kajiado, Kitengela, Rongai\nFee: KES 100\n3 riders online"
    if "flour" in msg or "unga" in msg:
        return "Ajab Flour 2kg:\n💰 KES 175 Naivas\n💰 KES 172 Carrefour (best!)\n📦 50 packs ⭐4.8"
    if "milk" in msg:
        return "Brookside Milk 500ml:\n💰 KES 65 Naivas\n💰 KES 62 Chandarana\n📦 100 fresh"
    if "cart" in msg or "order" in msg:
        return f"You have {cart_count} items. Tap + then Cart > Place Order!"
    if "cheapest" in msg:
        return "Cheapest:\n🌽 Flour 2kg KES 175\n🥛 Milk KES 65\n🍅 Tomatoes KES 80\n🍞 Bread KES 60"
    return f"Try:\n• 'Help me'\n• 'Will you deliver?'\n• 'Cheapest flour'"

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse('''
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><title>LONMA ORBIT</title>
<style>
:root{--bg:#0B0E14;--card:#151A27;--text:#F8FAFC;--muted:#94A3B8;--border:#1E293B;--teal:#0A8EA8;--teal2:#06B6D4}
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial} body{background:var(--bg);color:var(--text);padding-bottom:96px}
.header{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--border)}
.h-top{display:flex;justify-content:space-between;align-items:center;padding:14px 16px}
.logo{background:#0A8EA8;color:#fff;padding:11px 18px;border-radius:12px;font-weight:900;font-size:15px;letter-spacing:0.5px}
.icons{display:flex;gap:10px}.ic{width:46px;height:46px;background:#1A2035;border:1px solid var(--border);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px;cursor:pointer}
.h-loc{padding:0 16px 14px;display:flex;align-items:center;gap:10px}
.loc-icon{width:44px;height:44px;background:#fff;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:20px}
.h-loc b{font-size:14px;font-weight:800}.h-loc small{font-size:12px;color:var(--muted)}
.search-wrap{padding:0 16px 16px;display:flex;gap:12px}
.search-box{flex:1;background:#151A27;border:1px solid var(--border);border-radius:18px;display:flex;align-items:center;gap:12px;padding:15px 18px}
.search-box input{border:none;outline:none;background:transparent;flex:1;font-size:14px;color:var(--text)}.search-box input::placeholder{color:var(--muted)}
.filter{width:56px;height:56px;background:#1A2035;border:1px solid var(--border);border-radius:18px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:22px}
.hero{margin:0 16px 18px;background:linear-gradient(135deg,#0A8EA8 0%,#0DB5D1 60%,#14D8B8 100%);border-radius:24px;padding:20px;display:flex;justify-content:space-between;align-items:center;color:#fff;box-shadow:0 12px 30px rgba(10,142,168,0.3)}
.hero h2{font-size:20px;font-weight:900;line-height:1.15}.hero p{font-size:12px;opacity:0.95;margin-top:6px;font-weight:600}
.hero-btn{background:#fff;color:#0A8EA8;padding:12px 20px;border-radius:100px;font-weight:900;font-size:12px}
.chips{display:flex;gap:10px;overflow-x:auto;padding:0 16px 14px;scrollbar-width:none}.chips::-webkit-scrollbar{display:none}
.chip{white-space:nowrap;padding:12px 18px;border-radius:100px;background:#1A2035;border:1px solid var(--border);font-size:13px;font-weight:800;color:var(--muted)}
.chip.active{background:#fff;color:#000;border-color:#fff}
.cats{display:flex;gap:14px;overflow-x:auto;padding:4px 16px 18px;scrollbar-width:none}.cats::-webkit-scrollbar{display:none}
.cat{min-width:74px;text-align:center}
.cat-icon{width:70px;height:70px;background:#1A2035;border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:34px;border:1px solid var(--border);margin:0 auto}
.cat.active.cat-icon{background:#0A8EA8;border-color:#0A8EA8}
.cat b{font-size:12px;margin-top:8px;display:block;font-weight:700}
.section{padding:6px 16px 18px}.sec-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.sec-head h3{font-size:18px;font-weight:900}.sec-head span{font-size:13px;color:#0A8EA8;font-weight:800}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.card{background:#151A27;border-radius:24px;overflow:hidden;border:1px solid var(--border)}
.card-img{height:138px;background:#1A2035;display:flex;align-items:center;justify-content:center;font-size:58px;position:relative}
.badge{position:absolute;top:12px;left:12px;background:#FF3B30;color:#fff;font-size:11px;font-weight:900;padding:6px 10px;border-radius:100px}
.heart{position:absolute;top:12px;right:12px;width:36px;height:36px;background:#fff;border-radius:100px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#000}
.card-body{padding:12px 14px}.store{font-size:10px;font-weight:900;color:#0A8EA8;letter-spacing:0.5px;text-transform:uppercase}
.card-body h4{font-size:13.5px;font-weight:800;line-height:1.25;margin:4px 0 6px;height:34px;overflow:hidden}
.meta{font-size:11.5px;color:var(--muted);font-weight:600}
.price-row{display:flex;justify-content:space-between;align-items:center;margin-top:10px}
.price b{font-size:15px;font-weight:900}.price small{font-size:11px;color:var(--muted);text-decoration:line-through;margin-left:6px}
.add-btn{width:38px;height:38px;background:#fff;color:#000;border:none;border-radius:12px;font-size:20px;font-weight:900}
.h-scroll{display:flex;gap:12px;overflow-x:auto;scrollbar-width:none}.h-scroll::-webkit-scrollbar{display:none}
.h-card{min-width:170px;background:#151A27;border-radius:22px;padding:12px;border:1px solid var(--border)}
.bottom{position:fixed;bottom:0;left:0;right:0;background:#151A27;border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:10px 0 14px;z-index:60}
.tab{flex:1;text-align:center;position:relative}.tab-i{font-size:26px}.tab b{font-size:10.5px;display:block;margin-top:3px;font-weight:700}.tab.active{color:#0A8EA8}
.cart-dot{position:absolute;top:0;right:20px;background:#FF3B30;color:#fff;font-size:11px;font-weight:900;min-width:22px;height:22px;border-radius:100px;display:flex;align-items:center;justify-content:center;border:2px solid #151A27}
#ai{position:fixed;bottom:92px;right:16px;width:64px;height:64px;background:#0A8EA8;border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:32px;color:#fff;box-shadow:0 12px 28px rgba(10,142,168,0.5);z-index:55}
#aiChat{display:none;position:fixed;bottom:20px;left:12px;right:12px;max-width:420px;margin:0 auto;height:68vh;background:#151A27;border-radius:28px;box-shadow:0 20px 60px rgba(0,0,0,0.5);z-index:70;flex-direction:column;overflow:hidden;border:1px solid var(--border)} #aiChat.open{display:flex}
.ai-h{background:#0A8EA8;color:#fff;padding:16px 18px;display:flex;justify-content:space-between;align-items:center}
.ai-msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;background:#0B0E14}
.m{max-width:85%;padding:12px 16px;border-radius:20px;font-size:13px;line-height:1.45;font-weight:600;white-space:pre-line}
.m.u{align-self:flex-end;background:#0A8EA8;color:#fff;border-bottom-right-radius:8px}
.m.b{align-self:flex-start;background:#1A2035;border:1px solid var(--border);border-bottom-left-radius:8px}
.ai-in{display:flex;gap:10px;padding:14px;border-top:1px solid var(--border);background:#151A27}
.ai-in input{flex:1;padding:14px 18px;border-radius:100px;border:1px solid var(--border);background:#0B0E14;color:var(--text);outline:none}
.ai-in button{padding:14px 20px;background:#0A8EA8;color:#fff;border:none;border-radius:100px;font-weight:800}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);backdrop-filter:blur(12px);justify-content:center;align-items:flex-end;z-index:80}.modal.open{display:flex}
.sheet{background:#151A27;width:100%;max-width:520px;margin:0 auto;border-radius:32px 32px 0 0;max-height:90vh;overflow-y:auto;border-top:1px solid var(--border)}
.s-h{padding:20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);position:sticky;top:0;background:#151A27}
.s-c{padding:18px}.btn{width:100%;padding:16px;border:none;border-radius:18px;font-weight:800;font-size:14px;margin-top:12px}.btn-green{background:#fff;color:#000}.btn-wa{background:#25D366;color:#fff}
.input{width:100%;padding:14px 16px;border-radius:16px;border:1px solid var(--border);font-size:13.5px;margin:7px 0;background:#0B0E14;color:var(--text)}
.cart-i{display:flex;gap:14px;padding:16px 0;border-bottom:1px solid var(--border)}.ci{width:64px;height:64px;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:30px;background:#1A2035;border:1px solid var(--border)}
.toast{position:fixed;bottom:110px;left:50%;transform:translateX(-50%);background:#fff;color:#000;padding:12px 20px;border-radius:100px;font-size:12.5px;font-weight:800;z-index:100;display:none}
</style></head><body>
<div class="header">
<div class="h-top"><div class="logo">LONMA ORBIT</div><div class="icons"><div class="ic" onclick="toggleDark()">🌙</div><div class="ic">🔍</div><div class="ic">🔔</div></div></div>
<div class="h-loc"><div class="loc-icon">📍</div><div><b>Kajiado Town • 30 min delivery</b><br><small id="userStatus">Guest • Login with WhatsApp</small></div><div style="margin-left:auto;font-size:20px;opacity:0.6" onclick="openProfile()">›</div></div>
<div class="search-wrap"><div class="search-box">🔍<input id="search" placeholder="Search flour, milk, bread..." oninput="searchProd()"></div><div class="filter">☰</div></div>
</div>
<div class="hero"><div><h2>Free Delivery<br>on First 3 Orders!</h2><p>Use code LONMA30 • Smart AI Bot</p></div><div class="hero-btn">ORDER NOW</div></div>
<div class="chips" id="storeChips"></div>
<div class="cats" id="catChips"></div>
<div class="section"><div class="sec-head"><h3>Best Deals Today</h3><span>See All</span></div><div class="grid" id="grid"></div></div>
<div class="section"><div class="sec-head"><h3>Flash Sale</h3><span style="color:#FF3B30" id="timer">Ends 02:14:33</span></div><div class="h-scroll" id="flash"></div></div>
<div class="bottom">
<div class="tab active"><div class="tab-i">🏠</div><b>Home</b></div>
<div class="tab" onclick="document.getElementById('catChips').scrollIntoView({behavior:'smooth'})"><div class="tab-i">📁</div><b>Categories</b></div>
<div class="tab" onclick="openCart()"><div class="tab-i">🛒</div><b>Cart</b><div class="cart-dot" id="cartDot">0</div></div>
<div class="tab" onclick="openRider()"><div class="tab-i">🏍️</div><b>Rider</b></div>
<div class="tab" onclick="openProfile()"><div class="tab-i">👤</div><b>Profile</b></div>
</div>
<div id="ai" onclick="toggleAI()">🤖</div>
<div id="aiChat"><div class="ai-h"><div><b>LONMA AI</b><div style="font-size:11px;opacity:0.9">Online • Smart Bot</div></div><div onclick="toggleAI()" style="width:36px;height:36px;background:rgba(255,255,255,0.2);border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="ai-msgs" id="aiMsgs"><div class="m b">Hello! 👋 I'm LONMA AI
Try:
• Help me
• Will you deliver?
• Cheapest flour</div></div><div class="ai-in"><input id="aiInput" placeholder="Ask anything..." onkeypress="if(event.key==='Enter') sendAI()"><button onclick="sendAI()">Send</button></div></div>
<div id="cartModal" class="modal"><div class="sheet"><div class="s-h"><h3>Cart (<span id="cartC">0</span>)</h3><div onclick="closeM()" style="width:40px;height:40px;background:#0B0E14;border-radius:14px;display:flex;align-items:center;justify-content:center">✕</div></div><div class="s-c"><div id="cartItems"></div><div style="background:#0B0E14;border-radius:20px;padding:16px;margin:16px 0;border:1px solid var(--border)"><div style="display:flex;justify-content:space-between;font-size:13px;margin:6px 0"><span>Subtotal</span><b>KES <span id="sub">0</span></b></div><div style="display:flex;justify-content:space-between;font-size:13px;margin:6px 0"><span>Delivery</span><b>KES 100</b></div><div style="display:flex;justify-content:space-between;font-size:15px;font-weight:800;border-top:1px solid var(--border);margin-top:10px;padding-top:12px"><span>Total</span><b>KES <span id="grand">0</span></b></div></div><input id="custName" class="input" placeholder="Full Name"><input id="custPhone" class="input" value="254" placeholder="M-Pesa Phone"><input id="custLoc" class="input" placeholder="Delivery Location"><button class="btn btn-green" onclick="checkout()">Place Order - Rider 30min</button><div id="status" style="text-align:center;font-size:11px;font-weight:700;margin-top:10px"></div><div id="track" style="display:none;margin-top:14px;background:#DCFCE7;border-radius:20px;padding:16px;color:#14532D"><b>Order <span id="orderId"></span> Confirmed!</b><p style="font-size:11.5px;margin-top:6px" id="riderInfo">Rider assigned</p></div></div></div></div>
<div id="riderModal" class="modal"><div class="sheet"><div class="s-h"><h3>Rider Center</h3><div onclick="closeM()" style="width:40px;height:40px;background:#0B0E14;border-radius:14px;display:flex;align-items:center;justify-content:center">✕</div></div><div class="s-c"><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px"><div style="background:#1A2035;padding:16px;border-radius:20px;text-align:center;border:1px solid var(--border)"><b>3</b><br><small style="font-size:10px">ONLINE</small></div><div style="background:#1A2035;padding:16px;border-radius:20px;text-align:center;border:1px solid var(--border)"><b id="rs2">0</b><br><small style="font-size:10px">ORDERS</small></div><div style="background:#1A2035;padding:16px;border-radius:20px;text-align:center;border:1px solid var(--border)"><b id="rs3">KES 0</b><br><small style="font-size:10px">SALES</small></div></div><div id="riderList" style="margin-top:16px"></div><div id="riderOrders" style="margin-top:12px"></div></div></div></div>
<div id="profileModal" class="modal"><div class="sheet"><div class="s-h"><h3>Profile</h3><div onclick="closeM()" style="width:40px;height:40px;background:#0B0E14;border-radius:14px;display:flex;align-items:center;justify-content:center">✕</div></div><div class="s-c"><div style="text-align:center;padding:8px 0 22px"><div style="width:88px;height:88px;background:#0A8EA8;border-radius:28px;display:flex;align-items:center;justify-content:center;font-size:40px;color:#fff;margin:0 auto">👤</div><h3 style="margin-top:14px" id="profileName">Welcome</h3><small style="color:var(--muted)" id="profilePhone">Login to order faster</small></div><div id="notLogged"><input id="waPhone" class="input" value="254" placeholder="WhatsApp 254712..."><button class="btn btn-wa" onclick="loginWA()">Login with WhatsApp</button></div><div id="logged" style="display:none"><div style="background:#DCFCE7;border-radius:18px;padding:14px;text-align:center;color:#14532D"><b>Logged in ✓</b><br><small id="loggedPhone">254...</small></div><button class="btn" style="background:#fff;color:#000;margin-top:12px" onclick="logout()">Logout</button></div></div></div></div>
<div id="adminModal" class="modal"><div class="sheet"><div class="s-h"><h3>Admin</h3><div onclick="closeM()" style="width:40px;height:40px;background:#0B0E14;border-radius:14px;display:flex;align-items:center;justify-content:center">✕</div></div><div class="s-c"><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px" id="adminStats"></div><div id="adminOrders" style="margin-top:14px"></div></div></div></div>
<div class="toast" id="toast"></div>
<script>
var PRODUCTS = [
{id:1,name:"Ajab Maize Flour 2kg",price:175,old:195,store:"Naivas",cat:"grocery",rate:4.8,sold:234,emoji:"🌽",color:"#2A2F45"},
{id:2,name:"Brookside Milk 500ml",price:65,old:75,store:"Naivas",cat:"dairy",rate:4.9,sold:512,emoji:"🥛",color:"#2A2F45"},
{id:3,name:"Coca Cola 1.25L",price:100,old:120,store:"Quickmart",cat:"drinks",rate:4.7,sold:320,emoji:"🥤",color:"#2A2F45"},
{id:4,name:"Omo Detergent 1kg",price:285,old:320,store:"Carrefour",cat:"home",rate:4.6,sold:89,emoji:"🧴",color:"#2A2F45"},
{id:5,name:"Tomatoes Fresh 1kg",price:80,old:100,store:"Quickmart",cat:"fresh",rate:4.9,sold:445,emoji:"🍅",color:"#2A2F45"},
{id:6,name:"White Bread 400g",price:60,old:70,store:"Naivas",cat:"dairy",rate:4.8,sold:210,emoji:"🍞",color:"#2A2F45"},
{id:7,name:"Pishori Rice 2kg",price:350,old:400,store:"Carrefour",cat:"grocery",rate:4.9,sold:156,emoji:"🍚",color:"#2A2F45"},
{id:8,name:"Geisha Soap 150g",price:55,old:65,store:"Magunas",cat:"care",rate:4.5,sold:98,emoji:"🧼",color:"#2A2F45"}
];
var STORES = ["ALL","Naivas","Quickmart","Carrefour","Chandarana","Magunas"];
var CATS = [
{id:"all",name:"All",icon:"🏬"},
{id:"fresh",name:"Fresh",icon:"🥬"},
{id:"grocery",name:"Grocery",icon:"🌽"},
{id:"drinks",name:"Drinks",icon:"🥤"},
{id:"dairy",name:"Dairy",icon:"🥛"}
];
var cart = []; var total = 0; var activeStore = "ALL"; var activeCat = "all";

function renderChips(){
 var sHtml = ""; for(var i=0;i<STORES.length;i++){ var s=STORES[i]; sHtml += '<div class="'+(s===activeStore?'chip active':'chip')+'" onclick="setStore(\\''+s+'\\')">'+s+'</div>'; }
 document.getElementById("storeChips").innerHTML = sHtml;
 var cHtml = ""; for(var j=0;j<CATS.length;j++){ var c=CATS[j]; cHtml += '<div class="cat '+(c.id===activeCat?'active':'')+'" onclick="setCat(\\''+c.id+'\\')"><div class="cat-icon">'+c.icon+'</div><b>'+c.name+'</b></div>'; }
 document.getElementById("catChips").innerHTML = cHtml;
}
function renderProducts(list){
 var html = ""; for(var i=0;i<list.length;i++){ var p=list[i]; var disc=Math.round((p.old-p.price)/p.old*100); html += '<div class="card"><div class="card-img">'+p.emoji+'<div class="badge">-'+disc+'%</div><div class="heart">♡</div></div><div class="card-body"><div class="store">'+p.store+'</div><h4>'+p.name+'</h4><div class="meta">⭐ '+p.rate+' • '+p.sold+' sold</div><div class="price-row"><div class="price"><b>KES '+p.price+'</b><small>KES '+p.old+'</small></div><button class="add-btn" onclick="addToCart('+p.id+')">+</button></div></div></div>'; }
 document.getElementById("grid").innerHTML = html;
}
function renderFlash(){
 var html = ""; for(var i=0;i<4;i++){ var p=PRODUCTS[i]; html += '<div class="h-card"><div style="font-size:36px;text-align:center;padding:12px;background:#1A2035;border-radius:16px;margin-bottom:8px">'+p.emoji+'</div><div style="font-size:11.5px;font-weight:700">'+p.name+'</div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px"><b>KES '+p.price+'</b><button class="add-btn" style="width:30px;height:30px;font-size:16px" onclick="addToCart('+p.id+')">+</button></div></div>'; }
 document.getElementById("flash").innerHTML = html;
}
function setStore(s){ activeStore=s; renderChips(); filterProducts(); }
function setCat(c){ activeCat=c; renderChips(); filterProducts(); }
function filterProducts(){
 var filtered=[]; for(var i=0;i<PRODUCTS.length;i++){ var p=PRODUCTS[i]; if((activeStore==="ALL"||p.store===activeStore)&&(activeCat==="all"||p.cat===activeCat)) filtered.push(p); }
 renderProducts(filtered);
}
function searchProd(){
 var q=document.getElementById("search").value.toLowerCase(); if(!q){renderProducts(PRODUCTS);return;}
 var f=[]; for(var i=0;i<PRODUCTS.length;i++){ var p=PRODUCTS[i]; if(p.name.toLowerCase().indexOf(q)>-1) f.push(p); } renderProducts(f);
}
function addToCart(id){
 var p=null; for(var i=0;i<PRODUCTS.length;i++){ if(PRODUCTS[i].id===id) p=PRODUCTS[i]; }
 if(!p) return; cart.push(p); total+=p.price;
 document.getElementById("cartDot").innerText=cart.length;
 document.getElementById("cartC").innerText=cart.length;
 showToast(p.name+" added ✓");
}
function openCart(){
 var d=document.getElementById("cartItems");
 if(cart.length===0){ d.innerHTML='<p style="text-align:center;padding:28px;color:var(--muted)">Cart empty</p>'; }
 else { var html=""; for(var i=0;i<cart.length;i++){ var c=cart[i]; html+='<div class="cart-i"><div class="ci">'+c.emoji+'</div><div style="flex:1"><h4 style="font-size:13px;font-weight:700">'+c.name+'</h4><small style="color:var(--muted)">'+c.store+' • KES '+c.price+'</small></div><b>KES '+c.price+'</b></div>'; } d.innerHTML=html; }
 document.getElementById("sub").innerText=total; document.getElementById("grand").innerText=total+100;
 document.getElementById("cartModal").classList.add("open");
}
function openRider(){ document.getElementById("riderModal").classList.add("open"); loadRiders(); }
function openProfile(){ document.getElementById("profileModal").classList.add("open"); }
function openAdmin(){ closeM(); document.getElementById("adminModal").classList.add("open"); loadAdmin(); }
function closeM(){ var modals=document.querySelectorAll(".modal"); for(var i=0;i<modals.length;i++) modals[i].classList.remove("open"); }
function toggleAI(){ document.getElementById("aiChat").classList.toggle("open"); }
function loginWA(){
 var phone=document.getElementById("waPhone").value;
 if(phone.length<10){ alert("Enter valid number"); return; }
 localStorage.setItem("user",phone);
 document.getElementById("notLogged").style.display="none"; document.getElementById("logged").style.display="block";
 document.getElementById("loggedPhone").innerText=phone; document.getElementById("profileName").innerText="Welcome! "+phone.slice(-4);
 document.getElementById("profilePhone").innerText=phone; document.getElementById("userStatus").innerText="Logged in • "+phone;
 document.getElementById("custPhone").value=phone;
 showToast("Logged in ✅"); fetch("/user/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone})});
}
function logout(){ localStorage.removeItem("user"); document.getElementById("notLogged").style.display="block"; document.getElementById("logged").style.display="none"; document.getElementById("profileName").innerText="Welcome"; document.getElementById("profilePhone").innerText="Login to order faster"; showToast("Logged out"); }
async function sendAI(){
 var input=document.getElementById("aiInput"); var msg=input.value.trim(); if(!msg) return;
 var box=document.getElementById("aiMsgs");
 box.innerHTML+='<div class="m u">'+msg+'</div>'; input.value=""; box.scrollTop=box.scrollHeight;
 try{
   var r=await fetch("/ai/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg,cart_count:cart.length})});
   var d=await r.json();
   box.innerHTML+='<div class="m b">'+d.reply+'</div>';
 } catch(e){
   box.innerHTML+='<div class="m b">Error, try again</div>';
 }
 box.scrollTop=box.scrollHeight;
}
async function checkout(){
 var phone=document.getElementById("custPhone").value; var loc=document.getElementById("custLoc").value;
 if(!loc){ alert("Enter location"); return; }
 document.getElementById("status").innerText="Placing order...";
 var r=await fetch("/mpesa/stkpush",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone,amount:total+100,location:loc,cart:cart})});
 var d=await r.json(); document.getElementById("orderId").innerText=d.order_id; document.getElementById("status").innerText="Order placed!"; document.getElementById("track").style.display="block"; document.getElementById("riderInfo").innerText="Rider John KMEZ 123A • 4.9★ • 30min"; cart=[]; total=0; document.getElementById("cartDot").innerText=0;
}
async function loadRiders(){
 var r=await fetch("/riders"); var riders=await r.json();
 var html=""; for(var i=0;i<riders.length;i++){ var rd=riders[i]; html+='<div style="background:#1A2035;border:1px solid var(--border);border-radius:20px;padding:14px;display:flex;justify-content:space-between;align-items:center;margin-bottom:10px"><div><b>'+rd.name+' ⭐'+rd.rating+'</b><br><small style="color:var(--muted)">'+rd.motor+' • '+rd.location+'</small></div><div style="padding:7px 12px;border-radius:100px;background:'+(rd.status==="available"?"#DCFCE7":"#FEF3C7")+';color:#000;font-size:10px;font-weight:800">'+rd.status.toUpperCase()+'</div></div>'; }
 document.getElementById("riderList").innerHTML=html;
 var ro=await fetch("/orders"); var orders=await ro.json();
 document.getElementById("rs2").innerText=orders.length; document.getElementById("rs3").innerText="KES "+orders.reduce(function(s,o){return s+o.amount},0);
 var oh='<h4 style="margin:14px 0 10px;font-size:13px;font-weight:800">Active Orders</h4>'; for(var j=0;j<Math.min(orders.length,5);j++){ var o=orders[j]; oh+='<div style="background:#1A2035;border:1px solid var(--border);border-radius:18px;padding:12px;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><div><b>'+o.id+'</b> KES '+o.amount+'<br><small style="color:var(--muted)">'+o.location+'</small></div><button onclick="acceptOrder(\\''+o.id+'\\')" style="padding:9px 14px;background:#fff;color:#000;border:none;border-radius:100px;font-size:11px;font-weight:800">Accept</button></div>'; }
 document.getElementById("riderOrders").innerHTML=oh;
}
async function loadAdmin(){
 var r=await fetch("/orders"); var o=await r.json();
 document.getElementById("adminStats").innerHTML='<div style="background:#1A2035;border:1px solid var(--border);padding:18px;border-radius:20px;text-align:center"><b style="font-size:24px">'+o.length+'</b><br><small style="color:var(--muted);font-size:10px">ORDERS</small></div><div style="background:#1A2035;border:1px solid var(--border);padding:18px;border-radius:20px;text-align:center"><b style="font-size:20px">KES '+o.reduce(function(s,x){return s+x.amount},0)+'</b><br><small style="color:var(--muted);font-size:10px">REVENUE</small></div>';
 var html=""; for(var i=0;i<Math.min(o.length,8);i++){ var x=o[i]; html+='<div style="background:#1A2035;border:1px solid var(--border);border-radius:18px;padding:12px;margin-bottom:8px"><b>'+x.id+'</b> - '+x.status+'<br><small style="color:var(--muted)">'+x.location+' • KES '+x.amount+'</small></div>'; }
 document.getElementById("adminOrders").innerHTML=html;
}
async function acceptOrder(id){ await fetch("/rider/accept/"+id,{method:"POST"}); showToast("Accepted "+id+" ✓"); loadRiders(); }
function showToast(t){ var el=document.getElementById("toast"); el.innerText=t; el.style.display="block"; setTimeout(function(){el.style.display="none"},2600); }

renderChips(); renderProducts(PRODUCTS); renderFlash();
var timeLeft=2*3600+14*60+33; setInterval(function(){ timeLeft--; var h=Math.floor(timeLeft/3600); var m=Math.floor((timeLeft%3600)/60); var s=timeLeft%60; var el=document.getElementById("timer"); if(el) el.innerText="Ends "+(h<10?"0"+h:h)+":"+(m<10?"0"+m:m)+":"+(s<10?"0"+s:s); },1000);
</script></body></html>
''')

@app.post("/ai/chat")
async def chat(req: Request):
    try:
        b=await req.json()
        msg=b.get("message","")
        cart_count=b.get("cart_count",0)
        reply=smart_ai_reply(msg, cart_count)
        return {"reply": reply, "quick": ["Help me","Will you deliver?","Cheapest flour"]}
    except:
        return {"reply": "Try: Help me, Will you deliver?, Cheapest flour", "quick": []}

@app.post("/user/login")
async def login_user(req: Request):
    return {"success":True}

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    try:
        b=await req.json()
        oid=f"ORD{random.randint(1000,9999)}"
        ORDERS.append({"id":oid,"phone":b.get("phone"),"amount":b.get("amount",1),"location":b.get("location","Kajiado"),"cart":b.get("cart",[]),"status":"paid","time":datetime.now().isoformat()})
        token=get_token()
        if not token:
            return {"ResponseCode":"0","order_id":oid}
        ts=datetime.now().strftime("%Y%m%d%H%M%S")
        pwd=base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{ts}".encode()).decode()
        url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        r=requests.post(url,json={"BusinessShortCode":MPESA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":int(b.get("amount",1)),"PartyA":b.get("phone"),"PartyB":MPESA_SHORTCODE,"PhoneNumber":b.get("phone"),"CallBackURL":MPESA_CALLBACK_URL,"AccountReference":oid,"TransactionDesc":"LONMA"},headers={"Authorization":f"Bearer {token}"},timeout=10)
        d=r.json()
        d["order_id"]=oid
        return d
    except Exception as e:
        return {"ResponseCode":"1","error":str(e),"order_id":f"ORD{random.randint(1000,9999)}"}

@app.get("/riders")
async def riders():
    return RIDERS

@app.get("/orders")
async def orders():
    return ORDERS[::-1]

@app.post("/rider/accept/{oid}")
async def acc(oid: str):
    for o in ORDERS:
        if o["id"]==oid:
            o["status"]="rider_assigned"
    return {"success":True}

@app.get("/mpesa/callback")
async def cb():
    return {"ResultCode":0}

@app.post("/mpesa/callback")
async def cbp(req: Request):
    return {"ResultCode":0}

@app.get("/favicon.ico")
async def fav():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    return HTMLResponse("", status_code=404)
