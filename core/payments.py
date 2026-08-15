import httpx
import base64
from datetime import datetime
from core.config import settings

async def get_mpesa_token():
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = base64.b64encode(f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()).decode()
    async with httpx.AsyncClient() as client:
        r = await client.get(auth_url, headers={"Authorization": f"Basic {auth}"})
        r.raise_for_status()
        return r.json()["access_token"]

async def stk_push(order_id: str, phone: str, amount: int):
    token = await get_mpesa_token()
    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()).decode()
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": order_id,
        "TransactionDesc": "LONMA Order"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(stk_url, json=payload, headers={"Authorization": f"Bearer {token}"})
        return r.json()
