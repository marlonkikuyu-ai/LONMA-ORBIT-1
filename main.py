from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, random, time
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
OTP_STORE = {}
USERS = {}
ORDERS = []
def generate_otp():
    return str(random.randint(100000, 999999))
@app.post("/auth/send-otp")
async def send_otp(req: Request):
    b = await req.json()
    phone = b.get("phone", "").strip()
    if len(phone) < 9:
        return {"success": False, "error": "Invalid phone"}
    otp = generate_otp()
    OTP_STORE[phone] = {"otp": otp, "exp": time.time() + 300, "tries": 0}
    return {"success": True, "debug_otp": otp}
@app.post("/auth/verify-otp")
async def verify_otp(req: Request):
    b = await req.json()
    phone = b.get("phone", "").strip()
    code = b.get("code", "").strip()
    name = b.get("name", "").strip()
    rec = OTP_STORE.get(phone)
    if not rec:
        return {"success": False, "error": "No OTP sent"}
    if time.time() > rec["exp"]:
        OTP_STORE.pop(phone, None)
        return {"success": False, "error": "OTP expired"}
    if rec["otp"]!= code:
        rec["tries"] += 1
        return {"success": False, "error": "Wrong code"}
    OTP_STORE.pop(phone, None)
    token = f"tok_{phone}_{int(time.time())}"
    USERS[token] = {"phone": phone, "name": name if name else "Mteja"}
    return {"success": True, "token": token, "user": USERS[token]}
@app.get("/auth/me")
async def me(req: Request):
    token = req.headers.get("Authorization", "").replace("Bearer ", "")
    u = USERS.get(token)
    if not u:
        return {"logged_in": False}
    return {"logged_in": True, "user": u}
@app.post("/auth/logout")
async def logout(req: Request):
    token = req.headers.get("Authorization", "").replace("Bearer ", "")
    USERS.pop(token, None)
    return {"success": True}
@app.get("/logo.png")
async def logo_png():
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="80"><rect width="200" height="80" fill="#0A8EA8" rx="12"/><text x="100" y="48" font-size="30" text-anchor="middle" fill="white" font-family="Arial" font-weight="900">LO</text></svg>'
    return Response(content=svg, media_type="image/svg+xml")
@app.post("/mpesa/stkpush")
async def stkpush(req: Request):
    b = await req.json()
    oid = f"ORD{random.randint(1000,9999)}"
    ORDERS.append({"id": oid, "phone": b.get("phone"), "amount": b.get("amount")})
    return {"success": True, "order_id": oid}
