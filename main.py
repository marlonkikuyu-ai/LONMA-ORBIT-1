from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import os, random, time
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
OTP_STORE = {}
USERS = {}
ORDERS = []
SUPERMARKETS = ["Naivas","Carrefour","Quickmart","Chandarana Foodplus"]
PRODUCTS_DB = [
{"id":1,"name":"Jogoo Maize Flour 2kg","price":175,"old":195,"supermarket":"Naivas","cat":"Staples","emoji":"🌽","color":"#F59E0B"},
{"id":2,"name":"Mumias Sugar 2kg","price":310,"old":340,"supermarket":"Naivas","cat":"Staples","emoji":"🍚","color":"#EF4444"},
{"id":3,"name":"Fresh Fri Cooking Oil 2L","price":450,"old":520,"supermarket":"Quickmart","cat":"Cooking","emoji":"🫒","color":"#10B981"},
{"id":4,"name":"Pishori Rice 2kg","price":350,"old":400,"supermarket":"Carrefour","cat":"Staples","emoji":"🍚","color":"#8B5CF6"},
{"id":5,"name":"Brookside Milk 500ml","price":65,"old":75,"supermarket":"Chandarana Foodplus","cat":"Dairy","emoji":"🥛","color":"#0EA5E9"},
{"id":6,"name":"Supa Loaf Bread 400g","price":60,"old":70,"supermarket":"Naivas","cat":"Bakery","emoji":"🍞","color":"#F97316"},
{"id":7,"name":"Kabras Sugar 1kg","price":160,"old":180,"supermarket":"Quickmart","cat":"Staples","emoji":"🍬","color":"#EC4899"},
{"id":8,"name":"Elianto Oil 3L","price":680,"old":750,"supermarket":"Carrefour","cat":"Cooking","emoji":"🧴","color":"#14B8A6"},
]
def generate_otp():
    return str(random.randint(100000,999999))
def make_img(emoji,color,name):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect width="400" height="300" fill="{color}"/><text x="200" y="140" font-size="90" text-anchor="middle">{emoji}</text><rect x="0" y="220" width="400" height="80" fill="white"/><text x="200" y="265" font-size="18" text-anchor="middle" font-family="Arial" font-weight="800">{name[:20]}</text></svg>'
    return svg.encode()
@app.get("/img/{pid}")
async def prod_img(pid:int):
    p=next((x for x in PRODUCTS_DB if x["id"]==pid),PRODUCTS_DB[0])
    return Response(content=make_img(p["emoji"],p["color"],p["name"]),media_type="image/svg+xml")
@app.get("/api/supermarkets")
async def get_markets():
    return {"supermarkets":SUPERMARKETS}
@app.get("/api/products")
async def get_products(supermarket:str=""):
    if supermarket:
        return [p for p in PRODUCTS_DB if p["supermarket"]==supermarket]
    return PRODUCTS_DB
@app.post("/auth/send-otp")
async def send_otp(req:Request):
    b=await req.json()
    phone=b.get("phone","").strip()
    if len(phone)<9: return {"success":False,"error":"Invalid phone"}
    otp=generate_otp()
    OTP_STORE[phone]={"otp":otp,"exp":time.time()+300,"tries":0}
    return {"success":True,"debug_otp":otp}
@app.post("/auth/verify-otp")
async def verify_otp(req:Request):
    b=await req.json()
    phone=b.get("phone","").strip();code=b.get("code","").strip();name=b.get("name","").strip()
    rec=OTP_STORE.get(phone)
    if not rec: return {"success":False,"error":"No OTP"}
    if time.time()>rec["exp"]: OTP_STORE.pop(phone,None); return {"success":False,"error":"Expired"}
    if rec["otp"]!=code: return {"success":False,"error":"Wrong code"}
    OTP_STORE.pop(phone,None)
    token=f"tok_{phone}_{int(time.time())}"
    USERS[token]={"phone":phone,"name":name if name else "Mteja"}
    return {"success":True,"token":token,"user":USERS[token]}
