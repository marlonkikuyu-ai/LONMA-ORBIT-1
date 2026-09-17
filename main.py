from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, FileResponse
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
RIDERS=[{"id":1,"name":"John Mwangi","motor":"KMEZ 123A","status":"available","rating":4.9,"location":"Kajiado","trips":12}]

REVIEWS=[
 {"name":"Wanjiku A.","location":"Kajiado","stars":5,"text":"Unga ilifika in 25min! Bei poa kuliko Naivas.","product":"Jogoo Unga","date":"2 days ago"},
 {"name":"Otieno K.","location":"Kitengela","stars":5,"text":"M-Pesa STK ilikuja instantly. Fresh kabisa.","product":"Fresh Fri Oil","date":"5 days ago"},
 {"name":"Amina N.","location":"Rongai","stars":4,"text":"Maziwa na mkate zilifika moto. Rider polite.","product":"Brookside Milk","date":"1 week ago"},
]

def smart_ai_reply(msg):
    m=msg.lower()
    if any(x in m for x in ["where are you","location","wapi","hq"]):
        return {"reply":"📍 Kajiado Town HQ! 4.9⭐ by 2,340+ Kenyans.","action":None}
    if "unga" in m: return {"reply":"✅ Jogoo Unga 2kg - KES 175 ⭐4.8","action":"add_to_cart","product_id":1,"product_name":"Jogoo Unga"}
    if "sukari" in m or "sugar" in m: return {"reply":"✅ Mumias Sugar 2kg - KES 310 ⭐4.9","action":"add_to_cart","product_id":2,"product_name":"Mumias Sugar"}
    if "mafuta" in m or "oil" in m: return {"reply":"✅ Fresh Fri Oil 2L - KES 450 ⭐4.8","action":"add_to_cart","product_id":3,"product_name":"Fresh Fri Oil"}
    if "mchele" in m or "rice" in m: return {"reply":"✅ Pishori Rice 2kg - KES 350 ⭐4.9","action":"add_to_cart","product_id":4,"product_name":"Pishori Rice"}
    if "maziwa" in m or "milk" in m: return {"reply":"✅ Brookside Milk 500ml - KES 65 ⭐4.9","action":"add_to_cart","product_id":5,"product_name":"Brookside Milk"}
    if "mkate" in m or "bread" in m: return {"reply":"✅ White Bread 400g - KES 60 ⭐4.8","action":"add_to_cart","product_id":6,"product_name":"White Bread"}
    if "review" in m or "rate" in m: return {"reply":"⭐ 4.9/5 from 2,340+ Kenyans! Wanjiku: ⭐⭐⭐⭐⭐ 'Unga 25min!'","action":None}
    if any(x in m for x in ["hello","hi","jambo"]): return {"reply":"Jambo! Karibu LONMA ORBIT! 🇰🇪 Nipe unga?","action":None}
    return {"reply":"Try: unga, sukari, mafuta, or show reviews","action":None}

def make_product_svg(name, brand_color, emoji):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300"><rect width="300" height="300" fill="#FFFFFF" rx="20"/><rect x="30" y="30" width="240" height="160" fill="{brand_color}" rx="12"/><text x="150" y="100" font-size="56" text-anchor="middle" fill="white">{emoji}</text><text x="150" y="145" font-size="18" font-weight="900" text-anchor="middle" fill="white" font-family="Arial">{name.split(' ')[0]}</text><rect x="20" y="210" width="260" height="70" fill="#F8FAFC" rx="12"/><text x="150" y="245" font-size="12" font-weight="800" text-anchor="middle" fill="#0B0E14" font-family="Arial">{name[:22]}</text></svg>'''
    return svg.encode()

# LOGO ROUTES - serves your uploaded logo.png
@app.get("/logo.png")
async def logo_png():
    for p in ["logo.png","./logo.png","/mnt/data/logo.png"]:
        if os.path.exists(p):
            return FileResponse(p, media_type="image/png")
    # fallback to your uploaded file in this session
    if os.path.exists("/mnt/data/wa_image_1298718935028212791"):
        return FileResponse("/mnt/data/wa_image_1298718935028212791", media_type="image/jpeg")
    return Response(status_code=404)

