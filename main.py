from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests, base64, os
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OrderCreate(BaseModel):
    customer_name: str
    phone: str
    product_id: int
    quantity: int

class MpesaRequest(BaseModel):
    phone: str
    amount: int

class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    stock: int
    img: str = "📦"

products = [
    {"id": 1, "name": "Unga Ngano 2kg", "category": "Flour", "price": 180, "stock": 100, "img": "🌾"},
    {"id": 2, "name": "Fresh Milk 500ml", "category": "Dairy", "price": 65, "stock": 200, "img": "🥛"},
    {"id": 3, "name": "White Bread", "category": "Bakery", "price": 70, "stock": 80, "img": "🍞"},
    {"id": 4, "name": "Cooking Oil 1L", "category": "Cooking", "price": 280, "stock": 50, "img": "🫒"},
    {"id": 5, "name": "Sugar 1kg", "category": "Essentials", "price": 160, "stock": 120, "img": "🍬"},
    {"id": 6, "name": "Pishori Rice 2kg", "category": "Grains", "price": 350, "stock": 60, "img": "🍚"},
]

orders = []

def get_mpesa_token():
    key = os.getenv("MPESA_CONSUMER_KEY", "")
    secret = os.getenv("MPESA_CONSUMER_SECRET", "")
    if not key or not secret:
        return None
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(key, secret))
    try:
        return r.json().get("access_token")
    except:
        return None

def stk_push(phone, amount):
    token = get_mpesa_token()
    if not token:
        return {"error": "Add MPESA keys in Render Environment"}
    shortcode = os.getenv("MPESA_SHORTCODE", "174379")
    passkey = os.getenv("MPESA_PASSKEY", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    if phone.startswith("+"):
        phone = phone[1:]
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": "https://app.lonmaorbit.co.ke/mpesa-callback",
        "AccountReference": "LONMA",
        "TransactionDesc": "LONMA Shop"
    }
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    r = requests.post(url, json=payload, headers=headers)
    return r.json()

SHOP_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA</title>
<style>body{font-family:system-ui;margin:0;background:#f7f7f7}header{background:#2e7d32;color:#fff;padding:16px;text-align:center;position:sticky;top:0;z-index:10}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;padding:16px;padding-bottom:200px}
.card{background:#fff;border-radius:16px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.price{color:#2e7d32;font-weight:700}button{background:#2e7d32;color:#fff;border:0;padding:10px;border-radius:10px;width:100%;margin-top:8px;cursor:pointer}
#cart{position:fixed;bottom:0;left:0;right:0;background:#fff;padding:12px;border-top:1px solid #ddd}
input{padding:10px;border-radius:8px;border:1px solid #ccc;width:100%;margin:4px 0;box-sizing:border-box}
</style></head><body>
<header><h2>🛒 LONMA Supermarket</h2><a href="/admin" style="color:#c8e6c9">Admin</a> | <small>Lipa na M-Pesa</small></header>
<div class="grid" id="grid"></div>
<div id="cart"><input id="name" placeholder="Your Name"><input id="phone" placeholder="M-Pesa 07xx"><p id="total">Total: KSh 0</p>
<button onclick="pay()">💳 Lipa na M-Pesa</button><button onclick="wa()" style="background:#25D366">📱 WhatsApp Order</button><p id="s" style="text-align:center"></p></div>
<script>
let cart=[], P=[];
async function load(){ let r=await fetch('/products'); P=await r.json();
document.getElementById('grid').innerHTML=P.map(x=>`<div class="card"><div style="font-size:40px;text-align:center">${x.img}</div><h3>${x.name}</h3><small>${x.category}</small><div class="price">KSh ${x.price}</div><button onclick="add(${x.id})">Add</button></div>`).join('');}
function add(id){ cart.push(id); let t=cart.reduce((a,i)=>a+P.find(p=>p.id==i).price,0); document.getElementById('total').innerText='Total: KSh '+t; document.getElementById('s').innerText=cart.length+' items';}
async function pay(){ let ph=document.getElementById('phone').value; if(!ph) return alert('Enter phone'); let total=cart.reduce((a,i)=>a+P.find(p=>p.id==i).price,0); if(total==0) return alert('Cart empty');
document.getElementById('s').innerText='Sending STK... check phone'; let r=await fetch('/mpesa-pay',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone:ph,amount:total})}); let j=await r.json(); document.getElementById('s').innerText=j.CustomerMessage || JSON.stringify(j); }
async function wa(){ let n=document.getElementById('name').value, ph=document.getElementById('phone').value; let msg=`LONMA Order ${n} (${ph}): `+cart.map(id=>P.find(p=>p.id==id).name).join(', '); window.open('https://wa.me/254700000000?text='+encodeURIComponent(msg),'_blank');}
load();
</script></body></html>"""

ADMIN_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:system-ui;padding:20px;background:#f7f7f7}input,button{padding:10px;margin:6px 0;width:100%;border-radius:8px;border:1px solid #ccc;box-sizing:border-box}button{background:#2e7d32;color:#fff;border:0}.card{background:#fff;padding:12px;border-radius:10px;margin:6px 0}</style></head><body>
<h2>LONMA Admin</h2><input type="password" id="pass" placeholder="Password lonma123"><button onclick="check()">Login</button>
<div id="f" style="display:none"><h3>Add Product</h3><input id="n" placeholder="Name"><input id="c" placeholder="Category"><input id="p" type="number" placeholder="Price"><input id="st" type="number" placeholder="Stock"><input id="im" placeholder="Emoji eg 🥤"><button onclick="add()">Add</button><h3>Orders</h3><div id="o"></div></div>
<script>function check(){if(document.getElementById('pass').value=='lonma123'){document.getElementById('f').style.display='block';load()}}async function load(){let r=await fetch('/orders');let o=await r.json();document.getElementById('o').innerHTML=o.map(x=>`<div class=card>${x.customer||''} ${x.phone||''} - ${x.product} = ${x.total}</div>`).join('')||'No orders'}async function add(){let b={name:document.getElementById('n').value,category:document.getElementById('c').value,price:parseFloat(document.getElementById('p').value),stock:parseInt(document.getElementById('st').value),img:document.getElementById('im').value||'📦'};await fetch('/add-product',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});alert('Added');}</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def shop_page():
    return SHOP_HTML

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return ADMIN_HTML

@app.get("/products")
def get_products():
    return products

@app.get("/orders")
def get_orders():
    return orders

@app.post("/mpesa-pay")
def mpesa_pay(req: MpesaRequest):
    return stk_push(req.phone, req.amount)

@app.post("/mpesa-callback")
def mpesa_callback(data: dict):
    print(data)
    orders.append({"customer": "M-Pesa", "product": str(data), "total": 0, "phone": ""})
    return {"ok": True}

@app.post("/order")
def create_order(o: OrderCreate):
    p = next((x for x in products if x["id"] == o.product_id), None)
    if not p:
        return {"error": "not found"}
    orders.append({"customer": o.customer_name, "phone": o.phone, "product": p["name"], "qty": o.quantity, "total": p["price"]*o.quantity})
    return {"ok": True}

@app.post("/add-product")
def add_product(p: ProductCreate):
    nid = max([x["id"] for x in products], default=0) + 1
    products.append({"id": nid, "name": p.name, "category": p.category, "price": p.price, "stock": p.stock, "img": p.img})
    return {"ok": True}

@app.delete("/products/{pid}")
def delete_product(pid: int):
    global products
    products = [x for x in products if x["id"] != pid]
    return {"ok": True}
