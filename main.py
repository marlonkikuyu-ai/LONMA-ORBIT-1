from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OrderCreate(BaseModel):
    customer_name: str
    phone: str
    product_id: int
    quantity: int

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
    {"id": 7, "name": "Blue Band 500g", "category": "Spread", "price": 280, "stock": 40, "img": "🧈"},
    {"id": 8, "name": "Eggs Tray", "category": "Dairy", "price": 420, "stock": 30, "img": "🥚"},
]
orders = []

SHOP = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA</title><style>
body{font-family:system-ui;margin:0;background:#f7f7f7} header{background:#2e7d32;color:#fff;padding:16px;text-align:center;position:sticky;top:0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;padding:16px;padding-bottom:140px}
.card{background:#fff;border-radius:16px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.price{color:#2e7d32;font-weight:700} button{background:#2e7d32;color:#fff;border:0;padding:8px 12px;border-radius:10px;width:100%;margin-top:8px}
#cart{position:fixed;bottom:0;left:0;right:0;background:#fff;padding:12px;border-top:1px solid #ddd}
input{padding:8px;border-radius:8px;border:1px solid #ccc;width:100%;margin:4px 0;box-sizing:border-box}
</style></head><body>
<header><h2>🛒 LONMA Supermarket</h2><a href="/admin" style="color:#c8e6c9">Admin</a></header>
<div class="grid" id="grid"></div>
<div id="cart"><input id="name" placeholder="Your Name"><input id="phone" placeholder="Phone 07xx">
<button onclick="checkout()">Place Order via WhatsApp</button><p id="s" style="text-align:center"></p></div>
<script>
let cart=[]; async function load(){ let r=await fetch('/products'); let p=await r.json(); window.P=p;
document.getElementById('grid').innerHTML=p.map(x=>`<div class="card"><div style="font-size:40px;text-align:center">${x.img}</div><h3>${x.name}</h3><small>${x.category} • ${x.stock} left</small><div class="price">KSh ${x.price}</div><button onclick="add(${x.id})">Add</button></div>`).join('');}
function add(id){cart.push(id);document.getElementById('s').innerText=cart.length+' items';}
async function checkout(){let n=document.getElementById('name').value,ph=document.getElementById('phone').value;
if(!n||!ph)return alert('name+phone'); if(!cart.length)return alert('empty');
for(let id of cart){await fetch('/order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({customer_name:n,phone:ph,product_id:id,quantity:1})})}
let msg=`LONMA Order ${n} (${ph}): `+cart.map(id=>P.find(p=>p.id==id).name).join(', ');
window.open('https://wa.me/254700000000?text='+encodeURIComponent(msg),'_blank'); document.getElementById('s').innerText='Sent ✅'; cart=[];}
load();
</script></body></html>
"""

ADMIN = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin</title>
<style>body{font-family:system-ui;padding:20px;background:#f7f7f7} input,button{padding:10px;margin:5px;border-radius:8px;border:1px solid #ccc;width:100%;box-sizing:border-box} button{background:#2e7d32;color:#fff;border:0}
.card{background:#fff;padding:12px;border-radius:12px;margin:8px 0}</style></head><body>
<h2>LONMA Admin</h2><input type="password" id="pass" placeholder="Password (lonma123)">
<div id="form" style="display:none">
<h3>Add Product</h3><input id="name" placeholder="Name"><input id="cat" placeholder="Category">
<input id="price" type="number" placeholder="Price"><input id="stock" type="number" placeholder="Stock">
<input id="img" placeholder="Emoji eg 🥤"><button onclick="add()">Add Product</button>
<h3>Orders</h3><div id="orders"></div><h3>Products</h3><div id="list"></div>
</div>
<script>
function check(){ if(document.getElementById('pass').value=='lonma123'){document.getElementById('form').style.display='block';load();} else alert('wrong');}
document.getElementById('pass').addEventListener('change',check);
async function load(){ let r=await fetch('/products'); let p=await r.json(); document.getElementById('list').innerHTML=p.map(x=>`<div class="card">${x.img} ${x.name} - KSh${x.price} - ${x.stock} left <button onclick="del(${x.id})">Delete</button></div>`).join('');
let r2=await fetch('/orders'); let o=await r2.json(); document.getElementById('orders').innerHTML=o.map(x=>`<div class="card">${x.customer} ${x.phone} - ${x.product} x${x.qty} = ${x.total}</div>`).join('')||'No orders';}
async function add(){ let body={name:document.getElementById('name').value, category:document.getElementById('cat').value, price:parseFloat(document.getElementById('price').value), stock:parseInt(document.getElementById('stock').value), img:document.getElementById('img').value||'📦'}; await fetch('/add-product',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); load(); }
async function del(id){ await fetch('/products/'+id,{method:'DELETE'}); load(); }
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def shop(): return SHOP

@app.get("/admin", response_class=HTMLResponse)
def admin(): return ADMIN

@app.get("/products")
def get_p(): return products

@app.get("/orders")
def get_o(): return orders

@app.post("/order")
def order(o: OrderCreate):
    p = next((x for x in products if x["id"] == o.product_id), None)
    if not p: return {"error": "no"}
    orders.append({"customer": o.customer_name, "phone": o.phone, "product": p["name"], "qty": o.quantity, "total": p["price"]*o.quantity})
    p["stock"] -= o.quantity
    return {"ok": True}

@app.post("/add-product")
def add_p(p: ProductCreate):
    nid = max([x["id"] for x in products], default=0)+1
    products.append({"id": nid, "name": p.name, "category": p.category, "price": p.price, "stock": p.stock, "img": p.img})
    return {"ok": True}

@app.delete("/products/{pid}")
def delete_p(pid: int):
    global products
    products = [x for x in products if x["id"] != pid]
    return {"ok": True}
