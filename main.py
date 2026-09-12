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
LOGO_URL = "https://i.imgur.com/soyzxqH.png"

def get_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" if MPESA_ENV == "sandbox" else "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return r.json().get("access_token")

PRODUCTS = [
    {"id": 1, "name": "LONMA T-Shirt", "price": 1500, "image": "https://via.placeholder.com/300?text=T-Shirt"},
    {"id": 2, "name": "LONMA Hoodie", "price": 3500, "image": "https://via.placeholder.com/300?text=Hoodie"},
    {"id": 3, "name": "LONMA Cap", "price": 800, "image": "https://via.placeholder.com/300?text=Cap"},
]

@app.get("/", response_class=HTMLResponse)
async def home():
    html_products = "".join([f"""
    <div class="card">
        <img src="{p['image']}">
        <h3>{p['name']}</h3>
        <p>KSH {p['price']}</p>
        <button onclick="buy({p['id']},{p['price']},'{p['name']}')">Buy Now</button>
    </div>""" for p in PRODUCTS])

    return f"""
    <html>
    <head><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>LONMA ORBIT</title>
    <style>
    body{{margin:0;font-family:Arial;background:#f5f5f5}}
    header{{background:#000;color:#fff;padding:10px 20px;display:flex;align-items:center;gap:12px;position:sticky;top:0}}
    header img{{width:45px;height:45px;border-radius:50%;background:#fff;object-fit:contain;padding:2px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:15px;padding:20px}}
    .card{{background:#fff;border-radius:12px;padding:12px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,0.1)}}
    .card img{{width:100%;border-radius:8px}}
    .card button{{background:#000;color:#fff;border:none;width:100%;padding:10px;border-radius:8px;margin-top:8px;font-weight:bold}}
    .modal{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);justify-content:center;align-items:center}}
    .box{{background:#fff;padding:20px;border-radius:12px;width:90%;max-width:350px}}
    input{{width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:8px;box-sizing:border-box}}
    </style></head>
    <body>
    <header>
        <img src="{LOGO_URL}" onerror="this.src='https://via.placeholder.com/45?text=LO'">
        <b style="font-size:20px;letter-spacing:1px">LONMA ORBIT</b>
    </header>
    <div class="grid">{html_products}</div>
    <div id="m" class="modal"><div class="box">
        <h3 id="pn"></h3><p id="pp"></p>
        <input id="phone" value="254" placeholder="2547XXXXXXX">
        <button onclick="pay()" style="width:100%;padding:12px;background:#00b14f;color:#fff;border:none;border-radius:8px;font-weight:bold">Pay with M-Pesa</button>
        <button onclick="document.getElementById('m').style.display='none'" style="width:100%;margin-top:8px;padding:10px;background:#ddd;border:none;border-radius:8px">Cancel</button>
        <p id="st"></p>
    </div></div>
    <script>
    let pr, pid
    function buy(id,price,name){{pid=id;pr=price;document.getElementById('pn').innerText=name;document.getElementById('pp').innerText='KSH '+price;document.getElementById('m').style.display='flex';}}
    async function pay(){{
        let ph=document.getElementById('phone').value
        document.getElementById('st').innerText='Sending STK...'
        let r=await fetch('/mpesa/stkpush',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{phone:ph,amount:pr}})}})
        let d=await r.json()
        if(d.ResponseCode=='0'){{document.getElementById('st').innerText='✅ Check phone, enter PIN'}}
        else{{document.getElementById('st').innerText='Error: '+JSON.stringify(d)}}
    }}
    </script>
    </body></html>
    """

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    b=await req.json()
    token=get_token()
    ts=datetime.now().strftime("%Y%m%d%H%M%S")
    pwd=base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{ts}".encode()).decode()
    url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    payload={{"BusinessShortCode":MPESA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":b.get("amount",1),"PartyA":b.get("phone"),"PartyB":MPESA_SHORTCODE,"PhoneNumber":b.get("phone"),"CallBackURL":MPESA_CALLBACK_URL,"AccountReference":"LONMA","TransactionDesc":"Payment"}}
    r=requests.post(url,json=payload,headers={{"Authorization":f"Bearer {{token}}"}})
    return r.json()

@app.get("/mpesa/callback")
async def cb_get(): return {{"ResultCode":0,"ResultDesc":"OK"}}
@app.post("/mpesa/callback")
async def cb_post(req: Request):
    d=await req.json()
    print(d)
    return {{"ResultCode":0,"ResultDesc":"Accepted"}}
@app.get("/favicon.ico")
async def fav(): return {{}}
