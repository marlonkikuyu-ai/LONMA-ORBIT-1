from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, base64, requests, random, re
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

PRODUCTS=[
 {"id":1,"name":"Ajab Maize Flour 2kg","price":175,"old":195,"store":"Naivas","cat":"grocery","stock":50,"rate":4.8,"sold":234,"emoji":"🌽"},
 {"id":2,"name":"Brookside Milk 500ml","price":65,"old":75,"store":"Naivas","cat":"dairy","stock":100,"rate":4.9,"sold":512,"emoji":"🥛"},
 {"id":3,"name":"Coca Cola 1.25L","price":100,"old":120,"store":"Quickmart","cat":"drinks","stock":80,"rate":4.7,"sold":320,"emoji":"🥤"},
 {"id":4,"name":"Omo Detergent 1kg","price":285,"old":320,"store":"Carrefour","cat":"home","stock":40,"rate":4.6,"sold":89,"emoji":"🧴"},
 {"id":5,"name":"Tomatoes Fresh 1kg","price":80,"old":100,"store":"Quickmart","cat":"fresh","stock":60,"rate":4.9,"sold":445,"emoji":"🍅"},
 {"id":6,"name":"White Bread 400g","price":60,"old":70,"store":"Naivas","cat":"dairy","stock":70,"rate":4.8,"sold":210,"emoji":"🍞"},
 {"id":7,"name":"Pishori Rice 2kg","price":350,"old":400,"store":"Carrefour","cat":"grocery","stock":30,"rate":4.9,"sold":156,"emoji":"🍚"},
 {"id":8,"name":"Geisha Soap 150g","price":55,"old":65,"store":"Magunas","cat":"care","stock":90,"rate":4.5,"sold":98,"emoji":"🧼"},
]
RIDERS=[{"id":1,"name":"John Mwangi","motor":"KMEZ 123A","status":"available","rating":4.9,"location":"Kajiado","trips":12},{"id":2,"name":"Peter Ochieng","motor":"KMFA 456B","status":"delivering","rating":4.8,"location":"Kitengela","trips":28},{"id":3,"name":"Samuel Kiprop","motor":"KMEB 789C","status":"available","rating":5.0,"location":"Rongai","trips":15}]
ORDERS=[]

