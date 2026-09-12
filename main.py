from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, base64, requests
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
    {"id":"naivas","name":"NAIVAS","color":"#008000","logo":"https://via.placeholder.com/100/008000/fff?text=N"},
    {"id":"quickmart","name":"QUICKMART","color":"#FF0000","logo":"https://via.placeholder.com/100/FF0000/fff?text=Q"},
    {"id":"carrefour","name":"CARREFOUR","color":"#0047AB","logo":"https://via.placeholder.com/100/0047AB/fff?text=C"},
    {"id":"chandarana","name":"CHANDARANA","color":"#FF8C00","logo":"https://via.placeholder.com/100/FF8C00/fff?text=CH"},
    {"id":"magunas","name":"MAGUNAS","color":"#800080","logo":"https://via.placeholder.com/100/800080/fff?text=M"},
]

CATEGORIES = [
    {"id":"fresh","name":"Fresh Food","icon":"🥬","items":"Vegetables, Fruits, Meat"},
    {"id":"grocery","name":"Grocery","icon":"🛒","items":"Flour, Rice, Cooking Oil"},
    {"id":"beverages","name":"Beverages","icon":"🥤","items":"Soda, Juice, Water"},
    {"id":"dairy","name":"Dairy & Bakery","icon":"🥛","items":"Milk, Bread, Eggs"},
    {"id":"household","name":"Household","icon":"🧹","items":"Detergent, Tissue"},
    {"id":"personal","name":"Personal Care","icon":"🧴","items":"Soap, Lotion, Pads"},
]

PRODUCTS=[
    {"id":1,"name":"Ajab Maize Flour 2kg","price":175,"store":"naivas","category":"grocery","image":"https://via.placeholder.com/300/f0f0f0/000?text=Maize+Flour"},
    {"id":2,"name":"Ajab Maize Flour 2kg","price":180,"store":"quickmart","category":"grocery","image":"https://via.placeholder.com/300/f0f0f0/000?text=Maize+Flour"},
    {"id":3,"name":"Ajab Maize Flour 2kg","price":172,"store":"carrefour","category":"grocery","image":"https://via.placeholder.com/300/f0f0f0/000?text=Maize+Flour"},
    {"id":4,"name":"Brookside Milk 500ml","price":65,"store":"naivas","category":"dairy","image":"https://via.placeholder.com/300/fff/000?text=Milk"},
    {"id":5,"name":"Brookside Milk 500ml","price":62,"store":"chandarana","category":"dairy","image":"https://via.placeholder.com/300/fff/000?text=Milk"},
    {"id":6,"name":"Coca Cola 1.25L","price":100,"store":"quickmart","category":"beverages","image":"https://via.placeholder.com/300/FF0000/fff?text=Coke"},
    {"id":7,"name":"Coca Cola 1.25L","price":99,"store":"magunas","category":"beverages","image":"https://via.placeholder.com/300/FF0000/fff?text=Coke"},
    {"id":8,"name":"Omo Detergent 1kg","price":285,"store":"carrefour","category":"household","image":"https://via.placeholder.com/300/0047AB/fff?text=Omo"},
    {"id":9,"name":"Omo Detergent 1kg","price":290,"store":"naivas","category":"household","image":"https://via.placeholder.com/300/0047AB/fff?text=Omo"},
    {"id":10,"name":"Tomatoes 1kg","price":80,"store":"quickmart","category":"fresh","image":"https://via.placeholder.com/300/008000/fff?text=Tomatoes"},
    {"id":11,"name":"White Bread 400g","price":60,"store":"naivas","category":"dairy","image":"https://via.placeholder.com/300/FFD700/000?text=Bread"},
    {"id":12,"name":"Geisha Soap","price":55,"store":"magunas","category":"personal","image":"https://via.placeholder.com/300/FF69B4/fff?text=Geisha"},
]

