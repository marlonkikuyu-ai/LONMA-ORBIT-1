from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os, base64, requests
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://app.lonmaorbit.co.ke/mpesa/callback")
MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")

# YOUR COLORED LOGO - replace with new Imgur direct link after upload
LOGO_URL = "https://i.imgur.com/soyzxqH.jpg"

def get_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" if MPESA_ENV == "sandbox" else "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return r.json().get("access_token")

PRODUCTS = [
    {"id":1,"name":"LONMA T-Shirt","price":1500,"image":"https://via.placeholder.com/400?text=T-Shirt"},
    {"id":2,"name":"LONMA Hoodie","price":3500,"image":"https://via.placeholder.com/400?text=Hoodie"},
    {"id":3,"name":"LONMA Cap","price":800,"image":"https://via.placeholder.com/400?text=Cap"},
    {"id":4,"name":"LONMA Sneakers","price":4500,"image":"https://via.placeholder.com/400?text=Sneakers"},
]

@app.get("/", response_class=HTMLResponse)
async def home():
    cards="".join([f'<div class="card"><img src="{p["image"]}"><h3>{p["name"]}</h3><p>KSH {p["price"]}</p><button onclick="buy({p["id"]},{p["price"]},\'{p["name"]}\')">Buy Now</button></div>' for p in PRODUCTS])
    return f"""
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT</title>
    <style>
    body{{margin:0;font-family:Arial;background:#f5f5f5}}
    header{{background:#0A8EA8;color:#fff;padding:8px 16px;display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:10}}
    header img{{width:70px;height:70px;object-fit:contain;border-radius:8px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;padding:15px}}
    .card{{background:#fff;border-radius:12px;padding:12px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,0.1)}}
    .card img{{width:100%;border-radius:8px}} .card button{{width:100%;padding:12px;background:#0A8EA8;color:#fff;border:none;border-radius:8px;font-weight:bold;cursor:pointer}}
    .modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);justify-content:center;align-items:center;z-index:20}}
    .box{{background:#fff;padding:20px;border-radius:12px;width:90%;max-width:360px}}
    input{{width:100%;padding:12px;margin:10px 0;border-radius:8px;border:1px solid #ccc;box-sizing:border-box}}
    </style></head>
    <body>
    <header><img src="{LOGO_URL}"><div style="font-weight:900;font-size:20px;letter-spacing:2px">LONMA ORBIT</div></header>
    <div class="grid">{cards}</div>
    <div id="m" class="modal"><div class="box"><h3 id="pn"></h3><p id="pp"></p><input id="phone" value="254"><button onclick="pay()" style="width:100%;padding:13px;background:#0A8EA8;color:#fff;border:none;border-radius:8px;font-weight:bold">Lipa na M-Pesa</button><button onclick="document.getElementById('m').style.display='none'" style="width:100%;margin-top:8px;padding:10px;background:#eee;border:none;border-radius:8px">Cancel</button><p id="st" style="text-align:center;font-weight:bold"></p></div></div>
    <script>
    let pr;function buy(id,price,name){{pr=price;document.getElementById('pn').innerText=name;document.getElementById('pp').innerText='KSH '+price;document.getElementById('m').style.display='flex'}}
    async function pay(){{let ph=document.getElementById('phone').value;document.getElementById('st').innerText='Sending...';let r=await fetch('/mpesa/stkpush',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{phone:ph,amount:pr}})}});let d=await r.json();document.getElementById('st').innerText=d.ResponseCode=='0'?'✅ Check phone!':'Error '+JSON.stringify(d)}}
    </script></body></html>
    """

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    b=await req.json();token=get_token();ts=datetime.now().strftime("%Y%m%d%H%M%S");pwd=base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{ts}".encode()).decode();url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest";r=requests.post(url,json={{"BusinessShortCode":MPESA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":b.get("amount"),"PartyA":b.get("phone"),"PartyB":MPESA_SHORTCODE,"PhoneNumber":b.get("phone"),"CallBackURL":MPESA_CALLBACK_URL,"AccountReference":"LONMA","TransactionDesc":"LONMA"}},headers={{"Authorization":f"Bearer {{token}}"}});return r.json()

@app.get("/mpesa/callback")
async def cb_get(): return {{"ResultCode":0,"ResultDesc":"OK"}}
@app.post("/mpesa/callback")
async def cb_post(req: Request):
    print(await req.json());return {{"ResultCode":0,"ResultDesc":"Accepted"}}
@app.get("/favicon.ico")
async def fav(): return {{}}
@app.get("/products")
async def prods(): return PRODUCTS
