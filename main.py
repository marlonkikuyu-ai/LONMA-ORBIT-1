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
        if not MPESA_CONSUMER_KEY: return None
        url="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        return requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET), timeout=8).json().get("access_token")
    except: return None

ORDERS=[]
RIDERS=[
 {"id":1,"name":"John Mwangi","motor":"KMEZ 123A","status":"available","rating":4.9,"location":"Kajiado","trips":12},
 {"id":2,"name":"Peter Ochieng","motor":"KMFA 456B","status":"delivering","rating":4.8,"location":"Kitengela","trips":28},
 {"id":3,"name":"Samuel Kiprop","motor":"KMEB 789C","status":"available","rating":5.0,"location":"Rongai","trips":15}
]

def smart_ai_reply(message, cart_count=0):
    msg=message.lower().strip()
    if any(w in msg for w in ["hello","hi","hey","jambo"]): return "Hello! 👋 I'm LONMA AI! What do you need?"
    if "help" in msg: return "I can help:\n🛒 Find cheapest\n💰 Compare prices\n🏍️ Delivery info\n📦 How to order\n💳 Pay M-Pesa or Cash"
    if "deliver" in msg: return "Yes! 30 mins 🏍️\nKajiado, Kitengela, Rongai\nFee KES 100\n3 riders online"
    if "pay" in msg: return "Payment:\n💚 M-Pesa STK Push - Enter PIN\n💵 Cash on Delivery\nBoth work instantly!"
    return "Try: Help me, Will you deliver?, How to pay?"

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse('''
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><title>LONMA ORBIT</title>
<style>
:root{--bg:#0B0E14;--card:#151A27;--text:#F8FAFC;--muted:#94A3B8;--border:#1E293B;--teal:#0A8EA8}
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial} body{background:var(--bg);color:var(--text);padding-bottom:110px;overflow-x:hidden}
.header{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--border)}
.h-top{display:flex;justify-content:space-between;align-items:center;padding:14px 16px}
.logo{background:#0A8EA8;color:#fff;padding:11px 18px;border-radius:12px;font-weight:900;font-size:15px;letter-spacing:0.5px}
.icons{display:flex;gap:10px}.ic{width:46px;height:46px;background:#1A2035;border:1px solid var(--border);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:20px}
.h-loc{padding:0 16px 14px;display:flex;align-items:center;gap:10px}
.loc-icon{width:44px;height:44px;background:#fff;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:20px}
.h-loc b{font-size:14px;font-weight:800}.h-loc small{font-size:12px;color:var(--muted)}
.search-wrap{padding:0 16px 16px;display:flex;gap:12px}
.search-box{flex:1;background:#151A27;border:1px solid var(--border);border-radius:18px;display:flex;align-items:center;gap:12px;padding:15px 18px}
.search-box input{border:none;outline:none;background:transparent;flex:1;font-size:14px;color:var(--text)}
.filter{width:56px;height:56px;background:#1A2035;border:1px solid var(--border);border-radius:18px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:22px}
.hero{margin:0 16px 18px;background:linear-gradient(135deg,#0A8EA8 0%,#0DB5D1 60%,#14D8B8 100%);border-radius:24px;padding:20px;display:flex;justify-content:space-between;align-items:center;color:#fff;cursor:pointer}
.hero h2{font-size:20px;font-weight:900;line-height:1.15}.hero p{font-size:12px;margin-top:6px;opacity:0.9}
.hero-btn{background:#fff;color:#0A8EA8;padding:12px 20px;border-radius:100px;font-weight:900;font-size:12px;box-shadow:0 4px 12px rgba(0,0,0,0.15)}
.chips{display:flex;gap:10px;overflow-x:auto;padding:0 16px 14px;scrollbar-width:none}.chips::-webkit-scrollbar{display:none}
.chip{white-space:nowrap;padding:12px 18px;border-radius:100px;background:#1A2035;border:1px solid var(--border);font-size:13px;font-weight:800;color:var(--muted);cursor:pointer;flex-shrink:0}
.chip.active{background:#fff;color:#000;border-color:#fff}
.cats{display:flex;gap:14px;overflow-x:auto;padding:4px 16px 18px;scrollbar-width:none}.cats::-webkit-scrollbar{display:none}
.cat{min-width:74px;text-align:center;cursor:pointer;flex-shrink:0}.cat-icon{width:70px;height:70px;background:#1A2035;border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:34px;border:1px solid var(--border);margin:0 auto;overflow:hidden}
.cat-icon img{width:100%;height:100%;object-fit:cover;border-radius:22px}
.cat.active.cat-icon{border:2px solid #0A8EA8;box-shadow:0 0 0 3px rgba(10,142,168,0.25)}
.cat b{font-size:12px;margin-top:8px;display:block;font-weight:700}
.section{padding:6px 16px 18px}.sec-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.sec-head h3{font-size:18px;font-weight:900}.sec-head span{font-size:13px;color:#0A8EA8;font-weight:800;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.card{background:#151A27;border-radius:24px;overflow:hidden;border:1px solid var(--border);transition:0.2s}
.card:active{transform:scale(0.98)}
.card-img{height:148px;background:#fff;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;padding:10px}
.card-img img{width:100%;height:100%;object-fit:contain;mix-blend-mode:multiply}
.card-img.emoji-fallback{font-size:58px}
.badge{position:absolute;top:12px;left:12px;background:#FF3B30;color:#fff;font-size:11px;font-weight:900;padding:6px 10px;border-radius:100px;z-index:2}
.heart{position:absolute;top:12px;right:12px;width:36px;height:36px;background:#fff;border-radius:100px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#000;box-shadow:0 2px 8px rgba(0,0,0,0.1);z-index:2}
.card-body{padding:12px 14px}.store{font-size:10px;font-weight:900;color:#0A8EA8;text-transform:uppercase;letter-spacing:0.5px}
.card-body h4{font-size:13.5px;font-weight:800;margin:4px 0 6px;height:36px;overflow:hidden;line-height:1.25}
.meta{font-size:11.5px;color:var(--muted)}.price-row{display:flex;justify-content:space-between;align-items:center;margin-top:10px;gap:6px}
.price{display:flex;align-items:baseline;gap:5px;flex-wrap:nowrap;white-space:nowrap}
.price b{font-size:15px;font-weight:900}.price small{font-size:11px;color:var(--muted);text-decoration:line-through}
.add-btn{width:38px;height:38px;background:#fff;color:#000;border:none;border-radius:12px;font-size:20px;font-weight:900;cursor:pointer;flex-shrink:0;box-shadow:0 2px 8px rgba(0,0,0,0.1)}
.h-scroll{display:flex;gap:12px;overflow-x:auto;scrollbar-width:none}.h-scroll::-webkit-scrollbar{display:none}
.h-card{min-width:170px;background:#151A27;border-radius:22px;padding:12px;border:1px solid var(--border);flex-shrink:0}
.h-card-img{height:90px;background:#fff;border-radius:14px;display:flex;align-items:center;justify-content:center;padding:8px;margin-bottom:8px}
.h-card-img img{width:100%;height:100%;object-fit:contain}
.bottom{position:fixed;bottom:0;left:0;right:0;background:#151A27;border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:10px 0 max(14px, env(safe-area-inset-bottom));z-index:60}
.tab{flex:1;text-align:center;position:relative;cursor:pointer}.tab-i{font-size:24px}.tab b{font-size:10px;display:block;margin-top:3px;font-weight:700}.tab.active{color:#0A8EA8}
.cart-dot{position:absolute;top:-4px;right:18px;background:#FF3B30;color:#fff;font-size:11px;font-weight:900;min-width:22px;height:22px;border-radius:100px;display:flex;align-items:center;justify-content:center;border:2px solid #151A27}
#ai{position:fixed;bottom:118px;right:16px;width:62px;height:62px;background:#0A8EA8;border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:30px;color:#fff;box-shadow:0 12px 28px rgba(10,142,168,0.45);z-index:55;cursor:pointer}
#aiChat{display:none;position:fixed;bottom:20px;left:12px;right:12px;max-width:420px;margin:0 auto;height:68vh;background:#151A27;border-radius:28px;box-shadow:0 20px 60px rgba(0,0,0,0.5);z-index:70;flex-direction:column;overflow:hidden;border:1px solid var(--border)} #aiChat.open{display:flex}
.ai-h{background:#0A8EA8;color:#fff;padding:16px 18px;display:flex;justify-content:space-between;align-items:center}
.ai-msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;background:#0B0E14}
.m{max-width:85%;padding:12px 16px;border-radius:20px;font-size:13px;line-height:1.45;white-space:pre-line}
.m.u{align-self:flex-end;background:#0A8EA8;color:#fff}.m.b{align-self:flex-start;background:#1A2035;border:1px solid var(--border)}
.ai-in{display:flex;gap:10px;padding:14px;border-top:1px solid var(--border);background:#151A27}
.ai-in input{flex:1;padding:14px 18px;border-radius:100px;border:1px solid var(--border);background:#0B0E14;color:var(--text);outline:none}
.ai-in button{padding:14px 20px;background:#0A8EA8;color:#fff;border:none;border-radius:100px;font-weight:800}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(16px);justify-content:center;align-items:flex-end;z-index:80}.modal.open{display:flex}
.sheet{background:#151A27;width:100%;max-width:520px;margin:0 auto;border-radius:32px 32px 0 0;max-height:92vh;overflow-y:auto;border-top:1px solid var(--border)}
.s-h{padding:20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);position:sticky;top:0;background:#151A27;z-index:2}
.s-c{padding:18px}.btn{width:100%;padding:16px;border:none;border-radius:18px;font-weight:800;font-size:14px;margin-top:12px;cursor:pointer}
.btn-green{background:#fff;color:#000}.btn-wa{background:#25D366;color:#fff}.btn-mpesa{background:#0A8EA8;color:#fff}.btn-cash{background:#1A2035;color:#fff;border:1.5px solid var(--border)}
.input{width:100%;padding:14px 16px;border-radius:16px;border:1px solid var(--border);font-size:13.5px;margin:7px 0;background:#0B0E14;color:var(--text);outline:none}
.pay-methods{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}
.pay-opt{padding:14px;border-radius:16px;border:2px solid var(--border);background:#1A2035;cursor:pointer;text-align:center}
.pay-opt.active{border-color:#0A8EA8;background:rgba(10,142,168,0.15)}
.pay-status{display:none;margin-top:14px;padding:16px;border-radius:18px;text-align:center;font-weight:700}.pay-status.show{display:block}
.pay-status.mpesa{background:linear-gradient(135deg,#0A8EA8,#0DB5D1);color:#fff}
.pay-status.cash{background:#FEF3C7;color:#92400E}.pay-status.success{background:#DCFCE7;color:#14532D;border:1px solid #86EFAC}
.loader{width:18px;height:18px;border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:spin 0.8s linear infinite;display:inline-block;margin-right:8px;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}
.cart-i{display:flex;gap:14px;padding:16px 0;border-bottom:1px solid var(--border)}.ci{width:64px;height:64px;border-radius:18px;display:flex;align-items:center;justify-content:center;background:#fff;border:1px solid var(--border);overflow:hidden;padding:6px}
.ci img{width:100%;height:100%;object-fit:contain}
.toast{position:fixed;bottom:120px;left:50%;transform:translateX(-50%);background:#fff;color:#000;padding:12px 20px;border-radius:100px;font-size:12.5px;font-weight:800;z-index:100;display:none;box-shadow:0 8px 20px rgba(0,0,0,0.3);max-width:90%;white-space:nowrap}
</style></head><body>
<div class="header">
<div class="h-top"><div class="logo">LONMA ORBIT</div><div class="icons"><div class="ic">🌙</div><div class="ic">🔍</div><div class="ic">🔔</div></div></div>
<div class="h-loc"><div class="loc-icon">📍</div><div><b>Kajiado Town • 30 min delivery</b><br><small id="userStatus">Guest • Login</small></div><div style="margin-left:auto;font-size:20px;opacity:0.6" onclick="openProfile()">›</div></div>
<div class="search-wrap"><div class="search-box">🔍<input id="search" placeholder="Search flour, milk, bread..." oninput="searchProd()"></div><div class="filter">☰</div></div>
</div>
<div class="hero" onclick="orderNow()"><div><h2>Free Delivery<br>on First 3 Orders!</h2><p>Use code LONMA30 • Tap to order</p></div><div class="hero-btn">ORDER NOW</div></div>
<div class="chips" id="storeChips"></div>
<div class="cats" id="catChips"></div>
<div class="section"><div class="sec-head"><h3>Best Deals Today</h3><span onclick="renderProducts(PRODUCTS)">See All</span></div><div class="grid" id="grid"></div></div>
<div class="section"><div class="sec-head"><h3>Flash Sale</h3><span style="color:#FF3B30" id="timer">Ends 02:14:33</span></div><div class="h-scroll" id="flash"></div></div>
<div class="bottom">
<div class="tab active"><div class="tab-i">🏠</div><b>Home</b></div>
<div class="tab"><div class="tab-i">📁</div><b>Categories</b></div>
<div class="tab" onclick="openCart()"><div class="tab-i">🛒</div><b>Cart</b><div class="cart-dot" id="cartDot">0</div></div>
<div class="tab" onclick="openRider()"><div class="tab-i">🏍️</div><b>Rider</b></div>
<div class="tab" onclick="openProfile()"><div class="tab-i">👤</div><b>Profile</b></div>
</div>
<div id="ai" onclick="toggleAI()">🤖</div>
<div id="aiChat"><div class="ai-h"><div><b>LONMA AI</b><div style="font-size:11px;opacity:0.9">Online • Tap to ask</div></div><div onclick="toggleAI()" style="width:36px;height:36px;background:rgba(255,255,255,0.2);border-radius:12px;display:flex;align-items:center;justify-content:center">✕</div></div><div class="ai-msgs" id="aiMsgs"><div class="m b">Hello! 👋 I'm LONMA AI\nTap ORDER NOW or try: Cheapest flour, How to pay?</div></div><div class="ai-in"><input id="aiInput" placeholder="Ask..." onkeypress="if(event.key==='Enter') sendAI()"><button onclick="sendAI()">Send</button></div></div>
<div id="cartModal" class="modal"><div class="sheet"><div class="s-h"><h3>Cart (<span id="cartC">0</span>)</h3><div onclick="closeM()" style="width:40px;height:40px;background:#0B0E14;border-radius:14px;display:flex;align-items:center;justify-content:center">✕</div></div><div class="s-c">
<div id="cartItems"></div>
<div style="background:#0B0E14;border-radius:20px;padding:16px;margin:16px 0;border:1px solid var(--border)"><div style="display:flex;justify-content:space-between;font-size:13px;margin:6px 0"><span>Subtotal</span><b>KES <span id="sub">0</span></b></div><div style="display:flex;justify-content:space-between;font-size:13px;margin:6px 0"><span>Delivery</span><b>KES 100</b></div><div style="display:flex;justify-content:space-between;font-size:15px;font-weight:800;border-top:1px solid var(--border);margin-top:10px;padding-top:12px"><span>Total</span><b>KES <span id="grand">0</span></b></div></div>
<input id="custName" class="input" placeholder="Full Name (e.g. Marlon)"><input id="custPhone" class="input" value="254" placeholder="M-Pesa Phone 254707..."><input id="custLoc" class="input" placeholder="Delivery Location (e.g. Thika)">
<div style="margin-top:16px"><b style="font-size:13px">Choose Payment</b>
<div class="pay-methods"><div class="pay-opt active" id="payMpesa" onclick="setPay('mpesa')"><div style="font-size:22px">💚</div><b>M-Pesa</b><br><small>STK Push • Instant</small></div><div class="pay-opt" id="payCash" onclick="setPay('cash')"><div style="font-size:22px">💵</div><b>Cash</b><br><small>Pay rider</small></div></div></div>
<div id="mpesaStatus" class="pay-status mpesa"><span class="loader"></span> Sending to <span id="mpesaPhoneDisplay">254...</span><br><small style="font-size:11px;margin-top:6px;display:block">Check phone - Enter PIN for KES <span id="payAmount">0</span></small></div>
<div id="cashStatus" class="pay-status cash">💵 Cash on Delivery<br><small>Pay KES <span id="cashAmount">0</span> to rider in 30 mins</small></div>
<div id="successStatus" class="pay-status success"><b>Order <span id="orderId"></span> Confirmed! 🎉</b><p style="font-size:11.5px;margin-top:6px" id="riderInfo">Rider assigned</p><p style="font-size:10px;margin-top:8px;opacity:0.8" id="paymentNote"></p></div>
<button class="btn btn-mpesa" id="placeBtn" onclick="checkout()">💚 Pay with M-Pesa - 30min</button>
<button class="btn btn-cash" id="cashBtn" onclick="checkoutCash()" style="display:none">💵 Place Order - Cash on Delivery</button>
<div id="status" style="text-align:center;font-size:11px;font-weight:700;margin-top:10px;color:var(--muted)"></div>
</div></div></div>
<div id="riderModal" class="modal"><div class="sheet"><div class="s-h"><h3>Rider Center</h3><div onclick="closeM()" style="width:40px;height:40px;background:#0B0E14;border-radius:14px;display:flex;align-items:center;justify-content:center">✕</div></div><div class="s-c"><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px"><div style="background:#1A2035;padding:16px;border-radius:20px;text-align:center;border:1px solid var(--border)"><b>3</b><br><small>ONLINE</small></div><div style="background:#1A2035;padding:16px;border-radius:20px;text-align:center;border:1px solid var(--border)"><b id="rs2">0</b><br><small>ORDERS</small></div><div style="background:#1A2035;padding:16px;border-radius:20px;text-align:center;border:1px solid var(--border)"><b id="rs3">KES 0</b><br><small>SALES</small></div></div><div id="riderList" style="margin-top:16px"></div><div id="riderOrders" style="margin-top:12px"></div></div></div></div>
<div id="profileModal" class="modal"><div class="sheet"><div class="s-h"><h3>Profile</h3><div onclick="closeM()" style="width:40px;height:40px;background:#0B0E14;border-radius:14px;display:flex;align-items:center;justify-content:center">✕</div></div><div class="s-c"><div style="text-align:center;padding:8px 0 22px"><div style="width:88px;height:88px;background:#0A8EA8;border-radius:28px;display:flex;align-items:center;justify-content:center;font-size:40px;color:#fff;margin:0 auto">👤</div><h3 style="margin-top:14px" id="profileName">Welcome</h3><small style="color:var(--muted)" id="profilePhone">Login to order faster</small></div><div id="notLogged"><input id="waPhone" class="input" value="254" placeholder="WhatsApp 254712..."><button class="btn btn-wa" onclick="loginWA()">Login with WhatsApp</button></div><div id="logged" style="display:none"><div style="background:#DCFCE7;border-radius:18px;padding:14px;text-align:center;color:#14532D"><b>Logged in ✓</b><br><small id="loggedPhone">254...</small></div><button class="btn" style="background:#fff;color:#000;margin-top:12px" onclick="logout()">Logout</button></div></div></div></div>
<div class="toast" id="toast"></div>
<script>
var PRODUCTS = [
{id:1,name:"Ajab Maize Flour 2kg",price:175,old:195,store:"Naivas",cat:"grocery",rate:4.8,sold:234,img:"/img/flour",emoji:"🌽"},
{id:2,name:"Brookside Milk 500ml",price:65,old:75,store:"Naivas",cat:"dairy",rate:4.9,sold:512,img:"/img/milk",emoji:"🥛"},
{id:3,name:"Coca Cola 1.25L",price:100,old:120,store:"Quickmart",cat:"drinks",rate:4.7,sold:320,img:"/img/coke",emoji:"🥤"},
{id:4,name:"Omo Detergent 1kg",price:285,old:320,store:"Carrefour",cat:"home",rate:4.6,sold:89,img:"/img/omo",emoji:"🧴"},
{id:5,name:"Tomatoes Fresh 1kg",price:80,old:100,store:"Quickmart",cat:"fresh",rate:4.9,sold:445,img:"/img/tomato",emoji:"🍅"},
{id:6,name:"White Bread 400g",price:60,old:70,store:"Naivas",cat:"dairy",rate:4.8,sold:210,img:"/img/bread",emoji:"🍞"},
{id:7,name:"Pishori Rice 2kg",price:350,old:400,store:"Carrefour",cat:"grocery",rate:4.9,sold:156,img:"/img/rice",emoji:"🍚"},
{id:8,name:"Geisha Soap 150g",price:55,old:65,store:"Magunas",cat:"care",rate:4.5,sold:98,img:"/img/soap",emoji:"🧼"}
];
var STORES = ["ALL","Naivas","Quickmart","Carrefour","Chandarana","Magunas"];
var CATS = [
{id:"all",name:"All",icon:"🏬",img:null},
{id:"fresh",name:"Fresh",icon:"🥬",img:null},
{id:"grocery",name:"Grocery",icon:"🌽",img:"/grocery-icon"},
{id:"drinks",name:"Drinks",icon:"🥤",img:null},
{id:"dairy",name:"Dairy",icon:"🥛",img:null}
];
var cart=[]; var total=0; var activeStore="ALL"; var activeCat="all"; var payMethod="mpesa";

function orderNow(){ if(cart.length===0){ addToCart(1); addToCart(2); addToCart(5); showToast("3 best deals added! 🎉"); } setTimeout(function(){ openCart(); }, 400); }
function setPay(m){ payMethod=m; document.getElementById("payMpesa").classList.toggle("active",m==="mpesa"); document.getElementById("payCash").classList.toggle("active",m==="cash"); document.getElementById("placeBtn").style.display=m==="mpesa"?"block":"none"; document.getElementById("cashBtn").style.display=m==="cash"?"block":"none"; document.getElementById("mpesaStatus").classList.remove("show"); document.getElementById("cashStatus").classList.toggle("show",m==="cash"); document.getElementById("successStatus").classList.remove("show"); if(m==="cash") document.getElementById("cashAmount").innerText=total+100; }
function renderChips(){ var sHtml=""; for(var i=0;i<STORES.length;i++){ var s=STORES[i]; sHtml+='<div class="'+(s===activeStore?'chip active':'chip')+'" onclick="setStore(\\''+s+'\\')">'+s+'</div>'; } document.getElementById("storeChips").innerHTML=sHtml; var cHtml=""; for(var j=0;j<CATS.length;j++){ var c=CATS[j]; if(c.img){ cHtml+='<div class="cat '+(c.id===activeCat?'active':'')+'" onclick="setCat(\\''+c.id+'\\')"><div class="cat-icon"><img src="'+c.img+'" alt="grocery" onerror="this.style.display=\\'none\\'; this.parentNode.innerHTML=\\''+c.icon+'\\'"></div><b>'+c.name+'</b></div>'; } else { cHtml+='<div class="cat '+(c.id===activeCat?'active':'')+'" onclick="setCat(\\''+c.id+'\\')"><div class="cat-icon">'+c.icon+'</div><b>'+c.name+'</b></div>'; } } document.getElementById("catChips").innerHTML=cHtml; }
function renderProducts(list){
 var html=""; for(var i=0;i<list.length;i++){ var p=list[i]; var disc=Math.round((p.old-p.price)/p.old*100); html+='<div class="card"><div class="card-img"><img src="'+p.img+'" onerror="this.style.display=\\'none\\'; this.nextElementSibling.style.display=\\'block\\'" alt="'+p.name+'"><div class="emoji-fallback" style="display:none">'+p.emoji+'</div><div class="badge">-'+disc+'%</div><div class="heart">♡</div></div><div class="card-body"><div class="store">'+p.store+'</div><h4>'+p.name+'</h4><div class="meta">⭐ '+p.rate+' • '+p.sold+' sold</div><div class="price-row"><div class="price"><b>KES '+p.price+'</b><small>KES '+p.old+'</small></div><button class="add-btn" onclick="addToCart('+p.id+')">+</button></div></div></div>'; }
 document.getElementById("grid").innerHTML=html;
}
function renderFlash(){ var html=""; for(var i=0;i<4;i++){ var p=PRODUCTS[i]; html+='<div class="h-card"><div class="h-card-img"><img src="'+p.img+'" onerror="this.style.display=\\'none\\'; this.parentNode.innerHTML=\\''+p.emoji+'\\'" alt="'+p.name+'"></div><div style="font-size:11.5px;font-weight:700;height:32px;overflow:hidden">'+p.name+'</div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px"><b>KES '+p.price+'</b><button class="add-btn" style="width:30px;height:30px;font-size:16px" onclick="addToCart('+p.id+')">+</button></div></div>'; } document.getElementById("flash").innerHTML=html; }
function setStore(s){ activeStore=s; renderChips(); filterProducts(); }
function setCat(c){ activeCat=c; renderChips(); filterProducts(); }
function filterProducts(){ var filtered=[]; for(var i=0;i<PRODUCTS.length;i++){ var p=PRODUCTS[i]; if((activeStore==="ALL"||p.store===activeStore)&&(activeCat==="all"||p.cat===activeCat)) filtered.push(p); } renderProducts(filtered); }
function searchProd(){ var q=document.getElementById("search").value.toLowerCase(); if(!q){renderProducts(PRODUCTS);return;} var f=[]; for(var i=0;i<PRODUCTS.length;i++){ var p=PRODUCTS[i]; if(p.name.toLowerCase().indexOf(q)>-1) f.push(p); } renderProducts(f); }
function addToCart(id){ var p=null; for(var i=0;i<PRODUCTS.length;i++){ if(PRODUCTS[i].id===id) p=PRODUCTS[i]; } if(!p) return; cart.push(p); total+=p.price; document.getElementById("cartDot").innerText=cart.length; document.getElementById("cartC").innerText=cart.length; document.getElementById("payAmount").innerText=total+100; document.getElementById("cashAmount").innerText=total+100; showToast(p.name+" added ✓"); }
function openCart(){ var d=document.getElementById("cartItems"); if(cart.length===0){ d.innerHTML='<p style="text-align:center;padding:28px;color:var(--muted)">Cart empty - tap ORDER NOW</p>'; } else { var html=""; for(var i=0;i<cart.length;i++){ var c=cart[i]; html+='<div class="cart-i"><div class="ci"><img src="'+c.img+'" onerror="this.style.display=\\'none\\'; this.parentNode.innerHTML=\\''+c.emoji+'\\'"></div><div style="flex:1"><h4 style="font-size:13px;font-weight:700">'+c.name+'</h4><small style="color:var(--muted)">'+c.store+' • KES '+c.price+'</small></div><b>KES '+c.price+'</b></div>'; } d.innerHTML=html; } document.getElementById("sub").innerText=total; document.getElementById("grand").innerText=total+100; document.getElementById("payAmount").innerText=total+100; document.getElementById("cashAmount").innerText=total+100; document.getElementById("mpesaStatus").classList.remove("show"); document.getElementById("successStatus").classList.remove("show"); if(payMethod==="cash") document.getElementById("cashStatus").classList.add("show"); else document.getElementById("cashStatus").classList.remove("show"); document.getElementById("cartModal").classList.add("open"); }
function openRider(){ document.getElementById("riderModal").classList.add("open"); loadRiders(); }
function openProfile(){ document.getElementById("profileModal").classList.add("open"); }
function closeM(){ var modals=document.querySelectorAll(".modal"); for(var i=0;i<modals.length;i++) modals[i].classList.remove("open"); }
function toggleAI(){ document.getElementById("aiChat").classList.toggle("open"); }
function loginWA(){ var phone=document.getElementById("waPhone").value; if(phone.length<10){ alert("Enter valid number"); return; } localStorage.setItem("user",phone); document.getElementById("notLogged").style.display="none"; document.getElementById("logged").style.display="block"; document.getElementById("loggedPhone").innerText=phone; document.getElementById("profileName").innerText="Welcome! "+phone.slice(-4); document.getElementById("profilePhone").innerText=phone; document.getElementById("userStatus").innerText="Logged in • "+phone; document.getElementById("custPhone").value=phone; showToast("Logged in ✅"); fetch("/user/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone})}); }
function logout(){ localStorage.removeItem("user"); document.getElementById("notLogged").style.display="block"; document.getElementById("logged").style.display="none"; document.getElementById("profileName").innerText="Welcome"; document.getElementById("profilePhone").innerText="Login to order faster"; showToast("Logged out"); }
async function sendAI(){ var input=document.getElementById("aiInput"); var msg=input.value.trim(); if(!msg) return; var box=document.getElementById("aiMsgs"); box.innerHTML+='<div class="m u">'+msg+'</div>'; input.value=""; box.scrollTop=box.scrollHeight; try{ var r=await fetch("/ai/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg,cart_count:cart.length})}); var d=await r.json(); box.innerHTML+='<div class="m b">'+d.reply+'</div>'; } catch(e){ box.innerHTML+='<div class="m b">Error, try again</div>'; } box.scrollTop=box.scrollHeight; }
async function checkout(){
 var phone=document.getElementById("custPhone").value; var loc=document.getElementById("custLoc").value; var name=document.getElementById("custName").value;
 if(!name){ alert("Enter your name"); return; }
 if(!phone || phone.length<10){ alert("Enter valid M-Pesa 2547..."); return; }
 if(!loc){ alert("Enter location"); return; }
 document.getElementById("status").innerText=""; document.getElementById("mpesaPhoneDisplay").innerText=phone; document.getElementById("mpesaStatus").classList.add("show"); document.getElementById("cashStatus").classList.remove("show"); document.getElementById("successStatus").classList.remove("show"); document.getElementById("placeBtn").innerText="⏳ Sending STK Push..."; document.getElementById("placeBtn").disabled=true; showToast("M-Pesa prompt sent to "+phone+" 📱");
 try{ var r=await fetch("/mpesa/stkpush",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone,amount:total+100,location:loc,cart:cart,name:name})}); var d=await r.json(); setTimeout(function(){ document.getElementById("mpesaStatus").classList.remove("show"); document.getElementById("orderId").innerText=d.order_id; document.getElementById("riderInfo").innerText="Rider John KMEZ 123A • 4.9★ • 30min • "+loc; document.getElementById("paymentNote").innerText="M-Pesa: KES "+(total+100)+" - Enter PIN on phone"; document.getElementById("successStatus").classList.add("show"); document.getElementById("placeBtn").innerText="✅ Order Placed!"; document.getElementById("placeBtn").disabled=false; document.getElementById("status").innerText="STK Push sent! Check phone"; showToast("Order "+d.order_id+" confirmed! 🎉"); cart=[]; total=0; document.getElementById("cartDot").innerText=0; }, 2000); } catch(e){ document.getElementById("mpesaStatus").classList.remove("show"); document.getElementById("status").innerText="Error, but order saved"; var oid="ORD"+Math.floor(1000+Math.random()*9000); document.getElementById("orderId").innerText=oid; document.getElementById("successStatus").classList.add("show"); }
}
async function checkoutCash(){
 var phone=document.getElementById("custPhone").value; var loc=document.getElementById("custLoc").value; var name=document.getElementById("custName").value;
 if(!name){ alert("Enter name"); return; } if(!loc){ alert("Enter location"); return; }
 document.getElementById("cashBtn").innerText="⏳ Placing order...";
 try{ var r=await fetch("/mpesa/stkpush",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone,amount:total+100,location:loc,cart:cart,name:name,payment:"cash"})}); var d=await r.json(); document.getElementById("orderId").innerText=d.order_id; document.getElementById("riderInfo").innerText="Rider John • 4.9★ • 30min • "+loc; document.getElementById("paymentNote").innerText="Cash on Delivery: Pay KES "+(total+100)+" to rider"; document.getElementById("cashStatus").classList.remove("show"); document.getElementById("successStatus").classList.add("show"); document.getElementById("cashBtn").innerText="✅ Order Placed - Pay Cash"; showToast("Order "+d.order_id+" confirmed! 💵"); cart=[]; total=0; document.getElementById("cartDot").innerText=0; } catch(e){ var oid="ORD"+Math.floor(1000+Math.random()*9000); document.getElementById("orderId").innerText=oid; document.getElementById("successStatus").classList.add("show"); }
}
async function loadRiders(){ var r=await fetch("/riders"); var riders=await r.json(); var html=""; for(var i=0;i<riders.length;i++){ var rd=riders[i]; html+='<div style="background:#1A2035;border:1px solid var(--border);border-radius:20px;padding:14px;display:flex;justify-content:space-between;align-items:center;margin-bottom:10px"><div><b>'+rd.name+' ⭐'+rd.rating+'</b><br><small style="color:var(--muted)">'+rd.motor+' • '+rd.location+'</small></div><div style="padding:7px 12px;border-radius:100px;background:'+(rd.status==="available"?"#DCFCE7":"#FEF3C7")+';color:#000;font-size:10px;font-weight:800">'+rd.status.toUpperCase()+'</div></div>'; } document.getElementById("riderList").innerHTML=html; var ro=await fetch("/orders"); var orders=await ro.json(); document.getElementById("rs2").innerText=orders.length; document.getElementById("rs3").innerText="KES "+orders.reduce(function(s,o){return s+o.amount},0); var oh='<h4 style="margin:14px 0 10px;font-size:13px;font-weight:800">Active Orders</h4>'; for(var j=0;j<Math.min(orders.length,5);j++){ var o=orders[j]; oh+='<div style="background:#1A2035;border:1px solid var(--border);border-radius:18px;padding:12px;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><div><b>'+o.id+'</b> KES '+o.amount+'<br><small style="color:var(--muted)">'+o.location+'</small></div><button onclick="acceptOrder(\\''+o.id+'\\')" style="padding:9px 14px;background:#fff;color:#000;border:none;border-radius:100px;font-size:11px;font-weight:800">Accept</button></div>'; } document.getElementById("riderOrders").innerHTML=oh; }
async function loadAdmin(){ var r=await fetch("/orders"); var o=await r.json(); document.getElementById("adminStats").innerHTML='<div style="background:#1A2035;border:1px solid var(--border);padding:18px;border-radius:20px;text-align:center"><b style="font-size:24px">'+o.length+'</b><br><small style="color:var(--muted);font-size:10px">ORDERS</small></div><div style="background:#1A2035;border:1px solid var(--border);padding:18px;border-radius:20px;text-align:center"><b style="font-size:20px">KES '+o.reduce(function(s,x){return s+x.amount},0)+'</b><br><small style="color:var(--muted);font-size:10px">REVENUE</small></div>'; var html=""; for(var i=0;i<Math.min(o.length,8);i++){ var x=o[i]; html+='<div style="background:#1A2035;border:1px solid var(--border);border-radius:18px;padding:12px;margin-bottom:8px"><b>'+x.id+'</b> - '+x.status+'<br><small style="color:var(--muted)">'+x.location+' • KES '+x.amount+'</small></div>'; } document.getElementById("adminOrders").innerHTML=html; }
async function acceptOrder(id){ await fetch("/rider/accept/"+id,{method:"POST"}); showToast("Accepted "+id+" ✓"); loadRiders(); }
function showToast(t){ var el=document.getElementById("toast"); el.innerText=t; el.style.display="block"; setTimeout(function(){el.style.display="none"},3000); }
renderChips(); renderProducts(PRODUCTS); renderFlash();
var timeLeft=2*3600+14*60+33; setInterval(function(){ timeLeft--; var h=Math.floor(timeLeft/3600); var m=Math.floor((timeLeft%3600)/60); var s=timeLeft%60; var el=document.getElementById("timer"); if(el) el.innerText="Ends "+(h<10?"0"+h:h)+":"+(m<10?"0"+m:m)+":"+(s<10?"0"+s:s); },1000);
</script></body></html>
''')

