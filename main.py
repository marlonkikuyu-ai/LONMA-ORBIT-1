from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, requests, random, time
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
ORDERS=[]
RIDERS=[{"id":1,"name":"John Mwangi","motor":"KMEZ 123A","status":"available","rating":4.9}]
REVIEWS=[{"name":"Wanjiku A.","location":"Kajiado","stars":5,"text":"Unga ilifika 25min","product":"Jogoo Unga","date":"2 days ago"}]
OTP_STORE={}
USERS={}
def generate_otp():
    return str(random.randint(100000,999999))
def smart_ai_reply(msg):
    m=msg.lower()
    if "unga" in m:
        return {"reply":"Jogoo Unga 2kg KES 175","action":"add_to_cart","product_id":1,"product_name":"Jogoo Unga"}
    if "sukari" in m:
        return {"reply":"Mumias Sugar 2kg KES 310","action":"add_to_cart","product_id":2,"product_name":"Mumias Sugar"}
    return {"reply":"Jambo Karibu LONMA ORBIT","action":None}
def make_product_svg(name,brand_color,emoji):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300"><rect width="300" height="300" fill="#FFFFFF" rx="20"/><rect x="30" y="30" width="240" height="160" fill="{brand_color}" rx="12"/><text x="150" y="110" font-size="56" text-anchor="middle">{emoji}</text><rect x="20" y="210" width="260" height="70" fill="#F8FAFC" rx="12"/><text x="150" y="245" font-size="12" text-anchor="middle" font-family="Arial">{name[:22]}</text></svg>'
    return svg.encode()
def make_logo_svg():
    return b'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="80" viewBox="0 0 200 80"><rect width="200" height="80" fill="#0A8EA8" rx="12"/><text x="100" y="50" font-size="32" text-anchor="middle" fill="white" font-family="Arial" font-weight="900">LO</text></svg>'
@app.post("/auth/send-otp")
async def send_otp(req: Request):
    b=await req.json()
    phone=b.get("phone","").strip()
    if len(phone)<9:
        return {"success":False,"error":"Invalid phone"}
    otp=generate_otp()
    OTP_STORE[phone]={"otp":otp,"exp":time.time()+300,"tries":0}
    return {"success":True,"debug_otp":otp}
@app.post("/auth/verify-otp")
async def verify_otp(req: Request):
    b=await req.json()
    phone=b.get("phone","").strip()
    code=b.get("code","").strip()
    name=b.get("name","").strip()
    rec=OTP_STORE.get(phone)
    if not rec:
        return {"success":False,"error":"No OTP"}
    if time.time()>rec["exp"]:
        del OTP_STORE[phone]
        return {"success":False,"error":"Expired"}
    if rec["otp"]!=code:
        rec["tries"]+=1
        return {"success":False,"error":"Wrong"}
    del OTP_STORE[phone]
    token=f"tok_{phone}_{int(time.time())}"
    USERS[token]={"phone":phone,"name":name if name else "Mteja"}
    return {"success":True,"token":token,"user":USERS[token]}
@app.get("/auth/me")
async def me(req: Request):
    token=req.headers.get("Authorization","").replace("Bearer ","")
    u=USERS.get(token)
    if not u:
        return {"logged_in":False}
    return {"logged_in":True,"user":u}
@app.post("/auth/logout")
async def logout(req: Request):
    token=req.headers.get("Authorization","").replace("Bearer ","")
    if token in USERS:
        del USERS[token]
    return {"success":True}
@app.get("/logo.png")
async def logo_png():
    for p in ["logo.png","./logo.png"]:
        if os.path.exists(p):
            return FileResponse(p, media_type="image/png")
    return Response(content=make_logo_svg(), media_type="image/svg+xml")
@app.get("/favicon.ico")
async def favicon():
    return Response(content=make_logo_svg(), media_type="image/svg+xml")
