from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
import requests
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://app.lonmaorbit.co.ke/mpesa/callback")
MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")

def get_mpesa_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" if MPESA_ENV == "sandbox" else "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return r.json().get("access_token")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html><body style="font-family:sans-serif;text-align:center;padding:50px">
    <h1>LONMA ORBIT - Live</h1>
    <a href="/products">View Products</a>
    </body></html>
    """

@app.get("/products")
async def products():
    return {"products": ["Product 1", "Product 2"]}

@app.post("/mpesa/stkpush")
async def stk_push(request: Request):
    body = await request.json()
    phone = body.get("phone")
    amount = body.get("amount", 1)
    token = get_mpesa_token()
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
async def mpesa_callback_get():
    return {"ResultCode": 0, "ResultDesc": "Callback GET OK - service live"}

@app.post("/mpesa/callback")
async def mpesa_callback_post(request: Request):
    try:
        data = await request.json()
        print("M-Pesa Callback:", data)
        return {"ResultCode": 0, "ResultDesc": "Accepted"}
    except Exception as e:
        print("Callback error:", e)
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

@app.get("/favicon.ico")
async def favicon():
    return {}
