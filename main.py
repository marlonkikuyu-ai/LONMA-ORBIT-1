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

def get_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" if MPESA_ENV == "sandbox" else "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return r.json().get("access_token")

PRODUCTS = [
    {"id": 1, "name": "LONMA T-Shirt", "price": 1500, "image": "https://via.placeholder.com/400x400/000000/FFFFFF?text=T-Shirt"},
    {"id": 2, "name": "LONMA Hoodie", "price": 3500, "image": "https://via.placeholder.com/400x400/111111/FFFFFF?text=Hoodie"},
    {"id": 3, "name": "LONMA Cap", "price": 800, "image": "https://via.placeholder.com/400x400/222222/FFFFFF?text=Cap"},
    {"id": 4, "name": "LONMA Sneakers", "price": 4500, "image": "https://via.placeholder.com/400x400/000000/FFFFFF?text=Sneakers"},
]

@app.get("/", response_class=HTMLResponse)
async def home():
    cards = "".join([f"""
    <div class="card">
        <img src="{p['image']}">
        <h3>{p['name']}</h3>
        <p>KSH {p['price']}</p>
        <button onclick="buy({p['id']},{p['price']},'{p['name']}')">Buy Now</button>
    </div>""" for p in PRODUCTS])

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>LONMA ORBIT</title>
        <style>
            body{{margin:0;font-family:Arial;background:#f5f5f5}}
            header{{background:#000;color:#fff;padding:10px 20px;display:flex;align-items:center;gap:15px;position:sticky;top:0;z-index:100}}
            header .logo{{width:60px;height:60px;object-fit:contain;display:block}}
            header .brand{{font-size:22px;font-weight:bold;letter-spacing:2px}}
            .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;padding:20px}}
            .card{{background:#fff;border-radius:14px;padding:12px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.08)}}
            .card img{{width:100%;border-radius:10px}}
            .card h3{{margin:10px 0 5px}}
            .card button{{background:#000;color:#fff;border:none;width:100%;padding:12px;border-radius:10px;margin-top:8px;font-weight:bold;cursor:pointer}}
            .modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);justify-content:center;align-items:center;z-index:200}}
            .box{{background:#fff;padding:22px;border-radius:14px;width:90%;max-width:360px}}
            input{{width:100%;padding:13px;margin:10px 0;border:1px solid #ccc;border-radius:10px;box-sizing:border-box;font-size:16px}}
        </style>
    </head>
    <body>
        <header>
            <img class="logo" src="https://i.imgur.com/soyzxqH.jpg" alt="LONMA">
            <span class="brand">LONMA ORBIT</span>
        </header>

        <div class="grid">{cards}</div>

        <div id="m" class="modal">
            <div class="box">
                <h3 id="pn" style="margin:0"></h3>
                <p id="pp" style="color:#666"></p>
                <input id="phone" value="254" placeholder="2547XXXXXXXX">
                <button onclick="pay()" style="width:100%;padding:14px;background:#00b14f;color:#fff;border:none;border-radius:10px;font-weight:bold;font-size:16px">Lipa na M-Pesa</button>
                <button onclick="document.getElementById('m').style.display='none'" style="width:100%;margin-top:10px;padding:12px;background:#eee;border:none;border-radius:10px">Cancel</button>
                <p id="st" style="margin-top:12px;font-weight:bold;text-align:center"></p>
            </div>
        </div>

        <script>
            let selPrice, selId
            function buy(id,price,name){{
                selId=id; selPrice=price;
                document.getElementById('pn').innerText=name;
                document.getElementById('pp').innerText='KSH '+price;
                document.getElementById('m').style.display='flex';
                document.getElementById('st').innerText='';
            }}
            async function pay(){{
                const phone=document.getElementById('phone').value
                const st=document.getElementById('st')
                st.innerText='Sending STK Push...'
                const res=await fetch('/mpesa/stkpush',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{phone:phone,amount:selPrice}})}})
                const data=await res.json()
                if(data.ResponseCode=='0'){{st.innerText='✅ Check your phone! Enter M-Pesa PIN'}}
                else{{st.innerText='Error: '+(data.errorMessage||JSON.stringify(data))}}
            }}
        </script>
    </body>
    </html>
    """

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    body=await req.json()
    token=get_token()
    ts=datetime.now().strftime("%Y%m%d%H%M%S")
    pwd=base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{ts}".encode()).decode()
    url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if MPESA_ENV=="sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    payload={"BusinessShortCode":MPESA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":body.get("amount",1),"PartyA":body.get("phone"),"PartyB":MPESA_SHORTCODE,"PhoneNumber":body.get("phone"),"CallBackURL":MPESA_CALLBACK_URL,"AccountReference":"LONMA","TransactionDesc":"LONMA Payment"}
    r=requests.post(url,json=payload,headers={"Authorization":f"Bearer {token}"})
    return r.json()

@app.get("/mpesa/callback")
async def cb_get():
    return {"ResultCode":0,"ResultDesc":"OK"}

@app.post("/mpesa/callback")
async def cb_post(req: Request):
    data=await req.json()
    print(data)
    return {"ResultCode":0,"ResultDesc":"Accepted"}

@app.get("/favicon.ico")
async def fav():
    return {}

@app.get("/products")
async def prods():
    return PRODUCTS