@app.get("/", response_class=HTMLResponse)
async def index():
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA ORBIT</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Arial}
body{background:#0B0E14;color:#fff;padding-bottom:90px}
.header{background:#0A8EA8;padding:14px 16px}
.h-top{display:flex;justify-content:space-between;align-items:center}
.logo{height:48px;background:#fff;border-radius:10px;padding:4px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:16px}
.card{background:#151A27;border-radius:16px;overflow:hidden;border:1px solid #1E293B}
.card-body{padding:12px}
.input{width:100%;padding:13px;border-radius:12px;border:1px solid #1E293B;background:#0B0E14;color:#fff;margin:6px 0}
.btn{width:100%;padding:14px;border:none;border-radius:12px;font-weight:800;margin-top:8px;cursor:pointer}
.bottom{position:fixed;bottom:0;left:0;right:0;background:#151A27;display:flex;justify-content:space-around;padding:12px 0;border-top:1px solid #1E293B}
.tab{flex:1;text-align:center;cursor:pointer}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);justify-content:center;align-items:flex-end;z-index:99}
.modal.open{display:flex}
.sheet{background:#151A27;width:100%;max-width:520px;border-radius:22px 22px 0 0;padding:20px;max-height:92vh;overflow-y:auto}
</style>
</head>
<body>
<div class="header">
<div class="h-top">
<img src="/logo.png" class="logo">
<div style="background:#fff;color:#0A8EA8;padding:8px 14px;border-radius:100px;font-weight:800;font-size:12px">4.9 ★ 2.3k</div>
</div>
<div style="margin-top:10px"><b>LONMA ORBIT</b><br><small>30min delivery - Kajiado HQ</small></div>
</div>
<div class="grid" id="grid"></div>
<div class="bottom">
<div class="tab" onclick="window.scrollTo(0,0)">🏠<br><small>Home</small></div>
<div class="tab" onclick="openModal('cartModal')">🛒<br><small>Cart</small></div>
<div class="tab" onclick="openModal('profileModal')">👤<br><small>You</small></div>
</div>
<div id="cartModal" class="modal">
<div class="sheet">
<h3>Cart</h3>
<div id="cartItems" style="margin:12px 0"></div>
<input id="cPhone" class="input" value="254" placeholder="2547XXXXXXXX">
<button class="btn" style="background:#0A8EA8;color:#fff" onclick="checkout()">Lipa na M-Pesa</button>
<button class="btn" style="background:#1E293B;color:#fff" onclick="closeModals()">Close</button>
</div>
</div>
<div id="profileModal" class="modal">
<div class="sheet">
<h3>You</h3>
<div id="loginForm">
<input id="loginName" class="input" placeholder="Jina lako">
<input id="loginPhone" class="input" value="254" placeholder="2547XXXXXXXX">
<button class="btn" id="sendOtpBtn" style="background:#22C55E;color:#fff" onclick="sendOTP()">Tuma Code</button>
<div id="otpSection" style="display:none">
<input id="otpCode" class="input" placeholder="Enter 6-digit code" maxlength="6">
<button class="btn" style="background:#0A8EA8;color:#fff" onclick="verifyOTP()">Verify and Login</button>
<button class="btn" style="background:#1E293B;color:#fff" onclick="backToPhone()">Badilisha Namba</button>
</div>
</div>
<div id="userSection" style="display:none">
<h4 id="welcomeMsg" style="margin:10px 0"></h4>
<p id="userPhoneDisplay" style="color:#94A3B8"></p>
<button class="btn" style="background:#EF4444;color:#fff" onclick="logoutUser()">Logout</button>
</div>
<button class="btn" style="background:#1E293B;color:#fff" onclick="closeModals()">Close</button>
</div>
</div>
<script>
var PRODUCTS = [
{id:1, name:"Jogoo Unga 2kg", price:175},
{id:2, name:"Mumias Sugar 2kg", price:310},
{id:3, name:"Fresh Fri Oil 2L", price:450},
{id:4, name:"Pishori Rice 2kg", price:350}
];
var cart = [];
var authToken = localStorage.getItem("lonma_token") || "";
var currentPhone = "";
function renderProducts(){
var h = "";
for(var i=0;i<PRODUCTS.length;i++){
var p = PRODUCTS[i];
h += '<div class="card"><div class="card-body"><h4>'+p.name+'</h4><b>KES '+p.price+'</b><br><button class="btn" style="background:#fff;color:#000;margin-top:8px" onclick="addToCart('+p.id+')">Add +</button></div></div>';
}
document.getElementById("grid").innerHTML = h;
}
function addToCart(id){
for(var i=0;i<PRODUCTS.length;i++){
if(PRODUCTS[i].id===id){cart.push(PRODUCTS[i]);}
}
alert("Added to cart: "+cart.length);
openModal("cartModal");
renderCart();
}
function renderCart(){
var h = "";
var t = 0;
for(var i=0;i<cart.length;i++){h += "<div style='padding:8px 0;border-bottom:1px solid #1E293B;display:flex;justify-content:space-between'><span>"+cart[i].name+"</span><b>"+cart[i].price+"</b></div>"; t += cart[i].price;}
document.getElementById("cartItems").innerHTML = h || "Cart empty";
}
function openModal(id){
closeModals();
document.getElementById(id).classList.add("open");
if(id==="profileModal"){checkLogin();}
if(id==="cartModal"){renderCart();}
}
function closeModals(){
var m = document.querySelectorAll(".modal");
for(var i=0;i<m.length;i++){m[i].classList.remove("open");}
}
async function checkout(){
var phone = document.getElementById("cPhone").value;
var total = 0;
for(var i=0;i<cart.length;i++){total += cart[i].price;}
var r = await fetch("/mpesa/stkpush",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone, amount:total})});
var d = await r.json();
alert("Order placed: "+d.order_id);
cart = [];
closeModals();
}
async function sendOTP(){
var phone = document.getElementById("loginPhone").value.trim();
if(phone.length < 9){alert("Weka namba sahihi"); return;}
currentPhone = phone;
document.getElementById("sendOtpBtn").innerText = "Sending...";
var r = await fetch("/auth/send-otp",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:phone})});
var d = await r.json();
document.getElementById("sendOtpBtn").innerText = "Tuma Code";
if(d.success){
document.getElementById("otpSection").style.display = "block";
document.getElementById("sendOtpBtn").style.display = "none";
alert("Your code: "+d.debug_otp);
} else {
alert(d.error);
}
}
async function verifyOTP(){
var code = document.getElementById("otpCode").value.trim();
var name = document.getElementById("loginName").value.trim();
var r = await fetch("/auth/verify-otp",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({phone:currentPhone, code:code, name:name})});
var d = await r.json();
if(d.success){
authToken = d.token;
localStorage.setItem("lonma_token", authToken);
showUserSection(d.user);
} else {
alert(d.error);
}
}
function showUserSection(user){
document.getElementById("loginForm").style.display = "none";
document.getElementById("userSection").style.display = "block";
document.getElementById("welcomeMsg").innerText = "Jambo "+user.name+"!";
document.getElementById("userPhoneDisplay").innerText = user.phone;
}
function backToPhone(){
document.getElementById("otpSection").style.display = "none";
document.getElementById("sendOtpBtn").style.display = "block";
}
async function checkLogin(){
if(!authToken){return;}
var r = await fetch("/auth/me",{headers:{"Authorization":"Bearer "+authToken}});
var d = await r.json();
if(d.logged_in){showUserSection(d.user);}
}
async function logoutUser(){
await fetch("/auth/logout",{method:"POST",headers:{"Authorization":"Bearer "+authToken}});
localStorage.removeItem("lonma_token");
authToken = "";
location.reload();
}
renderProducts();
</script>
</body>
</html>"""
    return HTMLResponse(html)