@app.get("/auth/me")
async def me(req:Request):
    token=req.headers.get("Authorization","").replace("Bearer ","")
    u=USERS.get(token)
    return {"logged_in":bool(u),"user":u} if u else {"logged_in":False}
@app.post("/auth/logout")
async def logout(req:Request):
    token=req.headers.get("Authorization","").replace("Bearer ","")
    USERS.pop(token,None); return {"success":True}
@app.post("/mpesa/stkpush")
async def stkpush(req:Request):
    b=await req.json(); oid=f"ORD{random.randint(1000,9999)}"; ORDERS.append({"id":oid}); return {"success":True,"order_id":oid}
@app.get("/",response_class=HTMLResponse)
async def index():
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT - Supermarkets</title><style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial}body{background:#0B0E14;color:#fff;padding-bottom:90px}.header{background:#0A8EA8;padding:14px 16px;position:sticky;top:0;z-index:10}.h-top{display:flex;justify-content:space-between;align-items:center}.chips{display:flex;gap:8px;overflow-x:auto;padding:12px 16px}.chip{white-space:nowrap;padding:10px 16px;border-radius:100px;background:#151A27;border:1px solid #1E293B;color:#94A3B8;cursor:pointer}.chip.active{background:#fff;color:#000}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:0 16px}.card{background:#151A27;border-radius:16px;overflow:hidden;border:1px solid #1E293B}.card img{width:100%;height:130px;object-fit:cover}.card-body{padding:10px}.sm{font-size:10px;color:#0A8EA8;font-weight:800;text-transform:uppercase}.price{font-weight:900;margin:4px 0}.old{color:#64748B;text-decoration:line-through;font-size:12px}.btn{width:100%;padding:12px;border:none;border-radius:10px;font-weight:800;margin-top:6px;cursor:pointer}.bottom{position:fixed;bottom:0;left:0;right:0;background:#151A27;display:flex;justify-content:space-around;padding:10px;border-top:1px solid #1E293B}.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);justify-content:center;align-items:flex-end;z-index:50}.modal.open{display:flex}.sheet{background:#151A27;width:100%;max-width:520px;border-radius:20px 20px 0 0;padding:20px}.input{width:100%;padding:12px;border-radius:10px;border:1px solid #1E293B;background:#0B0E14;color:#fff;margin:6px 0}</style></head><body><div class="header"><div class="h-top"><b style="font-size:18px">LONMA ORBIT</b><div style="background:#fff;color:#0A8EA8;padding:6px 12px;border-radius:100px;font-size:12px;font-weight:800">4.9 ★</div></div><div style="margin-top:6px;font-size:13px">Supermarkets near you - 30min delivery</div></div><div class="chips" id="smChips"></div><div class="grid" id="grid"></div><div class="bottom"><div onclick="window.scrollTo(0,0)">🏠<br><small>Home</small></div><div onclick="openModal('cartModal')">🛒 <span id="cCount">0</span><br><small>Cart</small></div><div onclick="openModal('profileModal')">👤<br><small>You</small></div></div><div id="cartModal" class="modal"><div class="sheet"><h3>Cart</h3><div id="cartItems"></div><input id="cPhone" class="input" value="254"><button class="btn" style="background:#0A8EA8;color:#fff" onclick="checkout()">Lipa na M-Pesa</button><button class="btn" style="background:#333;color:#fff" onclick="closeModals()">Close</button></div></div><div id="profileModal" class="modal"><div class="sheet"><h3>Login</h3><div id="loginForm"><input id="loginName" class="input" placeholder="Jina"><input id="loginPhone" class="input" value="254"><button class="btn" id="sendBtn" style="background:#22C55E;color:#fff" onclick="sendOTP()">Tuma Code</button><div id="otpSec" style="display:none"><input id="otpCode" class="input" placeholder="6-digit"><button class="btn" style="background:#0A8EA8;color:#fff" onclick="verifyOTP()">Verify</button></div></div><div id="userSec" style="display:none"><h4 id="wMsg"></h4><button class="btn" style="background:red;color:#fff" onclick="logout()">Logout</button></div><button class="btn" style="background:#333;color:#fff" onclick="closeModals()">Close</button></div></div><script>var allProducts=[];var cart=[];var activeSm="";var authToken=localStorage.getItem("lonma_token")||"";var curPhone="";async function loadData(){let r=await fetch("/api/products");allProducts=await r.json();renderMarkets();renderProducts();}function renderMarkets(){let sms=["","Naivas","Carrefour","Quickmart","Chandarana Foodplus"];let h="";sms.forEach(s=>{h+='<div class="chip '+(activeSm===s?'active':'')+'" onclick="filterSm(\\''+s+'\\')">'+(s===""?"All":s)+'</div>'});document.getElementById("smChips").innerHTML=h;}function filterSm(s){activeSm=s;renderMarkets();renderProducts();}function renderProducts(){let h="";allProducts.filter(p=>!activeSm||p.supermarket===activeSm).forEach(p=>{let disc=Math.round((p.old-p.price)/p.old*100);h+='<div class="card"><img src="/img/'+p.id+'"><div class="card-body"><div class="sm">'+p.supermarket+'</div><div style="font-size:13px;font-weight:700;height:32px;overflow:hidden">'+p.name+'</div><div><span class="price">KES '+p.price+'</span> <span class="old">'+p.old+'</span> <span style="background:red;color:#fff;font-size:10px;padding:2px 6px;border-radius:10px">-'+disc+'%</span></div><button class="btn" style="background:#fff;color:#000" onclick="addToCart('+p.id+')">Add +</button></div></div>'});document.getElementById("grid").innerHTML=h;}function addToCart(id){let p=allProducts.find(x=>x.id===id);cart.push(p);document.getElementById("cCount").innerText=cart.length;let h="";let t=0;cart.forEach(c=>{h+="<div style='display:flex;justify-content:space-between;padding:6px 0'><span>"+c.name+"</span><b>"+c.price+"</b></div>";t+=c.price});document.getElementById("cartItems").innerHTML=h+"<b>Total: "+t+"</b>";}function openModal(id){closeModals();document.getElementById(id).classList.add("open");if(id==="profileModal")checkLogin();}function closeModals(){document.querySelectorAll(".modal").forEach(m=>m.classList.remove("open"));}async function checkout(){let phone=document.getElementById("cPhone").value;let r=await fetch("/mpesa/stkpush",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone,amount:100})});let d=await r.json();alert("Order "+d.order_id);}async function sendOTP(){let ph=document.getElementById("loginPhone").value;curPhone=ph;let r=await fetch("/auth/send-otp",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:ph})});let d=await r.json();if(d.success){document.getElementById("otpSec").style.display="block";document.getElementById("sendBtn").style.display="none";alert(d.debug_otp);}}async function verifyOTP(){let code=document.getElementById("otpCode").value;let name=document.getElementById("loginName").value;let r=await fetch("/auth/verify-otp",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:curPhone,code:code,name:name})});let d=await r.json();if(d.success){localStorage.setItem("lonma_token",d.token);authToken=d.token;document.getElementById("loginForm").style.display="none";document.getElementById("userSec").style.display="block";document.getElementById("wMsg").innerText="Jambo "+d.user.name;}}async function checkLogin(){if(!authToken)return;let r=await fetch("/auth/me",{headers:{"Authorization":"Bearer "+authToken}});let d=await r.json();if(d.logged_in){document.getElementById("loginForm").style.display="none";document.getElementById("userSec").style.display="block";document.getElementById("wMsg").innerText="Jambo "+d.user.name;}}async function logout(){await fetch("/auth/logout",{method:"POST",headers:{"Authorization":"Bearer "+authToken}});localStorage.clear();location.reload();}loadData();</script></body></html>""")