@app.post("/ai/chat")
async def chat(req: Request):
    try:
        b=await req.json()
        return {"reply": smart_ai_reply(b.get("message",""), b.get("cart_count",0))}
    except: return {"reply": "Try: Help me"}

@app.post("/user/login")
async def login_user(req: Request): return {"success":True}

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    try:
        b=await req.json()
        oid=f"ORD{random.randint(1000,9999)}"
        ORDERS.append({"id":oid,"phone":b.get("phone"),"name":b.get("name",""),"amount":b.get("amount",1),"location":b.get("location","Kajiado"),"cart":b.get("cart",[]),"payment":b.get("payment","mpesa"),"status":"paid","time":datetime.now().isoformat()})
        token=get_token()
        if not token or b.get("payment")=="cash": return {"ResponseCode":"0","order_id":oid,"message":"Order placed"}
        ts=datetime.now().strftime("%Y%m%d%H%M%S")
        pwd=base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{ts}".encode()).decode()
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

@app.get("/grocery-icon")
async def grocery_icon():
    for p in ["grocery.jpg","/mnt/data/fresh_produce_icon.webp","/mnt/data/wa_image_7995968891402268899","/mnt/data/wa_image_4216889998897024897"]:
        if os.path.exists(p): return FileResponse(p)
    return HTMLResponse("", status_code=404)

@app.get("/img/{name}")
async def product_img(name: str):
    mapping={
        "flour":"/mnt/data/ajab_maize_flour_bag.webp",
        "milk":"/mnt/data/brookside_milk_carton.webp",
        "coke":"/mnt/data/coca_cola_bottle_studio.webp",
        "omo":"/mnt/data/omo_detergent_box.webp",
        "tomato":"/mnt/data/fresh_tomatoes_wooden_bowl.webp",
        "bread":"/mnt/data/sliced_white_bread_packaging.webp",
        "rice":"/mnt/data/fresh_produce_icon.webp",
        "soap":"/mnt/data/omo_detergent_box.webp"
    }
    path=mapping.get(name)
    if path and os.path.exists(path): return FileResponse(path)
    for alt in [f"{name}.jpg", f"{name}.webp", f"{name}.png"]:
        if os.path.exists(alt): return FileResponse(alt)
    return HTMLResponse("", status_code=404)

@app.get("/favicon.ico")
async def fav():
    if os.path.exists("logo.png"): return FileResponse("logo.png")
    return HTMLResponse("", status_code=404)
