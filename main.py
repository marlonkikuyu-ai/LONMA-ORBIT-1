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
    {"id": 1, "name": "LONMA T-Shirt", "price": 1500, "image": "https://via.placeholder.com/300x300?text=T-Shirt"},
    {"id": 2, "name": "LONMA Hoodie", "price": 3500, "image": "https://via.placeholder.com/300x300?text=Hoodie"},
    {"id": 3, "name": "LONMA Cap", "price": 800, "image": "https://via.placeholder.com/300x300?text=Cap"},
    {"id": 4, "name": "LONMA Sneakers", "price": 4500, "image": "https://via.placeholder.com/300x300?text=Sneakers"},
]

@app.get("/", response_class=HTMLResponse)
async def home():
    products_html = ""
    for p in PRODUCTS:
        products_html += f"""
        <div class="card">
            <img src="{p['image']}">
            <h3>{p['name']}</h3>
            <p>KSH {p['price']}</p>
            <button onclick="buy({p['id']}, {p['price']}, '{p['name']}')">Buy Now</button>
        </div>
        """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>LONMA ORBIT</title>
        <style>
            body{{font-family:Arial;margin:0;background:#f5f5f5}}
            header{{background:#000;color:#fff;padding:15px;text-align:center;font-size:22px;font-weight:bold}}
            .container{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;padding:20px}}
            .card{{background:#fff;border-radius:12px;padding:15px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
            .card img{{width:100%;border-radius:8px}}
            .card button{{background:#000;color:#fff;border:none;padding:12px 20px;border-radius:8px;width:100%;margin-top:10px;cursor:pointer;font-weight:bold}}
            .modal{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);justify-content:center;align-items:center}}
            .modal-content{{background:#fff;padding:25px;border-radius:12px;width:90%;max-width:400px}}
            input{{width:100%;padding:12px;margin:10px 0;border:1px solid #ccc;border-radius:8px;box-sizing:border-box}}
            #payBtn{{background:#00a651;color:#fff}}
        </style>
    </head>
    <body>
        <header>LONMA ORBIT - Official Store</header>
        <div class="container">{products_html}</div>
        <div id="modal" class="modal">
            <div class="modal-content">
                <h2 id="pname"></h2>
                <p id="pprice"></p>
                <input id="phone" placeholder="Phone 2547XXXXXXXX" value="254">
                <button id="payBtn" onclick="pay()">Pay with M-Pesa</button>
                <button onclick="closeModal()" style="background:#ccc;margin-top:8px">Cancel</button>
                <p id="status" style="margin-top:15px;font-weight:bold"></p>
            </div>
        </div>
        <script>
            let selId, selPrice
            function buy(id, price, name) {{
                selId=id; selPrice=price;
                document.getElementById('pname').innerText=name;
                document.getElementById('pprice').innerText='KSH '+price;
                document.getElementById('modal').style.display='flex';
                document.getElementById('status').innerText='';
            }}
            function closeModal(){{document.getElementById('modal').style.display='none'}}
            async function pay(){{
                const phone=document.getElementById('phone').value;
                const status=document.getElementById('status');
                status.innerText='Sending STK Push...';
                const res=await fetch('/mpesa/stkpush', {{
                    method:'POST',
                    headers:{{'Content-Type':'application/json'}},
                    body: JSON.stringify({{phone: phone, amount: selPrice, product_id: selId}})
                }});
                const data=await res.json();
                console.log(data);
                if(data.ResponseCode=='0' || data.ResponseCode==0) {{
                    status.innerText='✅ Check your phone! Enter M-Pesa PIN';
                }} else {{
                    status.innerText='Error: '+(data.errorMessage||JSON.stringify(data));
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.get("/products")
async def get_products():
    return PRODUCTS

@app.post("/mpesa/stkpush")
async def stk_push(request: Request):
    body = await request.json()
    phone = body.get("phone")
    amount = body.get("amount", 1)
    token = get_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if MPESA_ENV == "sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": "LONMA",
        "TransactionDesc": "LONMA Payment"
    }
    res = requests.post(url, json=payload, headers=headers)
    return res.json()

@app.get("/mpesa/callback")
async def callback_get():
    return {"ResultCode": 0, "ResultDesc": "OK"}

@app.post("/mpesa/callback")
async def callback_post(request: Request):
    data = await request.json()
    print("CALLBACK:", data)
    return {"ResultCode": 0, "ResultDesc": "Accepted"}

@app.get("/favicon.ico")
async def favicon():
    return {}