@app.get("/", response_class=HTMLResponse)
async def home():
    store_tabs="".join([f'<button class="store-tab" data-store="{s["id"]}" style="border-color:{s["color"]}" onclick="filterStore(\'{s["id"]}\')"><span style="background:{s["color"]}">{s["name"][0]}</span>{s["name"]}</button>' for s in STORES])
    cat_cards="".join([f'<div class="cat-card" onclick="filterCat(\'{c["id"]}\')"><div class="cat-icon">{c["icon"]}</div><h4>{c["name"]}</h4><p>{c["items"]}</p></div>' for c in CATEGORIES])
    prod_cards="".join([f'<div class="prod-card" data-store="{p["store"]}" data-cat="{p["category"]}"><img src="{p["image"]}"><div class="store-badge {p["store"]}">{p["store"].upper()}</div><h4>{p["name"]}</h4><div class="price-row"><span class="price">KSH {p["price"]}</span><button onclick="buy({p["id"]},{p["price"]},\'{p["name"]}\')">Add</button></div></div>' for p in PRODUCTS])
    return f'''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT - Supermarket</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{font-family:Arial;background:#f5f6fa}}
header{{background:#0A8EA8;padding:10px 15px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100}} header img{{height:55px}}.cart{{background:#fff;color:#0A8EA8;padding:8px 14px;border-radius:20px;font-weight:900;font-size:13px}}
.hero{{background:#fff;padding:20px 15px;border-bottom:1px solid #eee}}.hero h1{{font-size:20px;font-weight:900}}.hero p{{font-size:13px;color:#666;margin-top:4px}}
.search{{margin-top:12px;display:flex;gap:8px}}.search input{{flex:1;padding:12px 15px;border-radius:25px;border:1px solid #ddd;background:#f5f6fa}}.search button{{padding:12px 18px;background:#0A8EA8;color:#fff;border:none;border-radius:25px;font-weight:900}}
.store-tabs{{display:flex;gap:8px;overflow-x:auto;padding:12px 15px;background:#fff;border-bottom:1px solid #eee}}.store-tab{{display:flex;align-items:center;gap:6px;padding:6px 12px 6px 6px;border:2px solid #ddd;border-radius:25px;background:#fff;white-space:nowrap;font-weight:900;font-size:12px;cursor:pointer}}.store-tab span{{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900}}.store-tab.active{{background:#000;color:#fff}}
.section{{padding:15px}}.section h3{{font-size:16px;font-weight:900;margin-bottom:12px}}
.cat-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}.cat-card{{background:#fff;border-radius:14px;padding:14px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,0.05);cursor:pointer}}.cat-icon{{font-size:28px;margin-bottom:6px}}.cat-card h4{{font-size:12px;font-weight:900}}.cat-card p{{font-size:10px;color:#888;margin-top:3px}}
.prod-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}.prod-card{{background:#fff;border-radius:14px;padding:8px;position:relative;box-shadow:0 2px 6px rgba(0,0,0,0.05)}}.prod-card img{{width:100%;border-radius:10px;aspect-ratio:1;object-fit:cover}}.store-badge{{position:absolute;top:12px;left:12px;font-size:9px;padding:4px 8px;border-radius:10px;font-weight:900;color:#fff}}.naivas{{background:#008000}}.quickmart{{background:#FF0000}}.carrefour{{background:#0047AB}}.chandarana{{background:#FF8C00}}.magunas{{background:#800080}}
.prod-card h4{{font-size:12px;margin:8px 0;height:28px;overflow:hidden}}.price-row{{display:flex;justify-content:space-between;align-items:center;margin-top:6px}}.price{{font-weight:900;color:#0A8EA8;font-size:13px}}.price-row button{{padding:6px 12px;background:#000;color:#fff;border:none;border-radius:15px;font-weight:700;font-size:11px}}
footer{{background:#000;color:#fff;padding:20px;text-align:center;margin-top:20px}} footer img{{height:50px}}
.modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);justify-content:center;align-items:center;z-index:200}}.box{{background:#fff;padding:20px;border-radius:16px;width:90%;max-width:380px}}.box input{{width:100%;padding:12px;margin:10px 0;border-radius:10px;border:1px solid #ddd}}
</style></head><body>
<header><img src="/logo.png"><div class="cart">🛒 <span id="cartCount">0</span></div></header>
<div class="hero"><h1>Compare Prices • Save Money</h1><p>Naivas | Quickmart | Carrefour | Chandarana | Magunas</p><div class="search"><input id="search" placeholder="Search flour, milk, bread..." onkeyup="searchProd()"><button onclick="searchProd()">Search</button></div></div>
<div class="store-tabs"><button class="store-tab active" onclick="filterStore('ALL')"><span style="background:#000">A</span>ALL STORES</button>{store_tabs}</div>
<div class="section"><h3>Categories</h3><div class="cat-grid">{cat_cards}</div></div>
<div class="section"><h3>Best Deals Today <span style="color:#0A8EA8">- Compare & Save</span></h3><div class="prod-grid" id="prodGrid">{prod_cards}</div></div>
<footer><img src="/logo.png"><p style="font-weight:900;letter-spacing:2px;font-size:13px">LONMA ORBIT SUPERMARKET</p><p style="font-size:11px;opacity:0.6;margin-top:5px">Kajiado • Nairobi • Kenya</p></footer>
<div id="m" class="modal"><div class="box"><h3 id="pn"></h3><p id="pp" style="color:#0A8EA8;font-weight:900"></p><input id="phone" value="254"><button onclick="pay()" style="width:100%;padding:13px;background:#00a651;color:#fff;border:none;border-radius:10px;font-weight:900;margin-top:8px">Lipa na M-Pesa</button><button onclick="document.getElementById('m').style.display='none'" style="width:100%;margin-top:8px;padding:10px;background:#eee;border:none;border-radius:10px">Cancel</button><p id="st" style="text-align:center;font-weight:700;margin-top:8px"></p></div></div>
<script>
let cart=0, pr;
function buy(id,price,name){{cart++;document.getElementById('cartCount').innerText=cart;pr=price;document.getElementById('pn').innerText=name;document.getElementById('pp').innerText='KSH '+price;document.getElementById('m').style.display='flex'}}
async function pay(){{let ph=document.getElementById('phone').value;document.getElementById('st').innerText='Sending...';let r=await fetch('/mpesa/stkpush',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{phone:ph,amount:pr}})}});let d=await r.json();document.getElementById('st').innerText=d.error?d.error:(d.ResponseCode=='0'?'✅ Check phone!':'Error '+JSON.stringify(d))}}
function filterStore(store){{document.querySelectorAll('.store-tab').forEach(b=>b.classList.remove('active'));event.currentTarget.classList.add('active');document.querySelectorAll('.prod-card').forEach(c=>{{if(store=='ALL'||c.dataset.store==store) c.style.display='block'; else c.style.display='none'}})}}
function filterCat(cat){{document.querySelectorAll('.prod-card').forEach(c=>{{if(c.dataset.cat==cat) c.style.display='block'; else c.style.display='none'}});window.scrollTo({{top:400,behavior:'smooth'}})}}
function searchProd(){{let q=document.getElementById('search').value.toLowerCase();document.querySelectorAll('.prod-card').forEach(c=>{{let name=c.querySelector('h4').innerText.toLowerCase(); c.style.display=name.includes(q)?'block':'none'}})}}
</script></body></html>
'''

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    try:
        b=await req.json();token=get_token()
        if not token: return {"error":"Set M-Pesa keys in Render Dashboard","ResponseCode":"1"}
        ts=datetime.now().strftime("%Y%m%d%H%M%S");pwd=base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{ts}".encode()).decode()
        url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        r=requests.post(url,json={"BusinessShortCode":MPESA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":int(b.get("amount",1)),"PartyA":b.get("phone"),"PartyB":MPESA_SHORTCODE,"PhoneNumber":b.get("phone"),"CallBackURL":MPESA_CALLBACK_URL,"AccountReference":"LONMA","TransactionDesc":"LONMA"},headers={"Authorization":f"Bearer {token}"},timeout=10)
        return r.json()
    except Exception as e: return {"error":str(e),"ResponseCode":"1"}

@app.get("/mpesa/callback")
async def cb_get(): return {"ResultCode":0,"ResultDesc":"OK"}
@app.post("/mpesa/callback")
async def cb_post(req: Request): print(await req.json());return {"ResultCode":0,"ResultDesc":"Accepted"}
@app.get("/logo.png")
async def logo(): return FileResponse("logo.png") if os.path.exists("logo.png") else {"error":"logo.png missing - upload logo.png to GitHub"}
@app.get("/favicon.ico")
async def fav(): return FileResponse("logo.png") if os.path.exists("logo.png") else {}
@app.get("/products")
async def prods(): return PRODUCTS
