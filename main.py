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

# --- MPESA FUNCTIONS ---
def get_mpesa_token():
    key = os.getenv("MPESA_CONSUMER_KEY", "test")
    secret = os.getenv("MPESA_CONSUMER_SECRET", "test")
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(key, secret))
    return r.json().get("access_token")

def stk_push(phone, amount):
    try:
        token = get_mpesa_token()
        shortcode = os.getenv("MPESA_SHORTCODE", "174379")
        passkey = os.getenv("MPESA_PASSKEY", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()
        
        # Format phone 07xx to 2547xx
        if phone.startswith("0"): phone = "254" + phone[1:]
        if phone.startswith("+"): phone = phone[1:]

        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": shortcode,
            "PhoneNumber": phone,
            "CallBackURL": "https://app.lonmaorbit.co.ke/mpesa-callback",
            "AccountReference": "LONMA",
            "TransactionDesc": "LONMA Supermarket"
        }
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        r = requests.post(url, json=payload, headers=headers)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

SHOP = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA</title>
<style>body{font-family:system-ui;margin:0;background:#f7f7f7}header{background:#2e7d32;color:#fff;padding:16px;text-align:center}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;padding:16px;padding-bottom:180px}
.card{background:#fff;border-radius:16px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.price{color:#2e7d32;font-weight:700}button{background:#2e7d32;color:#fff;border:0;padding:10px;border-radius:10px;width:100%;margin-top:8px}
#cart{position:fixed;bottom:0;left:0;right:0;background:#fff;padding:12px;border-top:1px solid #ddd}
input{padding:10px;border-radius:8px;border:1px solid #ccc;width:100%;margin:4px 0;box-sizing:border-box}
.pay{background:#000}
</style></head><body>
<header><h2>🛒 LONMA Supermarket</h2><small>Lipa na M-Pesa</small></header>
<div class="grid" id="grid"></div>
<div id="cart">
<input id="name" placeholder="Your Name"><input id="phone" placeholder="M-Pesa Phone 07xx">
<p id="total">Total: KSh 0</p>
<button onclick="pay()">💳 Lipa na M-Pesa</button>
<button onclick="checkout()" style="background:#25D366">📱 Order via WhatsApp</button>
<p id="s" style="text-align:center"></p>
</div>
<script>
let cart=[]; let P=[];
async function load(){let r=await fetch('/products');P=await r.json();
document.getElementById('grid').innerHTML=P.map(x=>`<div class="card"><div style="font-size:40px;text-align:center">${x.img}</div><h3>${x.name}</h3><small>${x.category}</small><div class="price">KSh ${x.price}</div><button onclick="add(${x.id})">Add</button></div>`).join('');}
function add(id){cart.push(id);update();}
function update(){let t=cart.reduce((a,id)=>a+P.find(p=>p.id==id).price,0);document.getElementById('total').innerText='Total: KSh '+t;document.getElementById('s').innerText=cart.length+' items';}
async function pay(){let ph=document.getElementById('phone').value; if(!ph)return alert('phone'); let total=cart.reduce((a,id)=>a+P.find(p=>p.id==id).price,0);
document.getElementById('s').innerText='Sending STK... check phone'; let r=await fetch('/mpesa-pay',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone:ph,amount:total})}); let j=await r.json(); document.getElementById('s').innerText=JSON.stringify(j); }
async function checkout(){let n=document.getElementById('name').value,ph=document.getElementById('phone').value; if(!n||!ph)return alert('name+phone'); let msg=`LONMA Order ${n} (${ph}): `+cart.map(id=>P.find(p=>p.id==id).name).join(', '); window.open('https://wa.me/254700000000?text='+encodeURIComponent(msg),'_blank');}
load();
</script></body></html>
"""

ADMIN = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:system-ui;padding:20px}input,button{padding:10px;margin:5px;width:100%;border-radius:8px;border:1px solid #ccc}button{background:#2e7d32;color:#fff}</style></head><body>
<h2>Admin - lonma123</h2><input type="password" id="pass" placeholder="Password"><div id="f" style="display:none"><h3>Add</h3><input id="n" placeholder="Name"><input id="c" placeholder="Category"><input id="p" type="number" placeholder="Price"><input id="st" type="number" placeholder="Stock"><input id="im" placeholder="Emoji"><button onclick="add()">Add</button><div id="o"></div></div>
<script>document.getElementById('pass').onchange=()=>{if(document.getElementById('pass').value=='lonma123'){document.getElementById('f').style.display='block';load()}};async function load(){let r=await fetch('/orders');let o=await r.json();document.getElementById('o').innerHTML=o.map(x=>`<p>${x.customer} - ${x.product} - ${x.total}</p>`).join('')}async function add(){let b={name:document.getElementById('n').value,category:document.getElementById('c').value,price:parseFloat(document.getElementById('p').value),stock:parseInt(document.getElementById('st').value),img:document.getElementById('im').value};await fetch('/add-product',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});alert('added')}</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
def shop(): return SHOP
@app.get("/admin", response_class=HTMLResponse)
def admin(): return ADMIN
@app.get("/products")
def get_p(): return products
@app.get("/orders")
def get_o(): return orders

@app.post("/mpesa-pay")
def mpesa_pay(req: MpesaRequest):
    result = stk_push(req.phone, req.amount)
    return result

@app.post("/mpesa-callback")
def mpesa_callback(data: dict):
    print("MPESA CALLBACK:", data)
    orders.append({"customer": "M-Pesa", "product": str(data), "total": 0})
    return {"ok": True}

@app.post("/order")
def order(o: OrderCreate):
    p = next((x for x in products if x["id"] == o.product_id), None)
    if not p: return {"error": "no"}
    orders.append({"customer": o.customer_name, "phone": o.phone, "product": p["name"], "qty": o.quantity, "total": p["price"]*o.quantity})
    return {"ok": True}

@app.post("/add-product")
def add_p(p: ProductCreate):
    nid = max([x["id"] for x in products], default=0)+1
    products.append({"id": nid, "name": p.name, "category": p.category, "price": p.price, "stock": p.stock, "img": p.img})
    return {"ok": True}
