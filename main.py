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
        return "Hello! 👋 I'm LONMA AI!\n\nI know prices from 5 stores: Naivas, Quickmart, Carrefour, Chandarana & Magunas.\n\nWhat do you need today?"
    if any(w in msg for w in ["help","assist","guide"]):
        return "I can help:\n\n🛒 Find cheapest products\n💰 Compare prices\n🏍️ Delivery info\n📦 How to order\n💳 M-Pesa payment\n\nTry: 'Will you deliver?' or 'Cheapest flour'"
    if any(w in msg for w in ["deliver","delivery","bring"]):
        if "where" in msg or "area" in msg:
            return "We deliver to:\n📍 Kajiado Town\n📍 Kitengela\n📍 Rongai\n📍 Kiserian\n\n30 mins, KES 100 fee, 3 riders online!"
        return "Yes! We deliver in 30 mins 🏍️\n\nAreas: Kajiado, Kitengela, Rongai\nFee: KES 100\n3 riders online\n\nWhere to deliver?"
    if "yes" in msg and ("bring" in msg or "on" in msg):
        return "Great! 🛒\n1. Tap + on products\n2. Click Cart bottom\n3. Enter location + M-Pesa\n4. Place Order\n\nRider in 30 mins! What do you want?"
    if "flour" in msg or "unga" in msg:
        return "Ajab Flour 2kg:\n💰 KES 175 Naivas\n💰 KES 172 Carrefour (best!)\n📦 50 packs, ⭐4.8\nTap + to add!"
    if "milk" in msg or "maziwa" in msg:
        return "Brookside Milk 500ml:\n💰 KES 65 Naivas\n💰 KES 62 Chandarana\n📦 100 fresh today, ⭐4.9"
    if "rider" in msg or "how long" in msg:
        return "🏍️ 30 mins delivery, KES 100\n3 riders:\n• John 4.9★ Available\n• Peter 4.8★ Delivering\n• Samuel 5.0★ Available"
    if "cart" in msg or "order" in msg:
        return f"You have {cart_count} items.\nTap + to add, then Cart icon > Place Order. Rider in 30 secs!"
    if "cheapest" in msg:
        return "Cheapest today:\n🌽 Flour 2kg KES 175\n🥛 Milk 500ml KES 65\n🍅 Tomatoes 1kg KES 80\n🍞 Bread KES 60\n10-20% OFF!"
    found=[]
    for p in PRODUCTS:
        if any(word in msg for word in p["name"].lower().split() if len(word)>2):
            found.append(p)
    if found:
        p=found[0]
        return f"{p['name']} {p['emoji']}\n💰 KES {p['price']} at {p['store']} (was {p['old']})\n📦 {p['stock']} in stock ⭐{p['rate']}"
    return f"I got: '{message}'\n\nTry:\n• 'Help me'\n• 'Will you deliver?'\n• 'Cheapest flour'\n• 'Milk price'"

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse('''
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><title>LONMA ORBIT • Fresh Groceries in 30 mins</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
<style>
:root{--bg:#F8FAFB;--card:#FFFFFF;--text:#0F172A;--muted:#64748B;--border:#F1F5F9;--teal:#0A8EA8;--teal2:#06B6D4;--shadow:0 10px 30px rgba(0,0,0,0.06);--shadow2:0 20px 40px rgba(0,0,0,0.08)}
.dark{--bg:#0B0E14;--card:#151A27;--text:#F8FAFC;--muted:#94A3B8;--border:#1E293B;--shadow:0 10px 30px rgba(0,0,0,0.3);--shadow2:0 20px 50px rgba(0,0,0,0.5)}
*{margin:0;padding:0;box-sizing:border-box;font-family:'Plus Jakarta Sans',Arial, sans-serif}
body{background:var(--bg);color:var(--text);padding-bottom:96px;transition:0.3s;-webkit-font-smoothing:antialiased}
.header{position:sticky;top:0;z-index:50;background:rgba(255,255,255,0.8);backdrop-filter:blur(24px) saturate(180%);-webkit-backdrop-filter:blur(24px) saturate(180%);border-bottom:1px solid var(--border)}
.dark.header{background:rgba(21,26,39,0.85)}
.h-top{display:flex;justify-content:space-between;align-items:center;padding:14px 16px}
.logo{background:linear-gradient(135deg,#0A8EA8 0%,#06B6D4 50%,#0891B2 100%);color:#fff;padding:10px 18px;border-radius:14px;font-weight:800;font-size:14px;letter-spacing:0.5px;box-shadow:0 8px 20px rgba(10,142,168,0.3)}
.icons{display:flex;gap:10px}.ic{width:44px;height:44px;background:var(--card);border:1px solid var(--border);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:20px;cursor:pointer;box-shadow:var(--shadow);transition:0.2s}.ic:active{transform:scale(0.92)}
.h-loc{padding:0 16px 14px;display:flex;align-items:center;gap:12px}
.loc-icon{width:42px;height:42px;background:linear-gradient(135deg,#E0F7FA,#B2EBF2);border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:18px}
.dark.loc-icon{background:linear-gradient(135deg,#164E63,#0E7490)}
.h-loc b{font-size:13.5px;font-weight:700;letter-spacing:-0.2px}.h-loc small{font-size:11.5px;color:var(--muted);font-weight:600}
.search-wrap{padding:0 16px 14px;display:flex;gap:12px}
.search-box{flex:1;background:var(--card);border:1px solid var(--border);border-radius:18px;display:flex;align-items:center;gap:12px;padding:15px 18px;box-shadow:var(--shadow);transition:0.2s}
.search-box:focus-within{border-color:var(--teal);box-shadow:0 0 0 4px rgba(10,142,168,0.1)}
.search-box input{border:none;outline:none;background:transparent;flex:1;font-size:14px;font-weight:600;color:var(--text)}.search-box input::placeholder{color:var(--muted)}
.filter{width:54px;height:54px;background:#0F172A;border-radius:18px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:22px;box-shadow:var(--shadow);cursor:pointer}
.dark.filter{background:#fff;color:#000}
.hero{margin:6px 16px 18px;background:radial-gradient(100% 200% at 0% 0%,#06B6D4 0%,#0A8EA8 40%,#0E7490 100%);border-radius:28px;padding:22px 20px;display:flex;justify-content:space-between;align-items:center;color:#fff;position:relative;overflow:hidden;box-shadow:0 20px 40px rgba(10,142,168,0.25)}
.hero::before{content:"";position:absolute;top:-40px;right:-40px;width:140px;height:140px;background:rgba(255,255,255,0.15);border-radius:50%;filter:blur(10px)}
.hero h2{font-size:19px;font-weight:800;line-height:1.2;letter-spacing:-0.5px;position:relative}.hero p{font-size:12px;opacity:0.9;margin-top:6px;font-weight:600;position:relative}
.hero-btn{background:#fff;color:#0A8EA8;padding:13px 22px;border-radius:100px;font-weight:800;font-size:12px;letter-spacing:0.3px;box-shadow:0 8px 20px rgba(0,0,0,0.15);cursor:pointer;transition:0.2s;position:relative}
.hero-btn:active{transform:scale(0.96)}
.chips{display:flex;gap:10px;overflow-x:auto;padding:2px 16px 14px;scrollbar-width:none}.chips::-webkit-scrollbar{display:none}
.chip{white-space:nowrap;padding:11px 18px;border-radius:100px;background:var(--card);border:1.5px solid var(--border);font-size:12.5px;font-weight:700;cursor:pointer;transition:0.2s;box-shadow:var(--shadow);color:var(--muted)}
.chip.active{background:#0F172A;color:#fff;border-color:#0F172A;box-shadow:0 8px 20px rgba(15,23,42,0.25);transform:translateY(-1px)}
.dark.chip.active{background:#fff;color:#000;border-color:#fff}
.cats{display:flex;gap:14px;overflow-x:auto;padding:6px 16px 18px;scrollbar-width:none}.cats::-webkit-scrollbar{display:none}
.cat{min-width:72px;text-align:center;cursor:pointer;transition:0.2s}.cat:active{transform:scale(0.93)}
.cat-icon{width:68px;height:68px;border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:var(--shadow);margin:0 auto;border:1.5px solid var(--border);transition:0.2s;background:var(--card)}
.cat.active.cat-icon{background:#0F172A;color:#fff;border-color:#0F172A;transform:translateY(-2px);box-shadow:var(--shadow2)}
.dark.cat.active.cat-icon{background:#fff;color:#000}
.cat b{font-size:11px;margin-top:8px;display:block;font-weight:700;letter-spacing:-0.1px}
.section{padding:6px 16px 18px}.sec-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.sec-head h3{font-size:17px;font-weight:800;letter-spacing:-0.4px}.sec-head span{font-size:12.5px;color:var(--teal);font-weight:800;cursor:pointer;background:rgba(10,142,168,0.08);padding:8px 14px;border-radius:100px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.card{background:var(--card);border-radius:26px;overflow:hidden;box-shadow:var(--shadow);border:1px solid var(--border);transition:0.25s;cursor:pointer}
.card:active{transform:scale(0.97)}
.card-img{height:132px;display:flex;align-items:center;justify-content:center;font-size:56px;position:relative}
.badge{position:absolute;top:12px;left:12px;background:#0F172A;color:#fff;font-size:10px;font-weight:800;padding:6px 10px;border-radius:100px;letter-spacing:0.3px;box-shadow:0 4px 12px rgba(0,0,0,0.15)}
.dark.badge{background:#fff;color:#000}
.heart{position:absolute;top:12px;right:12px;width:34px;height:34px;background:rgba(255,255,255,0.9);backdrop-filter:blur(12px);border-radius:100px;display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:var(--shadow);border:1px solid rgba(0,0,0,0.05)}
.dark.heart{background:rgba(21,26,39,0.9)}
.card-body{padding:12px 14px 14px}.store{font-size:10px;font-weight:800;color:var(--teal);letter-spacing:0.6px;text-transform:uppercase}
.card-body h4{font-size:13px;font-weight:700;line-height:1.3;margin:4px 0 6px;letter-spacing:-0.2px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;height:34px}
.meta{font-size:11px;color:var(--muted);font-weight:600;display:flex;align-items:center;gap:4px}
.price-row{display:flex;justify-content:space-between;align-items:center;margin-top:10px}
.price b{font-size:15px;font-weight:800;letter-spacing:-0.3px}.price small{font-size:11px;color:var(--muted);text-decoration:line-through;margin-left:6px;font-weight:600}
.add-btn{width:38px;height:38px;background:#0F172A;color:#fff;border:none;border-radius:13px;font-size:20px;font-weight:800;cursor:pointer;box-shadow:0 6px 16px rgba(15,23,42,0.2);transition:0.2s}
.add-btn:active{transform:scale(0.9)}.dark.add-btn{background:#fff;color:#000}
.h-scroll{display:flex;gap:12px;overflow-x:auto;padding-bottom:4px;scrollbar-width:none}.h-scroll::-webkit-scrollbar{display:none}
.h-card{min-width:168px;background:var(--card);border-radius:22px;padding:12px;border:1px solid var(--border);box-shadow:var(--shadow)}
.bottom{position:fixed;bottom:16px;left:16px;right:16px;background:rgba(255,255,255,0.85);backdrop-filter:blur(24px) saturate(180%);border:1px solid var(--border);border-radius:26px;display:flex;justify-content:space-around;padding:10px 6px 10px;z-index:60;box-shadow:var(--shadow2)}
.dark.bottom{background:rgba(21,26,39,0.85)}
.tab{flex:1;text-align:center;cursor:pointer;position:relative;padding:6px 0;border-radius:16px;transition:0.2s}
.tab.active{background:var(--text);color:var(--card)}.dark.tab.active{background:#fff;color:#000}
.tab-i{font-size:22px}.tab b{font-size:9.5px;display:block;margin-top:2px;font-weight:700;letter-spacing:0.2px}
.cart-dot{position:absolute;top:2px;right:18px;background:#EF4444;color:#fff;font-size:10px;font-weight:800;min-width:20px;height:20px;border-radius:100px;display:flex;align-items:center;justify-content:center;border:2px solid var(--card);box-shadow:0 2px 8px rgba(239,68,68,0.4)}
#ai{position:fixed;bottom:100px;right:18px;width:62px;height:62px;background:linear-gradient(135deg,#0A8EA8,#06B6D4);border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:28px;color:#fff;box-shadow:0 12px 28px rgba(10,142,168,0.4);cursor:pointer;z-index:55;animation:float 3s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
#aiChat{display:none;position:fixed;bottom:88px;left:16px;right:16px;max-width:420px;margin:0 auto;height:68vh;background:var(--card);border-radius:28px;box-shadow:var(--shadow2);z-index:70;flex-direction:column;overflow:hidden;border:1px solid var(--border)} #aiChat.open{display:flex;animation:pop 0.3s cubic-bezier(0.34,1.56,0.64,1)}
@keyframes pop{0%{transform:translateY(20px) scale(0.96);opacity:0}100%{transform:translateY(0) scale(1);opacity:1}}
.ai-h{background:linear-gradient(135deg,#0A8EA8,#06B6D4);color:#fff;padding:16px 18px;display:flex;justify-content:space-between;align-items:center}
.ai-msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;background:var(--bg)}
.m{max-width:84%;padding:12px 16px;border-radius:20px;font-size:13px;line-height:1.45;font-weight:600;white-space:pre-line}
.m.u{align-self:flex-end;background:#0F172A;color:#fff;border-bottom-right-radius:8px;box-shadow:0 4px 12px rgba(15,23,42,0.15)}
.dark.m.u{background:#fff;color:#000}
.m.b{align-self:flex-start;background:var(--card);border:1px solid var(--border);border-bottom-left-radius:8px;box-shadow:var(--shadow)}
.ai-in{display:flex;gap:10px;padding:14px;border-top:1px solid var(--border);background:var(--card)}
.ai-in input{flex:1;padding:14px 18px;border-radius:100px;border:1.5px solid var(--border);background:var(--bg);color:var(--text);outline:none;font-weight:600;font-size:13px}
.ai-in input:focus{border-color:var(--teal)}
.ai-in button{padding:14px 20px;background:#0F172A;color:#fff;border:none;border-radius:100px;font-weight:800;font-size:13px}
.dark.ai-in button{background:#fff;color:#000}
.quick{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.quick button{padding:8px 12px;background:var(--bg);color:var(--teal);border:1.5px solid rgba(10,142,168,0.2);border-radius:100px;font-size:11px;font-weight:700;cursor:pointer}
.modal{display:none;position:fixed;inset:0;background:rgba(15,23,42,0.5);backdrop-filter:blur(16px);justify-content:center;align-items:flex-end;z-index:80}.modal.open{display:flex;animation:fadeIn 0.2s}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.sheet{background:var(--card);width:100%;max-width:520px;margin:0 auto;border-radius:32px 32px 0 0;max-height:90vh;overflow-y:auto;box-shadow:var(--shadow2);animation:slideUp 0.35s cubic-bezier(0.34,1.56,0.64,1)}
@keyframes slideUp{from{transform:translateY(100%)}to{transform:translateY(0)}}
.s-h{padding:20px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--card);border-radius:32px 32px 0 0;z-index:2}
.s-h h3{font-weight:800;letter-spacing:-0.3px}
.s-c{padding:18px}
.btn{width:100%;padding:16px;border:none;border-radius:18px;font-weight:800;font-size:14px;cursor:pointer;margin-top:12px;letter-spacing:-0.2px;transition:0.2s}
.btn:active{transform:scale(0.98)}
.btn-green{background:#0F172A;color:#fff;box-shadow:0 10px 20px rgba(15,23,42,0.2)}.dark.btn-green{background:#fff;color:#000}
.btn-wa{background:#22C55E;color:#fff}.input{width:100%;padding:14px 16px;border-radius:16px;border:1.5px solid var(--border);font-size:13.5px;margin:7px 0;background:var(--bg);color:var(--text);font-weight:600;outline:none;transition:0.2s}.input:focus{border-color:var(--teal);box-shadow:0 0 0 4px rgba(10,142,168,0.08)}
.cart-i{display:flex;gap:14px;padding:16px 0;border-bottom:1px solid var(--border)}.ci{width:64px;height:64px;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:var(--shadow);border:1px solid var(--border)}
.toast{position:fixed;bottom:110px;left:50%;transform:translateX(-50%);background:#0F172A;color:#fff;padding:12px 20px;border-radius:100px;font-size:12.5px;font-weight:700;z-index:100;display:none;box-shadow:var(--shadow2);letter-spacing:-0.1px}
.dark.toast{background:#fff;color:#000}
</style></head><body>
<div class="header">
<div class="h-top"><div class="logo">LONMA ORBIT</div><div class="icons"><div class="ic" onclick="toggleDark()">🌙</div><div class="ic" onclick="document.getElementById('search').focus()">🔍</div><div class="ic">🔔</div></div></div>
<div class="h-loc"><div class="loc-icon">📍</div><div><b>Kajiado Town • 30 min delivery</b><br><small id="userStatus">Guest • Login with WhatsApp</small></div><div style="margin-left:auto;font-size:20px;opacity:0.5" onclick="openProfile()">›</div></div>
<div class="search-wrap"><div class="search-box">🔍<input id="search" placeholder="Search flour, milk, bread, soda..." oninput="searchProd()"></div><div class="filter">☰</div></div>
</div>
<div class="hero"><div><h2>Free Delivery<br>on First 3 Orders!</h2><p>Use code LONMA30 • Smart AI saves 20%</p></div><div class="hero-btn" onclick="document.getElementById('grid').scrollIntoView({behavior:'smooth'})">ORDER NOW</div></div>
<div class="chips" id="storeChips"></div>
<div class="cats" id="catChips"></div>
<div class="section"><div class="sec-head"><h3>Best Deals Today</h3><span onclick="renderProducts(PRODUCTS)">See All</span></div><div class="grid" id="grid"></div></div>
<div class="section"><div class="sec-head"><h3>Flash Sale • Live</h3><span style="color:#EF4444;background:#FEF2F2" id="timer">Ends 02:14:33</span></div><div class="h-scroll" id="flash"></div></div>
<div class="bottom">
<div class="tab active"><div class="tab-i">🏠</div><b>Home</b></div>
<div class="tab" onclick="document.getElementById('catChips').scrollIntoView({behavior:'smooth'})"><div class="tab-i">🗂️</div><b>Categories</b></div>
<div class="tab" onclick="openCart()"><div class="tab-i">🛒</div><b>Cart</b><div class="cart-dot" id="cartDot">0</div></div>
<div class="tab" onclick="openRider()"><div class="tab-i">🏍️</div><b>Rider</b></div>
<div class="tab" onclick="openProfile()"><div class="tab-i">👤</div><b>Profile</b></div>
</div>
<div id="ai" onclick="toggleAI()">🤖</div>
<div id="aiChat"><div class="ai-h"><div><b style="font-size:15px">LONMA AI</b><div style="font-size:11px;opacity:0.9;font-weight:600;margin-top:2px">● Online • 5 stores • Instant replies</div></div><div onclick="toggleAI()" style="width:36px;height:36px;background:rgba(255,255,255,0.2);border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:800">✕</div></div><div class="ai-msgs" id="aiMsgs"><div class="m b">Hello! 👋 I'm LONMA AI

Ask me anything:
• Cheapest flour, milk, bread
• Will you deliver?
• Help me order
</div></div><div class="ai-in"><input id="aiInput" placeholder="Ask anything..." onkeypress="if(event.key==='Enter') sendAI()"><button onclick="sendAI()">Send</button></div></div>
<div id="cartModal" class="modal"><div class="sheet"><div class="s-h"><h3>Cart (<span id="cartC">0</span>)</h3><div onclick="closeM()" style="width:40px;height:40px;background:var(--bg);border-radius:14px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:800">✕</div></div><div class="s-c"><div id="cartItems"></div><div style="background:var(--bg);border-radius:20px;padding:16px;margin:16px 0;border:1px solid var(--border)"><div style="display:flex;justify-content:space-between;font-size:13px;margin:6px 0"><span style="color:var(--muted);font-weight:600">Subtotal</span><b>KES <span id="sub">0</span></b></div><div style="display:flex;justify-content:space-between;font-size:13px;margin:6px 0"><span style="color:var(--muted);font-weight:600">Delivery</span><b>KES 100</b></div><div style="display:flex;justify-content:space-between;font-size:15px;font-weight:800;border-top:1px solid var(--border);margin-top:10px;padding-top:12px"><span>Total</span><b>KES <span id="grand">0</span></b></div></div><input id="custName" class="input" placeholder="Full Name"><input id="custPhone" class="input" value="254" placeholder="M-Pesa Phone 2547..."><input id="custLoc" class="input" placeholder="Delivery Location (Kajiado, Kitengela)"><button class="btn btn-green" onclick="checkout()">Place Order • Rider in 30 min</button><div id="status" style="text-align:center;font-size:11px;font-weight:700;margin-top:10px"></div><div id="track" style="display:none;margin-top:14px;background:linear-gradient(135deg,#DCFCE7,#BBF7D0);border-radius:20px;padding:16px;color:#14532D;border:1px solid #86EFAC"><b>Order <span id="orderId"></span> Confirmed! 🎉</b><p style="font-size:11.5px;margin-top:6px;font-weight:600" id="riderInfo">Rider assigned</p></div></div></div></div>
<div id="riderModal" class="modal"><div class="sheet"><div class="s-h"><h3>Rider Center 🏍️</h3><div onclick="closeM()" style="width:40px;height:40px;background:var(--bg);border-radius:14px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:800">✕</div></div><div class="s-c"><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px"><div style="background:linear-gradient(135deg,#E0F7FA,#B2EBF2);padding:16px;border-radius:20px;text-align:center;color:#0E7490"><b style="font-size:20px">3</b><br><small style="font-size:10px;font-weight:700">ONLINE</small></div><div style="background:linear-gradient(135deg,#FEF3C7,#FDE68A);padding:16px;border-radius:20px;text-align:center;color:#92400E"><b id="rs2" style="font-size:20px">0</b><br><small style="font-size:10px;font-weight:700">ORDERS</small></div><div style="background:linear-gradient(135deg,#DCFCE7,#BBF7D0);padding:16px;border-radius:20px;text-align:center;color:#14532D"><b id="rs3" style="font-size:18px">KES 0</b><br><small style="font-size:10px;font-weight:700">SALES</small></div></div><div id="riderList" style="margin-top:16px"></div><div id="riderOrders" style="margin-top:12px"></div></div></div></div>
<div id="profileModal" class="modal"><div class="sheet"><div class="s-h"><h3>Profile</h3><div onclick="closeM()" style="width:40px;height:40px;background:var(--bg);border-radius:14px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:800">✕</div></div><div class="s-c"><div style="text-align:center;padding:8px 0 22px"><div style="width:88px;height:88px;background:linear-gradient(135deg,#0A8EA8,#06B6D4);border-radius:28px;display:flex;align-items:center;justify-content:center;font-size:40px;color:#fff;margin:0 auto;box-shadow:0 12px 28px rgba(10,142,168,0.3)">👤</div><h3 style="margin-top:14px;font-size:18px;font-weight:800;letter-spacing:-0.3px" id="profileName">Welcome to LONMA</h3><small style="color:var(--muted);font-weight:600" id="profilePhone">Login to order faster & save 20%</small></div><div id="notLogged"><input id="waPhone" class="input" value="254" placeholder="WhatsApp 254712..."><button class="btn btn-wa" onclick="loginWA()">Login with WhatsApp • Instant</button></div><div id="logged" style="display:none"><div style="background:linear-gradient(135deg,#DCFCE7,#BBF7D0);border-radius:18px;padding:14px;text-align:center;color:#14532D;border:1px solid #86EFAC"><b>Logged in ✓</b><br><small id="loggedPhone" style="font-weight:700">254...</small></div><button class="btn" style="background:#0F172A;color:#fff" onclick="logout()">Logout</button></div><div style="margin-top:18px;display:grid;gap:12px"><div style="background:var(--card);border:1.5px solid var(--border);border-radius:20px;padding:16px;display:flex;justify-content:space-between;align-items:center;box-shadow:var(--shadow)"><span style="font-weight:700;font-size:13px">🌙 Dark Mode</span><span onclick="toggleDark()" style="padding:8px 14px;background:var(--bg);border-radius:100px;font-size:11px;font-weight:800;cursor:pointer;border:1px solid var(--border)">Toggle</span></div><div onclick="openAdmin()" style="background:#0F172A;color:#fff;border-radius:20px;padding:16px;display:flex;justify-content:space-between;align-items:center;box-shadow:var(--shadow)"><span style="font-weight:700;font-size:13px">📊 Admin Dashboard</span><span>›</span></div></div></div></div></div>
<div id="adminModal" class="modal"><div class="sheet"><div class="s-h"><h3>Admin</h3><div onclick="closeM()" style="width:40px;height:40px;background:var(--bg);border-radius:14px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:800">✕</div></div><div class="s-c"><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px" id="adminStats"></div><div id="adminOrders" style="margin-top:14px"></div></div></div></div>
<div class="toast" id="toast"></div>
<script>
var PRODUCTS = [
{id:1,name:"Ajab Maize Flour 2kg",price:175,old:195,store:"Naivas",cat:"grocery",rate:4.8,sold:234,emoji:"🌽",color:"#FFF8E1"},
{id:2,name:"Brookside Milk 500ml",price:65,old:75,store:"Naivas",cat:"dairy",rate:4.9,sold:512,emoji:"🥛",color:"#E3F2FD"},
{id:3,name:"Coca Cola 1.25L",price:100,old:120,store:"Quickmart",cat:"drinks",rate:4.7,sold:320,emoji:"🥤",color:"#FFEBEE"},
{id:4,name:"Omo Detergent 1kg",price:285,old:320,store:"Carrefour",cat:"home",rate:4.6,sold:89,emoji:"🧴",color:"#E8F5E9"},
{id:5,name:"Tomatoes Fresh 1kg",price:80,old:100,store:"Quickmart",cat:"fresh",rate:4.9,sold:445,emoji:"🍅",color:"#FFF3E0"},
{id:6,name:"White Bread 400g",price:60,old:70,store:"Naivas",cat:"dairy",rate:4.8,sold:210,emoji:"🍞",color:"#FFF8E1"},
{id:7,name:"Pishori Rice 2kg",price:350,old:400,store:"Carrefour",cat:"grocery",rate:4.9,sold:156,emoji:"🍚",color:"#F3E5F5"},
{id:8,name:"Geisha Soap 150g",price:55,old:65,store:"Magunas",cat:"care",rate:4.5,sold:98,emoji:"🧼",color:"#E0F7FA"}
];
var STORES = ["ALL","Naivas","Quickmart","Carrefour","Chandarana","Magunas"];
var CATS = [
{id:"all",name:"All",icon:"🏪",color:"#F1F5F9"},
{id:"fresh",name:"Fresh",icon:"🥬",color:"#DCFCE7"},
{id:"grocery",name:"Grocery",icon:"🌽",color:"#FEF3C7"},
{id:"drinks",name:"Drinks",icon:"🥤",color:"#FCE7F3"},
{id:"dairy",name:"Dairy",icon:"🥛",color:"#DBEAFE"},
{id:"home",name:"Home",icon:"🧹",color:"#E0E7FF"},
{id:"care",name:"Care",icon:"🧴",color:"#CCFBF1"},
{id:"baby",name:"Baby",icon:"👶",color:"#FFEDD5"}
];
var cart = []; var total = 0; var activeStore = "ALL"; var activeCat = "all"; var isDark = false;

function renderChips(){
 var sHtml = ""; for(var i=0;i<STORES.length;i++){ var s=STORES[i]; sHtml += '<div class="'+(s===activeStore?'chip active':'chip')+'" onclick="setStore(\\''+s+'\\')">'+s+'</div>'; }
 document.getElementById("storeChips").innerHTML = sHtml;
 var cHtml = ""; for(var j=0;j<CATS.length;j++){ var c=CATS[j]; var bg=c.color; cHtml += '<div class="'+(c.id===activeCat?'cat active':'cat')+'" onclick="setCat(\\''+c.id+'\\')"><div class="cat-icon" style="background:'+bg+'">'+c.icon+'</div><b>'+c.name+'</b></div>'; }
 document.getElementById("catChips").innerHTML = cHtml;
}
function renderProducts(list){
 var html = ""; for(var i=0;i<list.length;i++){ var p=list[i]; var disc=Math.round((p.old-p.price)/p.old*100); html += '<div class="card"><div class="card-img" style="background:'+p.color+'">'+p.emoji+'<div class="badge">-'+disc+'%</div><div class="heart">♡</div></div><div class="card-body"><div class="store">'+p.store+'</div><h4>'+p.name+'</h4><div class="meta">⭐ '+p.rate+' • '+p.sold+' sold</div><div class="price-row"><div class="price"><b>KES '+p.price+'</b><small>'+p.old+'</small></div><button class="add-btn" onclick="addToCart('+p.id+')">+</button></div></div></div>'; }
 document.getElementById("grid").innerHTML = html;
}
function renderFlash(){
 var html = ""; for(var i=0;i<4;i++){ var p=PRODUCTS[i]; html += '<div class="h-card"><div style="font-size:36px;text-align:center;padding:12px;background:'+p.color+';border-radius:16px;margin-bottom:8px">'+p.emoji+'</div><div style="font-size:11.5px;font-weight:700;letter-spacing:-0.2px">'+p.name+'</div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px"><b style="font-size:13px">KES '+p.price+'</b><button class="add-btn" style="width:30px;height:30px;font-size:16px" onclick="addToCart('+p.id+')">+</button></div></div>'; }
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
 if(cart.length===0){ d.innerHTML='<p style="text-align:center;padding:28px;color:var(--muted);font-weight:600">Cart empty - add items to order</p>'; }
 else { var html=""; for(var i=0;i<cart.length;i++){ var c=cart[i]; html+='<div class="cart-i"><div class="ci" style="background:'+c.color+'">'+c.emoji+'</div><div style="flex:1"><h4 style="font-size:13px;font-weight:700">'+c.name+'</h4><small style="color:var(--muted);font-weight:600">'+c.store+' • KES '+c.price+'</small></div><b style="font-size:14px">KES '+c.price+'</b></div>'; } d.innerHTML=html; }
 document.getElementById("sub").innerText=total; document.getElementById("grand").innerText=total+100;
 document.getElementById("cartModal").classList.add("open");
}
function openRider(){ document.getElementById("riderModal").classList.add("open"); loadRiders(); }
function openProfile(){ document.getElementById("profileModal").classList.add("open"); }
function openAdmin(){ closeM(); document.getElementById("adminModal").classList.add("open"); loadAdmin(); }
function closeM(){ var modals=document.querySelectorAll(".modal"); for(var i=0;i<modals.length;i++) modals[i].classList.remove("open"); }
function toggleAI(){ document.getElementById("aiChat").classList.toggle("open"); }
function toggleDark(){ isDark=!isDark; document.body.classList.toggle("dark",isDark); localStorage.setItem("dark",isDark); showToast(isDark?"Dark mode 🌙":"Light mode ☀️"); }
function loginWA(){
 var phone=document.getElementById("waPhone").value;
 if(phone.length<10){ alert("Enter valid number 2547..."); return; }
 localStorage.setItem("user",phone);
 document.getElementById("notLogged").style.display="none"; document.getElementById("logged").style.display="block";
 document.getElementById("loggedPhone").innerText=phone; document.getElementById("profileName").innerText="Welcome! "+phone.slice(-4);
 document.getElementById("profilePhone").innerText=phone; document.getElementById("userStatus").innerText="Logged in • "+phone;
 document.getElementById("custPhone").value=phone;
 showToast("Logged in ✅"); fetch("/user/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone})});
}
function logout(){ localStorage.removeItem("user"); document.getElementById("notLogged").style.display="block"; document.getElementById("logged").style.display="none"; document.getElementById("profileName").innerText="Welcome to LONMA"; document.getElementById("profilePhone").innerText="Login to order faster & save 20%"; showToast("Logged out"); }
async function sendAI(){
 var input=document.getElementById("aiInput"); var msg=input.value.trim(); if(!msg) return;
 var box=document.getElementById("aiMsgs");
 box.innerHTML+='<div class="m u">'+msg+'</div>'; input.value=""; box.scrollTop=box.scrollHeight;
 try{
   var r=await fetch("/ai/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:msg,cart_count:cart.length})});
   var d=await r.json();
   var quickHtml = "";
   if(d.quick && d.quick.length>0){
     quickHtml = '<div class="quick">';
     for(var i=0;i<d.quick.length;i++){ quickHtml += '<button onclick="askQuick(\\''+d.quick[i]+'\\')">'+d.quick[i]+'</button>'; }
     quickHtml += '</div>';
   }
   box.innerHTML+='<div class="m b">'+d.reply+quickHtml+'</div>';
 } catch(e){
   box.innerHTML+='<div class="m b">Sorry, error. Try again.</div>';
 }
 box.scrollTop=box.scrollHeight;
}
function askQuick(text){ document.getElementById("aiInput").value=text; sendAI(); }
async function checkout(){
 var phone=document.getElementById("custPhone").value; var loc=document.getElementById("custLoc").value;
 if(!loc){ alert("Enter location"); return; }
 document.getElementById("status").innerText="Placing order...";
 var r=await fetch("/mpesa/stkpush",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone,amount:total+100,location:loc,cart:cart})});
 var d=await r.json(); document.getElementById("orderId").innerText=d.order_id; document.getElementById("status").innerText="Order placed!"; document.getElementById("track").style.display="block"; document.getElementById("riderInfo").innerText="Rider John KMEZ 123A • 4.9★ • 30min away • Will call you"; cart=[]; total=0; document.getElementById("cartDot").innerText=0;
}
async function loadRiders(){
 var r=await fetch("/riders"); var riders=await r.json();
 var html=""; for(var i=0;i<riders.length;i++){ var rd=riders[i]; html+='<div style="background:var(--card);border:1.5px solid var(--border);border-radius:20px;padding:14px;display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;box-shadow:var(--shadow)"><div><b style="font-size:13px">'+rd.name+' ⭐'+rd.rating+'</b><br><small style="color:var(--muted);font-weight:600">'+rd.motor+' • '+rd.location+'</small></div><div style="padding:7px 12px;border-radius:100px;background:'+(rd.status==="available"?"#DCFCE7":"#FEF3C7")+';color:'+(rd.status==="available"?"#14532D":"#92400E")+';font-size:10px;font-weight:800">'+rd.status.toUpperCase()+'</div></div>'; }
 document.getElementById("riderList").innerHTML=html;
 var ro=await fetch("/orders"); var orders=await ro.json();
 document.getElementById("rs2").innerText=orders.length; document.getElementById("rs3").innerText="KES "+orders.reduce(function(s,o){return s+o.amount},0);
 var oh='<h4 style="margin:14px 0 10px;font-size:13px;font-weight:800">Active Orders</h4>'; for(var j=0;j<Math.min(orders.length,5);j++){ var o=orders[j]; oh+='<div style="background:var(--card);border:1.5px solid var(--border);border-radius:18px;padding:12px;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><div><b style="font-size:12px">'+o.id+'</b> KES '+o.amount+'<br><small style="color:var(--muted);font-weight:600">'+o.location+'</small></div><button onclick="acceptOrder(\\''+o.id+'\\')" style="padding:9px 14px;background:#0F172A;color:#fff;border:none;border-radius:100px;font-size:11px;font-weight:800">Accept</button></div>'; }
 document.getElementById("riderOrders").innerHTML=oh;
}
async function loadAdmin(){
 var r=await fetch("/orders"); var o=await r.json();
 document.getElementById("adminStats").innerHTML='<div style="background:var(--card);border:1.5px solid var(--border);padding:18px;border-radius:20px;text-align:center;box-shadow:var(--shadow)"><b style="font-size:24px">'+o.length+'</b><br><small style="color:var(--muted);font-weight:700;font-size:10px">ORDERS</small></div><div style="background:var(--card);border:1.5px solid var(--border);padding:18px;border-radius:20px;text-align:center;box-shadow:var(--shadow)"><b style="font-size:20px">KES '+o.reduce(function(s,x){return s+x.amount},0)+'</b><br><small style="color:var(--muted);font-weight:700;font-size:10px">REVENUE</small></div>';
 var html=""; for(var i=0;i<Math.min(o.length,8);i++){ var x=o[i]; html+='<div style="background:var(--card);border:1.5px solid var(--border);border-radius:18px;padding:12px;margin-bottom:8px"><b style="font-size:12px">'+x.id+'</b> - '+x.status+'<br><small style="color:var(--muted);font-weight:600">'+x.location+' • KES '+x.amount+'</small></div>'; }
 document.getElementById("adminOrders").innerHTML=html;
}
async function acceptOrder(id){ await fetch("/rider/accept/"+id,{method:"POST"}); showToast("Accepted "+id+" ✓"); loadRiders(); }
function showToast(t){ var el=document.getElementById("toast"); el.innerText=t; el.style.display="block"; setTimeout(function(){el.style.display="none"},2600); }

if(localStorage.getItem("dark")==="true"){ isDark=true; document.body.classList.add("dark"); }
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
        quick=[]
        low=msg.lower()
        if "deliver" in low or "bring" in low:
            quick=["Yes bring it on","Where do you deliver?","Delivery fee?"]
        elif "flour" in low:
            quick=["Add flour to cart","Milk price?","Cheapest rice?"]
        elif "help" in low:
            quick=["Will you deliver?","Cheapest flour","How to order?"]
        elif "hello" in low or "hi" in low:
            quick=["Help me","Cheapest flour","Will you deliver?"]
        else:
            quick=["Help me","Will you deliver?","Cheapest flour"]
        return {"reply": reply, "quick": quick}
    except:
        return {"reply": "I can help with delivery, prices, ordering. Try 'Help me'", "quick": ["Help me","Will you deliver?"]}

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

@app.get("/logo.png")
async def logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    return HTMLResponse("", status_code=404)

@app.get("/favicon.ico")
async def fav():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    return HTMLResponse("", status_code=404)
