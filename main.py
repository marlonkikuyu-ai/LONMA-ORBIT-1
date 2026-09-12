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

BRANDS = [
    {"name":"LONMA ORIGINALS","desc":"Signature Collection","img":"https://via.placeholder.com/300x200/0A8EA8/fff?text=ORIGINALS"},
    {"name":"ORBIT STREET","desc":"Street Culture","img":"https://via.placeholder.com/300x200/000/fff?text=ORBIT+STREET"},
    {"name":"ESSENTIALS","desc":"Everyday Wear","img":"https://via.placeholder.com/300x200/222/fff?text=ESSENTIALS"},
    {"name":"LONMA LUXE","desc":"Premium Drop","img":"https://via.placeholder.com/300x200/0A8EA8/fff?text=LUXE"},
]

PRODUCTS=[
    {"id":1,"name":"LONMA Orbit Tee - Black","price":1500,"brand":"LONMA ORIGINALS","image":"https://via.placeholder.com/400/000/fff?text=Tee+Black"},
    {"id":2,"name":"LONMA Orbit Tee - White","price":1500,"brand":"LONMA ORIGINALS","image":"https://via.placeholder.com/400/fff/000?text=Tee+White"},
    {"id":3,"name":"LONMA Street Hoodie","price":3500,"brand":"ORBIT STREET","image":"https://via.placeholder.com/400/111/fff?text=Hoodie"},
    {"id":4,"name":"LONMA Essentials Cap","price":800,"brand":"ESSENTIALS","image":"https://via.placeholder.com/400/0A8EA8/fff?text=Cap"},
    {"id":5,"name":"LONMA Cargo Pants","price":2800,"brand":"ORBIT STREET","image":"https://via.placeholder.com/400/333/fff?text=Cargo"},
    {"id":6,"name":"LONMA Luxe Jacket","price":5500,"brand":"LONMA LUXE","image":"https://via.placeholder.com/400/0A8EA8/fff?text=Jacket"},
    {"id":7,"name":"LONMA Sneakers - Orbit 1","price":4500,"brand":"LONMA ORIGINALS","image":"https://via.placeholder.com/400/000/fff?text=Sneakers"},
    {"id":8,"name":"LONMA Tote Bag","price":1200,"brand":"ESSENTIALS","image":"https://via.placeholder.com/400/eee/000?text=Tote"},
]