@app.get("/terms", response_class=HTMLResponse)
async def terms_page():
    return HTMLResponse('<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#0A8EA8;color:#fff;padding:20px;font-family:Arial;text-align:center}</style></head><body><h1>LONMA ORBIT</h1><a href="/" style="color:#fff">Back</a></body></html>')
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT</title><link rel="icon" href="/logo.png"><style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial}body{background:#0B0E14;color:#F8FAFC;padding-bottom:110px}.header{background:#0A8EA8;padding:12px 16px}.h-top{display:flex;justify-content:space-between;align-items:center}.logo-img{height:52px;background:#fff;border-radius:12px;padding:3px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;padding:16px}.card{background:#151A27;border-radius:20px;overflow:hidden;border:1px solid #1E293B}.card-img{height:150px;background:#fff}.card-img img{width:100%;height:100%;object-fit:cover}.card-body{padding:12px}.btn{width:100%;padding:14px;border:none;border-radius:14px;font-weight:800;margin-top:8px}.input{width:100%;padding:12px;border-radius:12px;border:1px solid #1E293B;background:#0B0E14;color:#fff;margin:6px 0}.bottom{position:fixed;bottom:0;left:0;right:0;background:#151A27;display:flex;justify-content:space-around;padding:10px;z-index:50}.tab{flex:1;text-align:center}.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);justify-content:center;align-items:flex-end;z-index:80}.modal.open{display:flex}.sheet{background:#151A27;width:100%;max-width:520px;border-radius:24px 24px 0 0;padding:20px;max-height:90vh;overflow-y:auto}</style></head><body><div class="header"><div class="h-top"><img src="/logo.png" class="logo-img"><div style="background:#fff;color:#0A8EA8;padding:8px 12px;border-radius:100px;font-weight:800">4.9</div></div><div style="color:#fff;margin-top:8px"><b>LONMA ORBIT - 30min delivery</b></div></div><div class="grid" id="grid"></div><div class="bottom"><div class="tab">🏠<br><small>Home</small></div><div class="tab" onclick="openCart()">🛒<br><small>Cart</small></div><div class="tab" onclick="openProfile()">👤<br><small>You</small></div></div><div id="cartModal" class="modal"><div class="sheet"><h3>Cart</h3><div id="cartItems"></div><button class="btn" style="background:#0A8EA8;color:#fff" onclick="checkout()">Lipa na M-Pesa</button><button class="btn" style="background:#333;color:#fff" onclick="closeM()">Close</button></div></div><div id="profileModal" class="modal"><div class="sheet"><h3>You</h3><input id="loginName" class="input" placeholder="Jina"><input id="loginPhone" class="input" value="254"><button class="btn" id="sendOtpBtn" onclick="sendOTP()" style="background:#22C55E;color:#fff">Tuma Code</button><div id="otpSection" style="display:none"><input id="otpCode" class="input" placeholder="6-digit"><button class="btn" onclick="verifyOTP()" style="background:#0A8EA8;color:#fff">Verify</button></div><div id="userSection" style="display:none"><h4 id="welcomeMsg"></h4><p id="userPhoneDisplay"></p><button class="btn" onclick="logoutUser()" style="background:#EF4444;color:#fff">Logout</button></div><button class="btn" style="background:#333;color:#fff" onclick="closeM()">Close</button></div></div><script>var PRODUCTS=[{"id":1,"name":"Jogoo Unga 2kg","price":175,"img":"/img/flour"},{"id":2,"name":"Mumias Sugar 2kg","price":310,"img":"/img/sugar"},{"id":3,"name":"Fresh Fri 2L","price":450,"img":"/img/oil"}];var cart=[];var authToken=localStorage.getItem("lonma_token")||"";var currentPhone="";function renderProducts(){var h="";for(var i=0;i<PRODUCTS.length;i++){var p=PRODUCTS[i];h+='<div class="card"><div class="card-img"><img src="'+p.img+'"></div><div class="card-body"><h4>'+p.name+'</h4><b>KES '+p.price+'</b><br><button class="btn" style="background:#fff;color:#000" onclick="addToCart('+p.id+')">Add</button></div></div>';}document.getElementById("grid").innerHTML=h;}function addToCart(id){for(var i=0;i<PRODUCTS.length;i++)if(PRODUCTS[i].id===id)cart.push(PRODUCTS[i]);}function openCart(){var h="";for(var i=0;i<cart.length;i++)h+='<div>'+cart[i].name+' - '+cart[i].price+'</div>';document.getElementById("cartItems").innerHTML=h||"Empty";document.getElementById("cartModal").classList.add("open");}function closeM(){var m=document.querySelectorAll(".modal");for(var i=0;i<m.length;i++)m[i].classList.remove("open");}async function checkout(){var r=await fetch("/mpesa/stkpush",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:"254700000000",amount:100})});var d=await r.json();alert(d.order_id);}async function sendOTP(){var phone=document.getElementById("loginPhone").value.trim();currentPhone=phone;var r=await fetch("/auth/send-otp",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone})});var d=await r.json();if(d.success){document.getElementById("otpSection").style.display="block";document.getElementById("sendOtpBtn").style.display="none";alert(d.debug_otp);}}async function verifyOTP(){var code=document.getElementById("otpCode").value.trim();var name=document.getElementById("loginName").value.trim();var r=await fetch("/auth/verify-otp",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:currentPhone,code:code,name:name})});var d=await r.json();if(d.success){authToken=d.token;localStorage.setItem("lonma_token",authToken);document.getElementById("userSection").style.display="block";document.getElementById("welcomeMsg").innerText="Jambo "+d.user.name;document.getElementById("userPhoneDisplay").innerText=d.user.phone;}}async function logoutUser(){await fetch("/auth/logout",{method:"POST",headers:{"Authorization":"Bearer "+authToken}});localStorage.removeItem("lonma_token");location.reload();}function openProfile(){document.getElementById("profileModal").classList.add("open");}renderProducts();</script></body></html>""")
@app.post("/ai/chat")
async def chat(req: Request):
    b=await req.json()
    return smart_ai_reply(b.get("message",""))
@app.post("/mpesa/stkpush")
async def stk(req: Request):
    b=await req.json()
    oid=f"ORD{random.randint(1000,9999)}"
    ORDERS.append({"id":oid})
    return {"order_id":oid}
@app.get("/img/{name}")
async def product_img(name: str):
    maps={"flour":("JOGOO","#F59E0B","🌽"),"sugar":("MUMIAS","#EF4444","🍚"),"oil":("FRESH FRI","#10B981","🫒")}
    n,c,e=maps.get(name,(name.upper(),"#0A8EA8","🛒"))
    return Response(content=make_product_svg(n,c,e), media_type="image/svg+xml")