# ===== SMART AI BOT LOGIC =====
def smart_ai_reply(message, cart_count=0):
    msg = message.lower().strip()

    # Greetings
    if any(w in msg for w in ["hello","hi","hey","jambo","habari"]):
        return "Hello! 👋 I'm LONMA AI, your smart shopping assistant!\n\nI know prices from 5 stores: Naivas, Quickmart, Carrefour, Chandarana & Magunas.\n\nI can:\n• Find cheapest products\n• Check stock\n• Track rider delivery\n• Help you order\n\nWhat do you need today? Try 'cheapest flour' or 'help me'"

    # Help
    if any(w in msg for w in ["help","assist","what can you","how to","guide"]):
        return "I can help you with:\n\n🛒 PRODUCTS: Say 'flour', 'milk', 'bread', 'soda' - I'll find cheapest price\n\n💰 PRICES: 'cheapest flour' or 'compare milk'\n\n🏍️ DELIVERY: 'will you deliver?', 'rider time', 'delivery fee'\n\n📦 ORDER: 'how to order', 'my cart', 'checkout'\n\n💳 PAYMENT: 'M-Pesa', 'cash on delivery'\n\nJust type what you need! For example: 'Will you deliver to Kitengela?'"

    # Delivery questions - FIXES YOUR SCREENSHOT ISSUE
    if any(w in msg for w in ["deliver","delivery","bring","come","transport"]):
        if "where" in msg or "location" in msg or "area" in msg:
            return "Yes! We deliver to:\n\n📍 Kajiado Town\n📍 Kitengela\n📍 Rongai\n📍 Kiserian\n📍 Ongata Rongai\n\nDelivery in 30 minutes! Fee is KES 100.\n\nWe have 3 riders online now:\n• John Mwangi - KMEZ 123A - 4.9★ - Available\n• Peter Ochieng - 4.8★ - Delivering\n• Samuel Kiprop - 5.0★ - Available\n\nWhere should I deliver to?"
        if "kitengela" in msg or "rongai" in msg or "kajiado" in msg:
            return f"Yes! We deliver to {msg.title()}! 🏍️\n\nDelivery time: 30 minutes\nDelivery fee: KES 100\nRider will call you when near.\n\nAdd products to cart and checkout - rider will be assigned immediately!\n\nWhat do you want to order?"
        return "Yes, we deliver! 🚚💨\n\n✅ We deliver in 30 minutes\n✅ Areas: Kajiado, Kitengela, Rongai\n✅ Fee: KES 100 only\n✅ 3 riders available now\n✅ Pay M-Pesa or Cash\n\nJust add items to cart and checkout. Where do you want delivery?"

    if "yes" in msg and ("bring" in msg or "deliver" in msg or "on" in msg):
        return "Great! Let's order! 🛒\n\n1. Add products from Best Deals (tap + button)\n2. Click Cart icon (bottom)\n3. Enter your location and M-Pesa number\n4. Click 'Place Order'\n\nRider will be assigned in 30 seconds and deliver in 30 minutes!\n\nWhat do you want? Flour? Milk? Bread?"

    if "will you" in msg or "can you" in msg:
        if "deliver" in msg:
            return "Yes, we will deliver! 🏍️ 30 minutes, KES 100 fee. We cover Kajiado, Kitengela, Rongai. Add to cart and checkout - rider comes immediately!"
        return "Yes, I can help! Tell me what you need - flour, milk, delivery info, or how to order?"

    # Price comparisons
    if "cheapest" in msg or "cheap" in msg or "lowest" in msg:
        for p in PRODUCTS:
            if any(word in msg for word in p["name"].lower().split()[:2]):
                cheapest = min([x for x in PRODUCTS if p["cat"]==x["cat"]], key=lambda x: x["price"]) if len([x for x in PRODUCTS if p["cat"]==x["cat"]])>1 else p
                return f"Cheapest {p['name'].split()[0]} is {cheapest['name']} at KES {cheapest['price']} at {cheapest['store']} (was KES {cheapest['old']}) - {cheapest['stock']} in stock! ⭐{cheapest['rate']}\n\nTap + to add to cart!"
        # Generic cheapest
        return "Here are cheapest items today:\n\n🌽 Flour 2kg - KES 175 Naivas (was 195)\n🥛 Milk 500ml - KES 65 Naivas (was 75)\n🍅 Tomatoes 1kg - KES 80 Quickmart (was 100)\n🍞 Bread - KES 60 Naivas\n\nAll have 10-20% OFF! Which do you want?"

    # Specific products
    if "flour" in msg or "maize" in msg or "unga" in msg:
        return "Ajab Maize Flour 2kg:\n\n💰 KES 175 at Naivas (cheapest!)\n💰 KES 178 at Quickmart\n💰 KES 172 at Carrefour (best deal!)\n\n📦 50 packs in stock\n⭐ 4.8 stars, 234 sold\n\nGood for ugali! Tap + on flour card to add to cart. Want me to add it?"

    if "milk" in msg or "maziwa" in msg:
        return "Brookside Milk 500ml:\n\n💰 KES 65 Naivas\n💰 KES 62 Chandarana (cheapest!)\n📦 100 packs fresh today\n⭐ 4.9 stars, 512 sold\n\nFresh daily milk! Goes well with bread KES 60. Add to cart?"

    if "bread" in msg or "mkate" in msg:
        return "White Bread 400g:\n\n💰 KES 60 Naivas (fresh)\n📦 70 loaves available\n⭐ 4.8 stars\n\nSoft fresh bread! Best with milk and eggs. Tap + to add!"

    if "tomato" in msg or "nyanya" in msg:
        return "Tomatoes Fresh 1kg:\n\n💰 KES 80 Quickmart (was KES 100)\n📦 60kg farm fresh today\n⭐ 4.9 stars, 445 sold\n\nFarm fresh! Great for stew. Add to cart?"

    if "soda" in msg or "coke" in msg or "drink" in msg:
        return "Coca Cola 1.25L:\n\n💰 KES 100 Quickmart\n💰 KES 99 Magunas (cheapest)\n📦 80 bottles chilled\n⭐ 4.7 stars\n\nChilled! Add to cart?"

    if "omo" in msg or "detergent" in msg or "soap" in msg:
        return "Omo Detergent 1kg KES 285 at Carrefour (cheapest, was 320) - 40 packs. Geisha Soap 150g KES 55 Magunas. Need household items?"

    if "rider" in msg or "delivery time" in msg or "how long" in msg:
        return "Rider info 🏍️:\n\n⏱️ Delivery: 30 minutes\n💰 Fee: KES 100\n📍 Areas: Kajiado, Kitengela, Rongai\n👥 Riders: 3 online\n\n• John KMEZ 123A - 4.9★ - Available - Kajiado\n• Peter KMFA 456B - 4.8★ - Delivering - Kitengela\n• Samuel KMEB 789C - 5.0★ - Available - Rongai\n\nRider calls you when 2 mins away!"

    if "cart" in msg or "order" in msg or "checkout" in msg or "buy" in msg:
        return f"You have {cart_count} items in cart.\n\nTo order:\n1. Tap + on products to add\n2. Click Cart icon bottom\n3. Enter location + M-Pesa number\n4. Click 'Place Order'\n\nRider assigned in 30 seconds!\n\nNeed help adding something?"

    if "price" in msg or "how much" in msg or "cost" in msg:
        return "Tell me which product! For example:\n• 'flour price'\n• 'milk price'\n• 'cheapest bread'\n\nI compare 5 supermarkets to give you cheapest!"

    if "stock" in msg or "available" in msg or "left" in msg:
        stock_info = "\n".join([f"• {p['emoji']} {p['name']}: {p['stock']} left at {p['store']}" for p in PRODUCTS[:5]])
        return f"Current stock:\n\n{stock_info}\n\nAll fresh today! Which do you need?"

    if "payment" in msg or "mpesa" in msg or "pay" in msg or "cash" in msg:
        return "Payment options:\n\n💚 Lipa na M-Pesa: Enter 2547... number, STK push sent\n💵 Cash on Delivery: Pay rider when he delivers\n\nBoth work! M-Pesa is faster. Which do you prefer?"

    if "thank" in msg or "thanks" in msg or "asante" in msg:
        return "You're welcome! 😊 Happy to help!\n\nNeed anything else? Flour, milk, delivery info? I'm here 24/7!"

    # Fallback - intelligent
    found = []
    for p in PRODUCTS:
        if any(word in msg for word in p["name"].lower().split() if len(word)>2):
            found.append(p)

    if found:
        p = found[0]
        return f"Found {p['name']}! {p['emoji']}\n\n💰 KES {p['price']} at {p['store']} (was KES {p['old']})\n📦 {p['stock']} in stock\n⭐ {p['rate']} stars, {p['sold']} sold\n\nTap + button on product card to add to cart! Need anything else?"

    return f"I understood: '{message}'\n\nI'm LONMA AI - I can:\n\n• Find products: say 'flour' or 'milk'\n• Check cheapest: 'cheapest flour'\n• Delivery: 'will you deliver to Kitengela?'\n• Order help: 'how to order'\n\nTry asking:\n• 'Help me'\n• 'Will you deliver?'\n• 'Cheapest milk'\n• 'What is in stock?'"

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse('''
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT</title>
<style>
:root{--bg:#f6f7fb;--card:#fff;--text:#111;--muted:#666;--border:#eee}
.dark{--bg:#0f0f0f;--card:#1c1c1e;--text:#fff;--muted:#aaa;--border:#2a2a2a}
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial} body{background:var(--bg);color:var(--text);padding-bottom:90px}
.header{position:sticky;top:0;z-index:50;background:var(--card);border-bottom:1px solid var(--border)}
.h-top{display:flex;justify-content:space-between;align-items:center;padding:10px 14px}
.logo{width:110px;height:36px;background:#0A8EA8;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900;font-size:14px}
.icons{display:flex;gap:8px}.ic-btn{width:38px;height:38px;background:var(--bg);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:18px;cursor:pointer;border:1px solid var(--border)}
.h-location{padding:0 14px 10px;display:flex;align-items:center;gap:8px}.pin{width:32px;height:32px;background:#e6f7fa;border-radius:10px;display:flex;align-items:center;justify-content:center}.h-location b{font-size:13px}.h-location small{font-size:11px;color:var(--muted)}
.search{padding:10px 14px;background:var(--card);display:flex;gap:10px}.search-box{flex:1;background:var(--bg);border-radius:14px;display:flex;align-items:center;gap:10px;padding:12px 14px;border:1px solid var(--border)}.search-box input{border:none;background:transparent;outline:none;flex:1;font-size:13px;color:var(--text)}.filter-btn{width:48px;height:48px;background:#111;border-radius:14px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px}
.hero{margin:12px 14px;background:linear-gradient(105deg,#0A8EA8 0%,#00c2a2 100%);border-radius:20px;padding:16px;display:flex;justify-content:space-between;align-items:center;color:#fff}
.hero h2{font-size:17px;font-weight:800}.hero p{font-size:11px;opacity:0.9;margin-top:4px}.hero-btn{background:#fff;color:#0A8EA8;padding:10px 16px;border-radius:24px;font-weight:800;font-size:11px}
.chips{display:flex;gap:8px;overflow-x:auto;padding:8px 14px}.chip{white-space:nowrap;padding:8px 14px;border-radius:20px;background:var(--card);border:1px solid var(--border);font-size:11px;font-weight:700;cursor:pointer}.chip.active{background:#111;color:#fff}
.cats{display:flex;gap:12px;overflow-x:auto;padding:12px 14px}.cat{min-width:64px;text-align:center;cursor:pointer}.cat-icon{width:60px;height:60px;background:var(--card);border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:26px;box-shadow:0 4px 12px rgba(0,0,0,0.06);margin:0 auto;border:1px solid var(--border)}.cat.active.cat-icon{background:#0A8EA8;color:#fff}.cat b{font-size:10px;margin-top:6px;display:block}
.section{padding:10px 14px}.sec-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}.sec-head h3{font-size:15px;font-weight:800}.sec-head span{font-size:11px;color:#0A8EA8;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.card{background:var(--card);border-radius:20px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.05);border:1px solid var(--border)}
.card-img{height:120px;background:var(--bg);display:flex;align-items:center;justify-content:center;font-size:42px;position:relative}.badge{position:absolute;top:10px;left:10px;background:#ff3b30;color:#fff;font-size:9px;font-weight:800;padding:4px 7px;border-radius:8px}.heart{position:absolute;top:10px;right:10px;width:30px;height:30px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px}
.card-body{padding:10px}.store{font-size:8px;font-weight:800;color:#0A8EA8}.card-body h4{font-size:12px;font-weight:700;height:32px;overflow:hidden}.meta{font-size:10px;color:var(--muted);margin:4px 0}.price-row{display:flex;justify-content:space-between;align-items:center;margin-top:8px}.price b{font-size:14px}.price small{font-size:10px;color:#999;text-decoration:line-through;margin-left:4px}.add-btn{width:32px;height:32px;background:#111;color:#fff;border:none;border-radius:11px;font-size:18px;font-weight:800;cursor:pointer}
.h-scroll{display:flex;gap:10px;overflow-x:auto}.h-card{min-width:160px;background:var(--card);border-radius:18px;padding:10px;border:1px solid var(--border)}
.bottom{position:fixed;bottom:0;left:0;right:0;background:var(--card);border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:8px 0 12px;z-index:60}
.tab{flex:1;text-align:center;cursor:pointer;position:relative}.tab-i{font-size:22px}.tab.active{color:#0A8EA8}.tab b{font-size:9px;display:block}.cart-dot{position:absolute;top:0;right:22px;background:#ff3b30;color:#fff;font-size:10px;font-weight:800;min-width:18px;height:18px;border-radius:9px;display:flex;align-items:center;justify-content:center}
#ai{position:fixed;bottom:92px;right:14px;width:58px;height:58px;background:#0A8EA8;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:28px;color:#fff;box-shadow:0 8px 24px rgba(10,142,168,0.45);cursor:pointer;z-index:55}
#aiChat{display:none;position:fixed;bottom:20px;left:12px;right:12px;max-width:420px;margin:0 auto;height:70vh;background:var(--card);border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,0.25);z-index:70;flex-direction:column;overflow:hidden;border:1px solid var(--border)} #aiChat.open{display:flex}
.ai-h{background:#0A8EA8;color:#fff;padding:14px 16px;display:flex;justify-content:space-between;align-items:center}.ai-msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:var(--bg)}.m{max-width:85%;padding:10px 14px;border-radius:18px;font-size:12px;line-height:1.4;white-space:pre-line}.m.u{align-self:flex-end;background:#0A8EA8;color:#fff;border-bottom-right-radius:6px}.m.b{align-self:flex-start;background:var(--card);border:1px solid var(--border);border-bottom-left-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,0.04)}.ai-in{display:flex;gap:8px;padding:12px;border-top:1px solid var(--border);background:var(--card)}.ai-in input{flex:1;padding:12px 16px;border-radius:24px;border:1px solid var(--border);background:var(--bg);color:var(--text);outline:none}.ai-in button{padding:12px 18px;background:#0A8EA8;color:#fff;border:none;border-radius:24px;font-weight:800}
.quick{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}.quick button{padding:6px 10px;background:#e0f7fa;color:#0A8EA8;border:1px solid #0A8EA8;border-radius:14px;font-size:10px;font-weight:700;cursor:pointer}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);backdrop-filter:blur(8px);justify-content:center;align-items:flex-end;z-index:80}.modal.open{display:flex}
.sheet{background:var(--card);width:100%;max-width:500px;margin:0 auto;border-radius:28px 28px 0 0;max-height:88vh;overflow-y:auto}.s-h{padding:18px 16px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--card)}.s-c{padding:16px}
.btn{width:100%;padding:15px;border:none;border-radius:16px;font-weight:800;font-size:14px;cursor:pointer;margin-top:10px}.btn-green{background:#00a651;color:#fff}.btn-wa{background:#25D366;color:#fff}.input{width:100%;padding:13px 14px;border-radius:14px;border:1px solid var(--border);font-size:13px;margin:6px 0;background:var(--bg);color:var(--text)}
.cart-i{display:flex;gap:12px;padding:14px 0;border-bottom:1px solid var(--border)}.ci{width:60px;height:60px;background:var(--bg);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:28px}
.toast{position:fixed;bottom:100px;left:50%;transform:translateX(-50%);background:#111;color:#fff;padding:10px 18px;border-radius:24px;font-size:12px;font-weight:700;z-index:100;display:none}
</style></head><body>
<div class="header">
<div class="h-top"><div class="logo">LONMA ORBIT</div><div class="icons"><div class="ic-btn" onclick="toggleDark()">🌙</div><div class="ic-btn" onclick="document.getElementById('search').focus()">🔍</div><div class="ic-btn">🔔</div></div></div>
<div class="h-location"><div class="pin">📍</div><div><b>Kajiado Town • 30 min delivery</b><br><small id="userStatus">Guest • Login with WhatsApp</small></div><div style="margin-left:auto" onclick="openProfile()">›</div></div>
<div class="search"><div class="search-box">🔍<input id="search" placeholder="Search flour, milk, bread..." oninput="searchProd()"></div><div class="filter-btn">☰</div></div>
</div>
<div class="hero"><div><h2>Free Delivery<br>on First 3 Orders!</h2><p>Use code LONMA30 • Smart AI Bot</p></div><div class="hero-btn">ORDER NOW</div></div>
<div class="chips" id="storeChips"></div>
<div class="cats" id="catChips"></div>
<div class="section"><div class="sec-head"><h3>Best Deals Today</h3><span onclick="renderProducts(PRODUCTS)">See All</span></div><div class="grid" id="grid"></div></div>
<div class="section"><div class="sec-head"><h3>Flash Sale</h3><span style="color:#ff3b30" id="timer">Ends 02:14:33</span></div><div class="h-scroll" id="flash"></div></div>
<div class="bottom">
<div class="tab active"><div class="tab-i">🏠</div><b>Home</b></div>
<div class="tab" onclick="document.getElementById('catChips').scrollIntoView({behavior:'smooth'})"><div class="tab-i">🗂️</div><b>Categories</b></div>
<div class="tab" onclick="openCart()"><div class="tab-i">🛒</div><b>Cart</b><div class="cart-dot" id="cartDot">0</div></div>
<div class="tab" onclick="openRider()"><div class="tab-i">🏍️</div><b>Rider</b></div>
<div class="tab" onclick="openProfile()"><div class="tab-i">👤</div><b>Profile</b></div>
</div>
<div id="ai" onclick="toggleAI()">🤖</div>
<div id="aiChat"><div class="ai-h"><div><b>LONMA AI</b><div style="font-size:11px;opacity:0.85">Online • 5 stores • Smart Bot</div></div><div onclick="toggleAI()" style="width:32px;height:32px;background:rgba(255,255,255,0.2);border-radius:10px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="ai-msgs" id="aiMsgs"><div class="m b">Hello! 👋 I'm your smart LONMA AI!

I know prices from 5 supermarkets and can:

• Find cheapest flour, milk, etc
• Answer "Will you deliver?"
• Help you order

Try:
• "Help me"
• "Will you deliver to Kitengela?"
• "Cheapest flour"
</div></div><div class="ai-in"><input id="aiInput" placeholder="Ask anything..." onkeypress="if(event.key==='Enter') sendAI()"><button onclick="sendAI()">Send</button></div></div>
<div id="cartModal" class="modal"><div class="sheet"><div class="s-h"><h3>Cart (<span id="cartC">0</span>)</h3><div onclick="closeM()" style="width:36px;height:36px;background:var(--bg);border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="s-c"><div id="cartItems"></div><div style="background:var(--bg);border-radius:16px;padding:14px;margin:14px 0"><div style="display:flex;justify-content:space-between;font-size:12px;margin:5px 0"><span>Subtotal</span><b>KES <span id="sub">0</span></b></div><div style="display:flex;justify-content:space-between;font-size:12px;margin:5px 0"><span>Delivery</span><b>KES 100</b></div><div style="display:flex;justify-content:space-between;font-size:14px;font-weight:800;border-top:1px solid var(--border);margin-top:8px;padding-top:10px"><span>Total</span><b>KES <span id="grand">0</span></b></div></div><input id="custName" class="input" placeholder="Full Name"><input id="custPhone" class="input" value="254" placeholder="M-Pesa Phone"><input id="custLoc" class="input" placeholder="Delivery Location"><button class="btn btn-green" onclick="checkout()">Place Order - Rider 30min</button><div id="status" style="text-align:center;font-size:11px;font-weight:700;margin-top:8px"></div><div id="track" style="display:none;margin-top:12px;background:#e8f5e9;border-radius:16px;padding:14px;color:#000"><b>Order <span id="orderId"></span> Confirmed!</b><p style="font-size:11px;margin-top:6px" id="riderInfo">Rider assigned</p></div></div></div></div>
<div id="riderModal" class="modal"><div class="sheet"><div class="s-h"><h3>Rider Center</h3><div onclick="closeM()" style="width:36px;height:36px;background:var(--bg);border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="s-c"><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px"><div style="background:#e0f7fa;padding:14px;border-radius:16px;text-align:center"><b>3</b><br><small style="font-size:10px">Online</small></div><div style="background:#fff3cd;padding:14px;border-radius:16px;text-align:center"><b id="rs2">0</b><br><small style="font-size:10px">Orders</small></div><div style="background:#d4edda;padding:14px;border-radius:16px;text-align:center"><b id="rs3">KES 0</b><br><small style="font-size:10px">Sales</small></div></div><div id="riderList" style="margin-top:14px"></div><div id="riderOrders" style="margin-top:10px"></div></div></div></div>
<div id="profileModal" class="modal"><div class="sheet"><div class="s-h"><h3>Profile</h3><div onclick="closeM()" style="width:36px;height:36px;background:var(--bg);border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="s-c"><div style="text-align:center;padding:10px 0 20px"><div style="width:80px;height:80px;background:#0A8EA8;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:36px;color:#fff;margin:0 auto">👤</div><h3 style="margin-top:12px" id="profileName">Welcome</h3><small style="color:var(--muted)" id="profilePhone">Login to order faster</small></div><div id="notLogged"><input id="waPhone" class="input" value="254" placeholder="WhatsApp 254712..."><button class="btn btn-wa" onclick="loginWA()">Login with WhatsApp</button></div><div id="logged" style="display:none"><div style="background:#d4edda;border-radius:14px;padding:12px;text-align:center;color:#000"><b>Logged in</b><br><small id="loggedPhone">254...</small></div><button class="btn" style="background:#111;color:#fff" onclick="logout()">Logout</button></div><div style="margin-top:16px;display:grid;gap:10px"><div style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:14px;display:flex;justify-content:space-between"><span>Dark Mode</span><span onclick="toggleDark()" style="padding:6px 12px;background:var(--bg);border-radius:10px;font-size:11px;font-weight:800;cursor:pointer">Toggle</span></div><div onclick="openAdmin()" style="background:#111;color:#fff;border-radius:16px;padding:14px;display:flex;justify-content:space-between"><span>Admin Dashboard</span><span>›</span></div></div></div></div></div>
<div id="adminModal" class="modal"><div class="sheet"><div class="s-h"><h3>Admin</h3><div onclick="closeM()" style="width:36px;height:36px;background:var(--bg);border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer">✕</div></div><div class="s-c"><div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px" id="adminStats"></div><div id="adminOrders" style="margin-top:12px"></div></div></div></div>
<div class="toast" id="toast"></div>
<script>
var PRODUCTS = [
{id:1,name:"Ajab Maize Flour 2kg",price:175,old:195,store:"Naivas",cat:"grocery",rate:4.8,sold:234,emoji:"🌽"},
{id:2,name:"Brookside Milk 500ml",price:65,old:75,store:"Naivas",cat:"dairy",rate:4.9,sold:512,emoji:"🥛"},
{id:3,name:"Coca Cola 1.25L",price:100,old:120,store:"Quickmart",cat:"drinks",rate:4.7,sold:320,emoji:"🥤"},
{id:4,name:"Omo Detergent 1kg",price:285,old:320,store:"Carrefour",cat:"home",rate:4.6,sold:89,emoji:"🧴"},
{id:5,name:"Tomatoes Fresh 1kg",price:80,old:100,store:"Quickmart",cat:"fresh",rate:4.9,sold:445,emoji:"🍅"},
{id:6,name:"White Bread 400g",price:60,old:70,store:"Naivas",cat:"dairy",rate:4.8,sold:210,emoji:"🍞"},
{id:7,name:"Pishori Rice 2kg",price:350,old:400,store:"Carrefour",cat:"grocery",rate:4.9,sold:156,emoji:"🍚"},
{id:8,name:"Geisha Soap 150g",price:55,old:65,store:"Magunas",cat:"care",rate:4.5,sold:98,emoji:"🧼"}
];
var STORES = ["ALL","Naivas","Quickmart","Carrefour","Chandarana","Magunas"];
var CATS = [{id:"all",name:"All",icon:"🏪"},{id:"fresh",name:"Fresh",icon:"🥬"},{id:"grocery",name:"Grocery",icon:"🌽"},{id:"drinks",name:"Drinks",icon:"🥤"},{id:"dairy",name:"Dairy",icon:"🥛"},{id:"home",name:"Home",icon:"🧹"},{id:"care",name:"Care",icon:"🧴"},{id:"baby",name:"Baby",icon:"👶"}];
var cart = []; var total = 0; var activeStore = "ALL"; var activeCat = "all"; var isDark = false;

function renderChips(){
 var sHtml = ""; for(var i=0;i<STORES.length;i++){ var s=STORES[i]; sHtml += '<div class="'+(s===activeStore?'chip active':'chip')+'" onclick="setStore(\\''+s+'\\')">'+s+'</div>'; }
 document.getElementById("storeChips").innerHTML = sHtml;
 var cHtml = ""; for(var j=0;j<CATS.length;j++){ var c=CATS[j]; cHtml += '<div class="'+(c.id===activeCat?'cat active':'cat')+'" onclick="setCat(\\''+c.id+'\\')"><div class="cat-icon">'+c.icon+'</div><b>'+c.name+'</b></div>'; }
 document.getElementById("catChips").innerHTML = cHtml;
}
function renderProducts(list){
 var html = ""; for(var i=0;i<list.length;i++){ var p=list[i]; var disc=Math.round((p.old-p.price)/p.old*100); html += '<div class="card"><div class="card-img">'+p.emoji+'<div class="badge">-'+disc+'%</div><div class="heart">♡</div></div><div class="card-body"><div class="store">'+p.store+'</div><h4>'+p.name+'</h4><div class="meta">⭐ '+p.rate+' • '+p.sold+' sold</div><div class="price-row"><div class="price"><b>KES '+p.price+'</b><small>KES '+p.old+'</small></div><button class="add-btn" onclick="addToCart('+p.id+')">+</button></div></div></div>'; }
 document.getElementById("grid").innerHTML = html;
}
function renderFlash(){
 var html = ""; for(var i=0;i<4;i++){ var p=PRODUCTS[i]; html += '<div class="h-card"><div style="font-size:32px;text-align:center;padding:10px">'+p.emoji+'</div><div style="font-size:11px;font-weight:700">'+p.name+'</div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px"><b>KES '+p.price+'</b><button class="add-btn" style="width:26px;height:26px" onclick="addToCart('+p.id+')">+</button></div></div>'; }
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
 showToast(p.name+" added");
}
function openCart(){
 var d=document.getElementById("cartItems");
 if(cart.length===0){ d.innerHTML='<p style="text-align:center;padding:20px;color:var(--muted)">Cart empty</p>'; }
 else { var html=""; for(var i=0;i<cart.length;i++){ var c=cart[i]; html+='<div class="cart-i"><div class="ci">'+c.emoji+'</div><div style="flex:1"><h4 style="font-size:12px">'+c.name+'</h4><small>'+c.store+' • KES '+c.price+'</small></div><b>KES '+c.price+'</b></div>'; } d.innerHTML=html; }
 document.getElementById("sub").innerText=total; document.getElementById("grand").innerText=total+100;
 document.getElementById("cartModal").classList.add("open");
}
function openRider(){ document.getElementById("riderModal").classList.add("open"); loadRiders(); }
function openProfile(){ document.getElementById("profileModal").classList.add("open"); }
function openAdmin(){ closeM(); document.getElementById("adminModal").classList.add("open"); loadAdmin(); }
function closeM(){ var modals=document.querySelectorAll(".modal"); for(var i=0;i<modals.length;i++) modals[i].classList.remove("open"); }
function toggleAI(){ document.getElementById("aiChat").classList.toggle("open"); }
function toggleDark(){ isDark=!isDark; document.body.classList.toggle("dark",isDark); localStorage.setItem("dark",isDark); showToast(isDark?"Dark mode on 🌙":"Light mode on ☀️"); }
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
   var quickHtml = "";
   if(d.quick && d.quick.length>0){
     quickHtml = '<div class="quick">';
     for(var i=0;i<d.quick.length;i++){ quickHtml += '<button onclick="askQuick(\\''+d.quick[i]+'\\')">'+d.quick[i]+'</button>'; }
     quickHtml += '</div>';
   }
   box.innerHTML+='<div class="m b">'+d.reply+quickHtml+'</div>';
 } catch(e){
   box.innerHTML+='<div class="m b">Sorry, error. Try again. Error: '+e+'</div>';
 }
 box.scrollTop=box.scrollHeight;
}
function askQuick(text){ document.getElementById("aiInput").value=text; sendAI(); }
async function checkout(){
 var phone=document.getElementById("custPhone").value; var loc=document.getElementById("custLoc").value;
 if(!loc){ alert("Enter location"); return; }
 document.getElementById("status").innerText="Placing order...";
 var r=await fetch("/mpesa/stkpush",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone,amount:total+100,location:loc,cart:cart})});
 var d=await r.json(); document.getElementById("orderId").innerText=d.order_id; document.getElementById("status").innerText="Order placed!"; document.getElementById("track").style.display="block"; document.getElementById("riderInfo").innerText="Rider John KMEZ 123A • 4.9 stars • 30min"; cart=[]; total=0; document.getElementById("cartDot").innerText=0;
}
async function loadRiders(){
 var r=await fetch("/riders"); var riders=await r.json();
 var html=""; for(var i=0;i<riders.length;i++){ var rd=riders[i]; html+='<div style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:12px;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><div><b>'+rd.name+' ⭐'+rd.rating+'</b><br><small style="color:var(--muted)">'+rd.motor+' • '+rd.location+'</small></div><div style="padding:6px 10px;border-radius:10px;background:'+(rd.status==="available"?"#d4edda":"#fff3cd")+';color:#000;font-size:10px;font-weight:800">'+rd.status+'</div></div>'; }
 document.getElementById("riderList").innerHTML=html;
 var ro=await fetch("/orders"); var orders=await ro.json();
 document.getElementById("rs2").innerText=orders.length; document.getElementById("rs3").innerText="KES "+orders.reduce(function(s,o){return s+o.amount},0);
 var oh='<h4 style="margin:12px 0 8px;font-size:12px">Active Orders</h4>'; for(var j=0;j<Math.min(orders.length,5);j++){ var o=orders[j]; oh+='<div style="background:var(--card);border:1px solid var(--border);border-radius:14px;padding:10px;display:flex;justify-content:space-between;align-items:center;margin-bottom:6px"><div><b>'+o.id+'</b> KES '+o.amount+'<br><small>'+o.location+'</small></div><button onclick="acceptOrder(\\''+o.id+'\\')" style="padding:8px 12px;background:#00a651;color:#fff;border:none;border-radius:10px;font-size:11px;font-weight:800">Accept</button></div>'; }
 document.getElementById("riderOrders").innerHTML=oh;
}
async function loadAdmin(){
 var r=await fetch("/orders"); var o=await r.json();
 document.getElementById("adminStats").innerHTML='<div style="background:var(--card);border:1px solid var(--border);padding:16px;border-radius:16px;text-align:center"><b style="font-size:22px">'+o.length+'</b><br><small>Orders</small></div><div style="background:var(--card);border:1px solid var(--border);padding:16px;border-radius:16px;text-align:center"><b style="font-size:22px">KES '+o.reduce(function(s,x){return s+x.amount},0)+'</b><br><small>Revenue</small></div>';
 var html=""; for(var i=0;i<Math.min(o.length,8);i++){ var x=o[i]; html+='<div style="background:var(--card);border:1px solid var(--border);border-radius:14px;padding:10px;margin-bottom:6px"><b>'+x.id+'</b> - '+x.status+'<br><small>'+x.location+' • KES '+x.amount+'</small></div>'; }
 document.getElementById("adminOrders").innerHTML=html;
}
async function acceptOrder(id){ await fetch("/rider/accept/"+id,{method:"POST"}); showToast("Accepted "+id); loadRiders(); }
function showToast(t){ var el=document.getElementById("toast"); el.innerText=t; el.style.display="block"; setTimeout(function(){el.style.display="none"},2500); }

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
        reply = smart_ai_reply(msg, cart_count)

        # Quick reply suggestions based on message
        quick = []
        low = msg.lower()
        if "deliver" in low or "bring" in low:
            quick = ["Yes bring it on", "Where do you deliver?", "Delivery fee?"]
        elif "flour" in low:
            quick = ["Add flour to cart", "Milk price?", "Cheapest rice?"]
        elif "help" in low:
            quick = ["Will you deliver?", "Cheapest flour", "How to order?"]
        elif "hello" in low or "hi" in low:
            quick = ["Help me", "Cheapest flour", "Will you deliver?"]
        else:
            quick = ["Help me", "Will you deliver?", "Cheapest flour"]

        return {"reply": reply, "quick": quick}
    except Exception as e:
        return {"reply": f"I understood: {b.get('message','')} - I can help with delivery, prices, and ordering. Try 'Help me' or 'Will you deliver?'", "quick": ["Help me", "Will you deliver?"]}

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
        d=r.json(); d["order_id"]=oid; return d
    except Exception as e:
        return {"ResponseCode":"1","error":str(e),"order_id":f"ORD{random.randint(1000,9999)}"}

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
async def logo():
    if os.path.exists("logo.png"): return FileResponse("logo.png")
    return HTMLResponse("", status_code=404)
@app.get("/favicon.ico")
async def fav():
    if os.path.exists("logo.png"): return FileResponse("logo.png")
    return HTMLResponse("", status_code=404)