@app.get("/favicon.ico")
async def favicon():
    for p in ["logo.png","./logo.png"]:
        if os.path.exists(p):
            return FileResponse(p, media_type="image/png")
    if os.path.exists("/mnt/data/wa_image_1298718935028212791"):
        return FileResponse("/mnt/data/wa_image_1298718935028212791", media_type="image/jpeg")
    return Response(content=make_product_svg("LONMA","#0A8EA8","🛒"), media_type="image/svg+xml")

@app.get("/terms", response_class=HTMLResponse)
async def terms_page():
    return HTMLResponse("""<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#0A8EA8;color:#fff;padding:20px;font-family:Arial;max-width:600px;margin:0 auto;text-align:center}.card{background:#fff;color:#0B0E14;border-radius:18px;padding:18px;margin:12px 0}</style></head><body>
<img src="/logo.png" style="width:120px;border-radius:16px;margin:20px auto;display:block"><h1>LONMA ORBIT</h1><div class="card">⭐4.9 by 2,340+ Kenyans. Supermarket delivery Kajiado HQ.</div><a href="/" style="color:#fff">← Back</a></body></html>""")

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT - For Kenyans</title><link rel="icon" href="/logo.png">
<style>
:root{--bg:#0B0E14;--card:#151A27;--text:#F8FAFC;--muted:#94A3B8;--border:#1E293B;--teal:#0A8EA8}
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,Arial} body{background:var(--bg);color:var(--text);padding-bottom:110px}
.header{position:sticky;top:0;z-index:40;background:#0A8EA8;border-bottom:1px solid rgba(0,0,0,0.1)}
.h-top{display:flex;justify-content:space-between;align-items:center;padding:10px 16px}
.logo-img{height:52px;border-radius:12px;background:#fff;padding:2px}
.rating-badge{background:#fff;color:#0A8EA8;padding:8px 12px;border-radius:100px;font-size:11px;font-weight:800}
.h-loc{padding:8px 16px 12px;display:flex;align-items:center;gap:10px;background:#0A8EA8;color:#fff}
.trust{display:flex;gap:8px;padding:10px 16px;overflow-x:auto;background:#0B0E14}.trust::-webkit-scrollbar{display:none}
.trust-item{white-space:nowrap;background:#151A27;border:1px solid var(--border);padding:8px 12px;border-radius:100px;font-size:11px;font-weight:700;flex-shrink:0}
.search-wrap{padding:0 16px 16px;background:#0B0E14}.search-box{background:#151A27;border:1px solid var(--border);border-radius:18px;display:flex;align-items:center;gap:12px;padding:14px 18px}
.search-box input{border:none;outline:none;background:transparent;flex:1;font-size:14px;color:var(--text)}
.hero{margin:0 16px 14px;background:#0A8EA8;border-radius:24px;padding:18px;display:flex;justify-content:space-between;align-items:center;color:#fff;cursor:pointer}
.hero h2{font-size:19px;font-weight:900}.hero-btn{background:#fff;color:#0A8EA8;padding:12px 20px;border-radius:100px;font-weight:900;font-size:12px}
.chips{display:flex;gap:10px;overflow-x:auto;padding:0 16px 14px}.chips::-webkit-scrollbar{display:none}
.chip{white-space:nowrap;padding:11px 18px;border-radius:100px;background:#151A27;border:1px solid var(--border);font-size:13px;color:var(--muted);flex-shrink:0}.chip.active{background:#fff;color:#000}
.cats{display:flex;gap:12px;overflow-x:auto;padding:4px 16px 18px}.cats::-webkit-scrollbar{display:none}
.cat{min-width:68px;text-align:center;flex-shrink:0}.cat-icon{width:64px;height:64px;background:#151A27;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:28px;border:1px solid var(--border);margin:0 auto}
.section{padding:6px 16px 18px}.sec-head{display:flex;justify-content:space-between;margin-bottom:14px}.sec-head h3{font-size:17px;font-weight:800}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.card{background:var(--card);border-radius:20px;overflow:hidden;border:1px solid var(--border)}
.card-img{height:150px;background:#fff;position:relative}.card-img img{width:100%;height:100%;object-fit:cover}
.badge{position:absolute;top:10px;left:10px;background:#EF4444;color:#fff;font-size:10px;font-weight:900;padding:5px 9px;border-radius:100px}
.card-body{padding:11px 12px}.store{font-size:9px;font-weight:800;color:var(--teal);text-transform:uppercase}.card-body h4{font-size:12.5px;margin:3px 0;height:32px;overflow:hidden}.stars{color:#FBBF24;font-size:11px;margin:4px 0}.price-row{display:flex;justify-content:space-between;margin-top:8px}.price b{font-size:14px}.price small{font-size:10px;color:var(--muted);text-decoration:line-through}.add-btn{width:34px;height:34px;background:#0B0E14;color:#fff;border:1px solid var(--border);border-radius:10px;font-size:18px}
.rev-scroll{display:flex;gap:12px;overflow-x:auto}.rev-scroll::-webkit-scrollbar{display:none}
.rev-card{min-width:260px;background:#151A27;border:1px solid var(--border);border-radius:20px;padding:16px;flex-shrink:0}
.rate-box{background:#0A8EA8;border-radius:20px;padding:18px;margin:0 16px 18px;color:#fff;text-align:center}
.bottom{position:fixed;bottom:0;left:0;right:0;background:rgba(21,26,39,0.98);border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:8px 0 10px;z-index:50}
.tab{flex:1;text-align:center;cursor:pointer}.tab-i{font-size:20px}.tab b{font-size:9px;display:block}.tab.active{color:#fff}
.cart-dot{position:absolute;top:0px;right:16px;background:#EF4444;color:#fff;font-size:10px;min-width:18px;height:18px;border-radius:100px;display:flex;align-items:center;justify-content:center}
#ai{position:fixed;bottom:90px;left:16px;width:56px;height:56px;background:#fff;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:26px;z-index:45;box-shadow:0 8px 24px rgba(0,0,0,0.3)}
#aiChat{display:none;position:fixed;bottom:20px;left:12px;right:12px;max-width:420px;margin:0 auto;height:70vh;background:#151A27;border-radius:24px;z-index:60;flex-direction:column;overflow:hidden;border:1px solid var(--border)} #aiChat.open{display:flex}
.ai-h{background:#0A8EA8;color:#fff;padding:12px 16px;display:flex;justify-content:space-between;align-items:center}
.ai-h img{height:36px;border-radius:8px;background:#fff;padding:2px}
.ai-msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:#0B0E14}
.m{max-width:86%;padding:12px 14px;border-radius:18px;font-size:13px;white-space:pre-line}.m.u{align-self:flex-end;background:#fff;color:#0B0E14}.m.b{align-self:flex-start;background:#1A2035;border:1px solid var(--border)}
.ai-in{display:flex;gap:8px;padding:12px;border-top:1px solid var(--border)}.ai-in input{flex:1;padding:12px 16px;border-radius:100px;border:1px solid var(--border);background:#0B0E14;color:#fff;outline:none}.ai-in button{padding:12px 18px;background:#0A8EA8;color:#fff;border:none;border-radius:100px}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);justify-content:center;align-items:flex-end;z-index:80}.modal.open{display:flex}
.sheet{background:#151A27;width:100%;max-width:520px;margin:0 auto;border-radius:28px 28px 0 0;max-height:92vh;overflow-y:auto}
.s-h{padding:18px 20px;display:flex;justify-content:space-between;border-bottom:1px solid var(--border)}
.s-c{padding:18px}.btn{width:100%;padding:15px;border:none;border-radius:16px;font-weight:800;margin-top:10px}.btn-mpesa{background:#0A8EA8;color:#fff}.btn-wa{background:#22C55E;color:#fff}
.input{width:100%;padding:13px;border-radius:14px;border:1px solid var(--border);margin:6px 0;background:#0B0E14;color:#fff}
.toast{position:fixed;bottom:100px;left:50%;transform:translateX(-50%);background:#fff;color:#000;padding:10px 18px;border-radius:100px;display:none;z-index:100}
</style></head><body>
<div class="header"><div class="h-top"><img src="/logo.png" class="logo-img" alt="LONMA ORBIT"><div class="rating-badge">⭐ 4.9 • 2.3k</div></div><div class="h-loc"><div><b style="font-size:13px">Serving Kenyans • 30min delivery</b><br><small style="font-size:11px;opacity:0.9">Kajiado HQ • Trusted by Wakenya</small></div></div></div>
<div class="trust"><div class="trust-item">⭐ 4.9 Rated</div><div class="trust-item">💚 M-Pesa</div><div class="trust-item">⚡ 30min</div><div class="trust-item">✓ 2,340+ Happy</div></div>
<div class="search-wrap"><div class="search-box">🔍<input id="search" placeholder="Search unga, sukari..." oninput="searchProd()"></div></div>
<div class="hero" onclick="orderNow()"><div><h2>Supermarket Items<br>for Kenyans! 🇰🇪</h2><p>⭐4.9 Rated • KARIBU30</p></div><div class="hero-btn">ORDER NOW</div></div>
<div class="chips" id="storeChips"></div><div class="cats" id="catChips"></div>
<div class="section"><div class="sec-head"><h3>Bei Poa Today ⭐</h3><span>See All</span></div><div class="grid" id="grid"></div></div>
<div class="rate-box"><b>⭐ 4.9/5 - Wakenya Wanapenda!</b><p style="font-size:11px;margin-top:6px">2,340+ verified deliveries</p><div style="font-size:20px;margin-top:8px">⭐⭐⭐⭐⭐</div></div>
<div class="section"><div class="sec-head"><h3>Wakenya Wanasema 💬</h3></div><div class="rev-scroll" id="revScroll"></div></div>
<div style="padding:20px 16px 110px;text-align:center"><img src="/logo.png" style="height:60px;border-radius:12px;margin-bottom:10px"><p style="font-size:10px;color:#475569">© 2026 LONMA ORBIT • <a href="/terms" style="color:#94A3B8">Terms</a></p></div>
<div class="bottom"><div class="tab active" style="position:relative"><div class="tab-i">🏠</div><b>Home</b></div><div class="tab"><div class="tab-i">🛍️</div><b>Shop</b></div><div class="tab" onclick="openCart()" style="position:relative"><div class="tab-i">🛒</div><b>Cart</b><div class="cart-dot" id="cartDot">0</div></div><div class="tab" onclick="openRider()"><div class="tab-i">🏍️</div><b>Rider</b></div><div class="tab" onclick="openProfile()"><div class="tab-i">👤</div><b>You</b></div></div>
<div id="ai" onclick="toggleAI()">💬</div>
<div id="aiChat"><div class="ai-h"><img src="/logo.png"><div onclick="toggleAI()" style="width:32px;height:32px;background:rgba(255,255,255,0.2);border-radius:10px;display:flex;align-items:center;justify-content:center">✕</div></div><div class="ai-msgs" id="aiMsgs"><div class="m b">Jambo! Karibu LONMA ORBIT! ⭐4.9<br>Try: Nipe unga</div></div><div class="ai-in"><input id="aiInput" placeholder="Ask..." onkeypress="if(event.key==='Enter') sendAI()"><button onclick="sendAI()">Send</button></div></div>
<div id="cartModal" class="modal"><div class="sheet"><div class="s-h"><h3>Cart (<span id="cartC">0</span>)</h3><div onclick="closeM()">✕</div></div><div class="s-c"><div id="cartItems"></div><div style="display:flex;justify-content:space-between;margin-top:12px"><span>Total</span><b>KES <span id="grand">0</span></b></div><input id="custName" class="input" placeholder="Jina"><input id="custPhone" class="input" value="254"><input id="custLoc" class="input" placeholder="Location"><button class="btn btn-mpesa" onclick="checkout()">💚 Lipa na M-Pesa</button></div></div></div>
<div id="riderModal" class="modal"><div class="sheet"><div class="s-h"><h3>Riders</h3><div onclick="closeM()">✕</div></div><div class="s-c"><div id="riderList"></div></div></div></div>
<div id="profileModal" class="modal"><div class="sheet"><div class="s-h"><h3>You</h3><div onclick="closeM()">✕</div></div><div class="s-c"><input id="waPhone" class="input" value="254"><button class="btn btn-wa" onclick="loginWA()">Login</button></div></div></div>
<div class="toast" id="toast"></div>
<script>
var PRODUCTS=[{"id":1,"name":"Jogoo Maize Flour 2kg - Unga","price":175,"old":195,"store":"Naivas","cat":"supermarket","rate":4.8,"sold":834,"img":"/img/flour"},{"id":2,"name":"Mumias Sugar 2kg - Sukari","price":310,"old":340,"store":"Naivas","cat":"supermarket","rate":4.9,"sold":612,"img":"/img/sugar"},{"id":3,"name":"Fresh Fri Oil 2L - Mafuta","price":450,"old":520,"store":"Quickmart","cat":"supermarket","rate":4.8,"sold":420,"img":"/img/oil"},{"id":4,"name":"Pishori Rice 2kg - Mchele","price":350,"old":400,"store":"Carrefour","cat":"supermarket","rate":4.9,"sold":556,"img":"/img/rice"},{"id":5,"name":"Brookside Milk 500ml - Maziwa","price":65,"old":75,"store":"Naivas","cat":"dairy","rate":4.9,"sold":512,"img":"/img/milk"},{"id":6,"name":"White Bread 400g - Mkate","price":60,"old":70,"store":"Naivas","cat":"dairy","rate":4.8,"sold":410,"img":"/img/bread"}];
var REVIEWS=[{"name":"Wanjiku A.","location":"Kajiado","stars":5,"text":"Unga ilifika in 25min! Bei poa!","product":"Jogoo Unga","date":"2 days ago"},{"name":"Otieno K.","location":"Kitengela","stars":5,"text":"M-Pesa instant. Fresh kabisa.","product":"Fresh Fri Oil","date":"5 days ago"},{"name":"Amina N.","location":"Rongai","stars":4,"text":"Rider polite sana.","product":"Milk","date":"1 week ago"}];
var STORES=["ALL","Naivas","Quickmart","Carrefour"];var CATS=[{id:"all",name:"All",icon:"🇰🇪"},{id:"supermarket",name:"Supermarket",icon:"🛒"},{id:"dairy",name:"Maziwa",icon:"🥛"}];
var cart=[];var total=0;var activeStore="ALL";var activeCat="all";
function renderReviews(){var h="";for(var i=0;i<REVIEWS.length;i++){var r=REVIEWS[i];h+='<div class="rev-card"><div style="color:#FBBF24">⭐'.repeat(r.stars)+'</div><div style="font-size:12px;margin:8px 0">"'+r.text+'"</div><b style="font-size:12px">'+r.name+'</b><small style="color:var(--muted)"> '+r.location+'</small></div>';}document.getElementById("revScroll").innerHTML=h;}
function renderChips(){var s="";for(var i=0;i<STORES.length;i++)s+='<div class="'+(STORES[i]===activeStore?'chip active':'chip')+'" onclick="setStore(\\''+STORES[i]+'\\')">'+STORES[i]+'</div>';document.getElementById("storeChips").innerHTML=s;var c="";for(var j=0;j<CATS.length;j++)c+='<div class="cat" onclick="setCat(\\''+CATS[j].id+'\\')"><div class="cat-icon">'+CATS[j].icon+'</div><b>'+CATS[j].name+'</b></div>';document.getElementById("catChips").innerHTML=c;}
function renderProducts(list){var h="";for(var i=0;i<list.length;i++){var p=list[i];var d=Math.round((p.old-p.price)/p.old*100);h+='<div class="card"><div class="card-img"><img src="'+p.img+'"><div class="badge">-'+d+'%</div></div><div class="card-body"><div class="store">'+p.store+'</div><h4>'+p.name+'</h4><div class="stars">⭐ '+p.rate+' ('+p.sold+')</div><div class="price-row"><div class="price"><b>KES '+p.price+'</b><small>KES '+p.old+'</small></div><button class="add-btn" onclick="addToCart('+p.id+')">+</button></div></div></div>';}document.getElementById("grid").innerHTML=h;}
function setStore(s){activeStore=s;renderChips();filterProducts();}function setCat(c){activeCat=c;renderChips();filterProducts();}
function filterProducts(){var f=[];for(var i=0;i<PRODUCTS.length;i++){var p=PRODUCTS[i];if((activeStore==="ALL"||p.store===activeStore)&&(activeCat==="all"||p.cat===activeCat))f.push(p);}renderProducts(f);}
function searchProd(){var q=document.getElementById("search").value.toLowerCase();if(!q){renderProducts(PRODUCTS);return;}var f=[];for(var i=0;i<PRODUCTS.length;i++)if(PRODUCTS[i].name.toLowerCase().indexOf(q)>-1)f.push(PRODUCTS[i]);renderProducts(f);}
function addToCart(id){for(var i=0;i<PRODUCTS.length;i++)if(PRODUCTS[i].id===id){cart.push(PRODUCTS[i]);total+=PRODUCTS[i].price;}document.getElementById("cartDot").innerText=cart.length;document.getElementById("cartC").innerText=cart.length;showToast("Added ✓");}
function orderNow(){if(cart.length===0){addToCart(1);addToCart(2);}setTimeout(function(){openCart()},400);}
function openCart(){var h="";for(var i=0;i<cart.length;i++)h+='<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1E293B"><span style="font-size:12px">'+cart[i].name+'</span><b>KES '+cart[i].price+'</b></div>';document.getElementById("cartItems").innerHTML=h||"Empty";document.getElementById("grand").innerText=total+100;document.getElementById("cartModal").classList.add("open");}
function openRider(){document.getElementById("riderModal").classList.add("open");}
function openProfile(){document.getElementById("profileModal").classList.add("open");}
function closeM(){var m=document.querySelectorAll(".modal");for(var i=0;i<m.length;i++)m[i].classList.remove("open");}
function toggleAI(){document.getElementById("aiChat").classList.toggle("open");}
function loginWA(){showToast("Karibu! 🇰🇪");closeM();}
async function sendAI(){var inp=document.getElementById("aiInput");var msg=inp.value.trim();if(!msg)return;var box=document.getElementById("aiMsgs");box.innerHTML+='<div class="m u">'+msg+'</div>';inp.value="";var r=await fetch("/ai/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg})});var d=await r.json();box.innerHTML+='<div class="m b">'+d.reply+'</div>';if(d.action==="add_to_cart")setTimeout(function(){addToCart(d.product_id)},500);box.scrollTop=box.scrollHeight;}
async function checkout(){var phone=document.getElementById("custPhone").value;var r=await fetch("/mpesa/stkpush",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone,amount:total+100})});var d=await r.json();showToast("Order "+d.order_id+" placed!");cart=[];total=0;closeM();}
function showToast(t){var e=document.getElementById("toast");e.innerText=t;e.style.display="block";setTimeout(function(){e.style.display="none"},2500);}
renderChips();renderProducts(PRODUCTS);renderReviews();
</script></body></html>""")

@app.post("/ai/chat")
async def chat(req: Request):
    b=await req.json(); return smart_ai_reply(b.get("message",""))
@app.post("/mpesa/stkpush")
async def stk(req: Request):
    b=await req.json(); oid=f"ORD{random.randint(1000,9999)}"; ORDERS.append({"id":oid}); return {"order_id":oid}
@app.get("/riders")
async def riders(): return RIDERS
@app.get("/img/{name}")
async def product_img(name: str):
    maps={"flour":("JOGOO UNGA","#F59E0B","🌽"),"sugar":("MUMIAS","#EF4444","🍚"),"oil":("FRESH FRI","#10B981","🫒"),"rice":("PISHORI","#8B5CF6","🍚"),"milk":("BROOKSIDE","#0EA5E9","🥛"),"bread":("MKATE","#F97316","🍞")}
    n,c,e = maps.get(name, (name.upper(),"#0A8EA8","🛒"))
    return Response(content=make_product_svg(n,c,e), media_type="image/svg+xml")