@app.get("/", response_class=HTMLResponse)
async def home():
    brand_cards="".join([f'<div class="brand-card" onclick="filterBrand(\'{b["name"]}\')"><img src="{b["img"]}"><div class="brand-info"><h3>{b["name"]}</h3><p>{b["desc"]}</p></div></div>' for b in BRANDS])
    prod_cards="".join([f'<div class="product-card" data-brand="{p["brand"]}"><img src="{p["image"]}"><span class="badge">{p["brand"]}</span><h4>{p["name"]}</h4><p class="price">KSH {p["price"]}</p><button onclick="buy({p["id"]},{p["price"]},\'{p["name"]}\')">Buy Now</button></div>' for p in PRODUCTS])
    return f'''
<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{font-family:Inter,Arial;background:#f8f9fa;color:#111}}
header{{background:#0A8EA8;padding:14px;display:flex;justify-content:center;align-items:center;position:sticky;top:0;z-index:100;box-shadow:0 2px 10px rgba(0,0,0,0.1)}}
header img{{height:68px;width:auto}}
.hero{{background:linear-gradient(135deg,#0A8EA8 0%,#065a6b 100%);color:#fff;padding:40px 20px;text-align:center}}
.hero h1{{font-size:32px;font-weight:900;letter-spacing:3px;margin-bottom:10px}} .hero p{{opacity:0.9;margin-bottom:20px}}
.hero button{{padding:14px 28px;background:#fff;color:#0A8EA8;border:none;border-radius:30px;font-weight:900;letter-spacing:1px;cursor:pointer}}
.section{{padding:25px 15px;max-width:1200px;margin:auto}} .section h2{{font-size:22px;font-weight:900;margin-bottom:15px;letter-spacing:1px}}
.brands-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:15px}}
.brand-card{{position:relative;border-radius:16px;overflow:hidden;cursor:pointer;height:180px;box-shadow:0 4px 12px rgba(0,0,0,0.15)}} .brand-card img{{width:100%;height:100%;object-fit:cover}}
.brand-info{{position:absolute;bottom:0;left:0;right:0;background:linear-gradient(transparent,rgba(0,0,0,0.8));color:#fff;padding:15px}} .brand-info h3{{font-size:16px;font-weight:900}} .brand-info p{{font-size:12px;opacity:0.8}}
.filter-bar{{display:flex;gap:8px;overflow-x:auto;padding:10px 0;margin-bottom:15px}} .filter-btn{{padding:8px 16px;border-radius:20px;border:1px solid #ddd;background:#fff;white-space:nowrap;cursor:pointer;font-weight:700}} .filter-btn.active{{background:#0A8EA8;color:#fff;border-color:#0A8EA8}}
.products-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}}
.product-card{{background:#fff;border-radius:14px;padding:10px;position:relative;box-shadow:0 2px 8px rgba(0,0,0,0.06)}} .product-card img{{width:100%;border-radius:10px;aspect-ratio:1;object-fit:cover}} .badge{{position:absolute;top:16px;left:16px;background:#0A8EA8;color:#fff;font-size:9px;padding:4px 8px;border-radius:10px;font-weight:900}} .product-card h4{{font-size:13px;margin:8px 0 4px;height:32px;overflow:hidden}} .price{{font-weight:900;color:#0A8EA8;margin-bottom:8px}} .product-card button{{width:100%;padding:10px;background:#000;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer}}
footer{{background:#000;color:#fff;padding:30px 20px;text-align:center;margin-top:30px}} footer img{{height:60px;margin-bottom:15px}} .social{{display:flex;justify-content:center;gap:15px;margin-top:15px}} .social a{{color:#0A8EA8;text-decoration:none;font-weight:700}}
.modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);justify-content:center;align-items:center;z-index:200}} .box{{background:#fff;padding:22px;border-radius:16px;width:90%;max-width:380px}} input{{width:100%;padding:13px;margin:10px 0;border-radius:10px;border:1px solid #ddd}}
</style></head><body>
<header><img src="/logo.png" alt="LONMA ORBIT"></header>
<div class="hero"><h1>LONMA ORBIT</h1><p>Future of Street Culture • Nairobi to the World</p><button onclick="document.getElementById('brands').scrollIntoView({{behavior:'smooth'}})">SHOP COLLECTIONS</button></div>

<div class="section" id="brands"><h2>SHOP BY BRAND</h2><div class="brands-grid">{brand_cards}</div></div>

<div class="section"><h2>FEATURED PRODUCTS</h2>
<div class="filter-bar">
<button class="filter-btn active" onclick="filterBrand('ALL')">All</button>
<button class="filter-btn" onclick="filterBrand('LONMA ORIGINALS')">Originals</button>
<button class="filter-btn" onclick="filterBrand('ORBIT STREET')">Street</button>
<button class="filter-btn" onclick="filterBrand('ESSENTIALS')">Essentials</button>
<button class="filter-btn" onclick="filterBrand('LONMA LUXE')">Luxe</button>
</div>
<div class="products-grid" id="products">{prod_cards}</div>
</div>

<footer><img src="/logo.png"><p style="font-weight:900;letter-spacing:2px">LONMA ORBIT</p><p style="opacity:0.6;font-size:13px;margin-top:8px">© 2026 LONMA ORBIT KE • Built in Kajiado</p><div class="social"><a href="#">Instagram</a><a href="#">TikTok</a><a href="#">WhatsApp</a></div></footer>

<div id="m" class="modal"><div class="box"><h3 id="pn"></h3><p id="pp" style="color:#0A8EA8;font-weight:900"></p><input id="phone" value="254" placeholder="2547..."><button onclick="pay()" style="width:100%;padding:14px;background:#00a651;color:#fff;border:none;border-radius:10px;font-weight:900;margin-top:10px">Lipa na M-Pesa</button><button onclick="document.getElementById('m').style.display='none'" style="width:100%;margin-top:8px;padding:12px;background:#eee;border:none;border-radius:10px">Cancel</button><p id="st" style="text-align:center;font-weight:700;margin-top:10px"></p></div></div>

<script>
let pr;
function buy(id,price,name){{pr=price;document.getElementById('pn').innerText=name;document.getElementById('pp').innerText='KSH '+price;document.getElementById('m').style.display='flex'}}
async function pay(){{let ph=document.getElementById('phone').value;document.getElementById('st').innerText='Sending...';let r=await fetch('/mpesa/stkpush',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{phone:ph,amount:pr}})}});let d=await r.json();document.getElementById('st').innerText=d.error?d.error:(d.ResponseCode=='0'?'✅ Check phone to pay!':'Error '+JSON.stringify(d))}}
function filterBrand(brand){{document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));event.target.classList.add('active');document.querySelectorAll('.product-card').forEach(card=>{{if(brand=='ALL' || card.dataset.brand==brand) card.style.display='block'; else card.style.display='none'}});if(brand!='ALL') document.getElementById('products').scrollIntoView({{behavior:'smooth'}})}}
</script>
</body></html>
'''

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    try:
        b=await req.json();token=get_token()
        if not token: return {"error":"M-Pesa keys not set in Render > Environment","ResponseCode":"1"}
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
async def logo(): return FileResponse("logo.png") if os.path.exists("logo.png") else {"error":"logo.png missing"}
@app.get("/favicon.ico")
async def fav(): return FileResponse("logo.png") if os.path.exists("logo.png") else {}
@app.get("/products")
async def prods(): return PRODUCTS
@app.get("/brands")
async def brands(): return BRANDS
