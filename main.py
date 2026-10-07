from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI()

USERS = {
    "admin": {"password": "Lonma@2026", "role": "Owner", "name": "Marlone - Owner", "branch": "all", "signature": "signed", "created": "2026-10-03"},
    "cashier1": {"password": "1234", "role": "Cashier", "name": "Marlon - Cashier", "branch": "lonma-westlands", "signature": "signed", "created": "2026-10-06"},
}

SUPERMARKETS = {
    "lonma-westlands": {"name": "LONMA Westlands", "short": "LONMA", "icon": "🏬", "products": [], "sales": []},
    "naivas": {"name": "Naivas", "short": "Naivas", "icon": "🛒", "products": [], "sales": []},
    "carrefour": {"name": "Carrefour", "short": "Carrefour", "icon": "🌍", "products": [], "sales": []},
    "chandarana": {"name": "Chandarana", "short": "Chandarana", "icon": "🍏", "products": [], "sales": []},
    "magunas": {"name": "Magunas", "short": "Magunas", "icon": "🏪", "products": [], "sales": []},
    "khetias": {"name": "Khetias", "short": "Khetias", "icon": "🏪", "products": [], "sales": []},
    "mathais": {"name": "Mathai's", "short": "Mathai's", "icon": "🌄", "products": [], "sales": []},
}

seed = [
    {"id": "BREAD001", "name": "Bread - Festive 400g", "price": 60, "stock": 300, "cat": "FOOD", "emoji": "🍞", "barcode": "6161100123"},
    {"id": "SUGAR001", "name": "Sugar - Kabras 1kg", "price": 165, "stock": 800, "cat": "FOOD", "emoji": "🧂", "barcode": "6161101100456"},
    {"id": "MILK001", "name": "Milk - Brookside 500ml", "price": 65, "stock": 500, "cat": "DRINKS", "emoji": "🥛", "barcode": "6161101100789"},
    {"id": "SODA001", "name": "Soda - Coca 500ml", "price": 70, "stock": 1000, "cat": "DRINKS", "emoji": "🥤", "barcode": "5449000000996"},
    {"id": "SUFU001", "name": "Sufuria - 3pc Set", "price": 1850, "stock": 40, "cat": "UTENSILS", "emoji": "🍲", "barcode": "6009685030021"},
    {"id": "GAS001", "name": "Gas Cooker - 2 Burner", "price": 4500, "stock": 15, "cat": "ELECTRONICS", "emoji": "🔥", "barcode": "6009685030151"},
]
for sm in SUPERMARKETS.values():
    sm["products"] = [dict(p) for p in seed]
    sm["sales"] = []

class Login(BaseModel): username: str; password: str
class Signup(BaseModel): username: str; password: str; name: str; role: str; branch: str; signature: str = ""
class Product(BaseModel): name: str; price: float; stock: int; cat: str; barcode: str = ""

@app.head("/")
async def head_root(): return Response(status_code=200)
@app.post("/api/login")
async def login(l: Login):
    from fastapi import HTTPException
    u = USERS.get(l.username.lower())
    if not u or u["password"]!= l.password: raise HTTPException(status_code=401, detail="Wrong")
    return {"username": l.username, "role": u["role"], "name": u["name"], "branch": u["branch"]}
@app.post("/api/signup")
async def signup(s: Signup):
    from fastapi import HTTPException
    if s.username.lower() in USERS: raise HTTPException(status_code=400, detail="Exists")
    USERS[s.username.lower()] = {"password": s.password, "role": s.role, "name": s.name, "branch": s.branch, "signature": s.signature, "created": datetime.now().isoformat()}
    return {"ok": True}
@app.get("/api/users")
async def list_users(): return [{"username": k, "name": v["name"], "role": v["role"], "branch": v["branch"], "created": v.get("created",""), "hasSignature": bool(v.get("signature"))} for k,v in USERS.items()]
@app.get("/api/supermarkets")
async def get_markets(): return SUPERMARKETS
@app.get("/api/{branch_id}/sales")
async def branch_sales(branch_id: str): return SUPERMARKETS.get(branch_id, {}).get("sales", [])[::-1]
@app.post("/api/{branch_id}/products")
async def add_prod(branch_id: str, p: Product):
    new_p = {"id": p.barcode or str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat.upper(), "emoji": "📦", "barcode": p.barcode or str(uuid.uuid4())[:8]}
    SUPERMARKETS[branch_id]["products"].append(new_p); return new_p
@app.post("/api/{branch_id}/products/bulk")
async def bulk_add(branch_id: str, products: List[Product]):
    added=[]
    for p in products:
        new_p = {"id": p.barcode or str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat.upper(), "emoji": "📦", "barcode": p.barcode or ""}
        SUPERMARKETS[branch_id]["products"].append(new_p); added.append(new_p)
    return {"added": len(added)}
@app.post("/api/{branch_id}/checkout")
async def checkout(branch_id: str, cart: List[dict]):
    sm = SUPERMARKETS[branch_id]; total=0; items=[]
    for ci in cart:
        prod = next((x for x in sm["products"] if x["id"]==ci["product_id"]), None)
        if prod and prod["stock"]>=ci["qty"]:
            prod["stock"]-=ci["qty"]; total+=prod["price"]*ci["qty"]; items.append({"name":prod["name"],"qty":ci["qty"],"price":prod["price"]})
    sale={"receipt":f"LON-{uuid.uuid4().hex[:6].upper()}","items":items,"total":total,"time":datetime.now().isoformat(),"cashier":"Marlon","payment":"M-Pesa"}
    sm["sales"].append(sale); return sale

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>LONMA ORBIT v2.3 BARCODE PRO</title>
<script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,system-ui} body{background:#0a0a0a;color:#fff;padding-bottom:120px}
.header{position:sticky;top:0;z-index:100;background:#000000f2;backdrop-filter:blur(14px);border-bottom:2px solid #0096B0;padding:12px 12px;display:flex;align-items:center;gap:8px}
.logo{width:44px;height:44px;background:linear-gradient(135deg,#0096B0,#00e5ff);border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:18px;color:#fff;flex-shrink:0}
.card{background:#141414;border:1px solid #242424;border-radius:16px;padding:14px;margin:10px 10px}
.pill{white-space:nowrap;padding:11px 18px;border-radius:24px;border:1.5px solid #333;background:#1e1e1e;font-size:13px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:6px;flex-shrink:0}
.pill.active{background:#0096B0;border-color:#0096B0;color:#fff;box-shadow:0 4px 14px rgba(0,150,176,0.35)}
.branch-scroll{display:flex;gap:10px;overflow-x:auto;padding:4px 4px 8px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.branch-scroll::-webkit-scrollbar{display:none}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:10px}
.stat{background:#141414;border:1px solid #242424;border-radius:14px;padding:12px 8px;text-align:center}
.cat{white-space:nowrap;padding:10px 18px;border-radius:24px;font-size:12px;font-weight:800;cursor:pointer;flex-shrink:0;border:2px solid transparent}
.cat.active{border-color:#fff;transform:scale(1.05)}
.cat-scroll{display:flex;gap:8px;overflow-x:auto;padding:4px 4px 10px;scrollbar-width:none}
.cat-scroll::-webkit-scrollbar{display:none}
.products{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.prod{background:#1b1b1b;border:1px solid #2a2a2a;border-radius:16px;padding:12px;position:relative;overflow:hidden}
.btn{background:#0096B0;color:#fff;border:none;padding:14px;border-radius:14px;font-weight:900;width:100%;cursor:pointer;letter-spacing:0.3px}
.fab{position:fixed;bottom:90px;right:16px;width:58px;height:58px;background:#FFD700;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:32px;font-weight:900;color:#000;box-shadow:0 10px 26px rgba(255,215,0,0.45);z-index:95;cursor:pointer;border:3px solid #000}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#000000fa;backdrop-filter:blur(10px);border-top:1px solid #222;display:flex;justify-content:space-around;padding:10px 0 calc(10px + env(safe-area-inset-bottom));z-index:90}
.bottom-nav div{font-size:10px;color:#666;text-align:center;cursor:pointer;padding:8px 14px;border-radius:12px;min-width:60px}
.bottom-nav div.active{color:#0096B0;background:#0096B01f;font-weight:800}
.modal{position:fixed;inset:0;background:#000000f0;display:none;align-items:flex-end;justify-content:center;z-index:200}
.modal-box{background:#171717;border-radius:22px 22px 0 0;width:100%;max-width:500px;padding:20px;max-height:88vh;overflow-y:auto;border-top:3px solid #0096B0}
input,select{width:100%;background:#0a0a0a;border:1.5px solid #333;padding:13px;border-radius:12px;color:#fff;margin:6px 0;font-size:14px}
.bg{background:radial-gradient(circle at 50% 0%,rgba(0,150,176,0.22),transparent 50%),#070707;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:12px}
.card-login{background:#121212;border:1px solid rgba(0,150,176,0.3);border-radius:20px;padding:22px;width:100%;max-width:400px}
.tabs{display:flex;gap:6px;margin:12px 0}.tab{flex:1;padding:10px;border-radius:20px;border:1px solid #333;background:#111;color:#888;font-weight:700;font-size:12px;cursor:pointer;text-align:center}
.tab.active{background:#0096B0;color:#fff;border-color:#0096B0}
#sigCanvas{border:2px dashed #0096B0;border-radius:12px;background:#000;width:100%;height:140px;touch-action:none}
.badge-stock{position:absolute;top:8px;right:8px;font-size:10px;background:#000000cc;padding:4px 8px;border-radius:10px;border:1px solid #333}
#reader video{border-radius:14px!important}
</style></head><body>

<div id="authPage" class="bg"><div class="card-login">
<div style="text-align:center"><div class="logo" style="margin:0 auto 10px">LO</div><div style="font-weight:800;letter-spacing:3px">LONMA ORBIT</div><div style="color:#0096B0;font-size:9px;letter-spacing:3px;margin-top:3px">v2.3 BARCODE • M-PESA • PDF PRO</div></div>
<div class="tabs"><div class="tab active" id="tab-login" onclick="switchAuth('login')">LOGIN</div><div class="tab" id="tab-signup" onclick="switchAuth('signup')">CREATE</div></div>
<div id="loginBox"><input id="user" placeholder="Username"><input id="pass" type="password" placeholder="Password"><div style="display:flex;gap:8px;margin:10px 0;font-size:11px;color:#aaa"><input type="checkbox" id="agree" style="width:16px"><label>I agree to Terms</label></div><div id="err" style="color:#ff4444;font-size:12px;display:none"></div><button class="btn" onclick="doLogin()">LOGIN →</button><div style="background:#000;border:1px dashed #333;border-radius:10px;padding:10px;margin-top:10px;font-size:11px;color:#888"><div onclick="fill('admin','Lonma@2026')" style="cursor:pointer;padding:4px 0">👑 admin / Lonma@2026</div><div onclick="fill('cashier1','1234')" style="cursor:pointer">💰 cashier1 / 1234</div></div></div>
<div id="signupBox" style="display:none"><input id="s-name" placeholder="Full Name"><input id="s-user" placeholder="Username"><input id="s-pass" type="password" placeholder="Password"><select id="s-role"><option value="Cashier">Cashier</option><option value="Manager">Manager</option><option value="Owner">Owner</option></select><select id="s-branch"><option value="lonma-westlands">LONMA Westlands HQ</option><option value="naivas">Naivas</option><option value="carrefour">Carrefour</option><option value="chandarana">Chandarana</option><option value="all">All Branches</option></select><div style="margin:12px 0"><small style="color:#0096B0;font-weight:800;font-size:10px">✍️ DRAW SIGNATURE</small><canvas id="sigCanvas"></canvas><div style="display:flex;gap:6px;margin-top:6px"><button class="btn" style="flex:1;padding:8px;background:#111;color:#888;font-size:11px" onclick="clearSig()">Clear</button></div><small id="sigStatus" style="color:#666;font-size:10px">Draw with finger</small></div><div style="display:flex;gap:8px;margin:10px 0;font-size:11px;color:#aaa"><input type="checkbox" id="agree2" style="width:16px"><label>Legally binding</label></div><div id="err2" style="color:#ff4444;font-size:12px;display:none"></div><button class="btn" style="background:#FFD700;color:#000" onclick="doSignup()">✍️ SIGN & CREATE</button></div>
</div></div>

<div id="mainPage" style="display:none">
<div class="header"><div class="logo">LO</div><div style="flex:1;min-width:0"><div id="bName" style="font-weight:900;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">LONMA Westlands</div><div id="uInfo" style="color:#0096B0;font-size:11px">Marlon • Cashier • Signed • M-Pesa • Scanner Ready</div></div><button onclick="showUsers()" style="background:#111;border:1px solid #333;color:#ccc;padding:8px 12px;border-radius:20px;font-size:11px;font-weight:700;flex-shrink:0">Users</button><button onclick="logout()" style="background:#111;border:1px solid #333;color:#666;padding:8px 10px;border-radius:20px;font-size:11px;flex-shrink:0">Logout</button></div>

<div class="card"><div style="display:flex;justify-content:space-between;align-items:center"><small style="color:#0096B0;font-weight:900;font-size:10px;letter-spacing:1.5px">BRANCHES - 7/7 ONLINE →</small><small style="color:#555;font-size:10px" onclick="loadBranches()">↻ Refresh</small></div><div class="branch-scroll" id="branchList" style="margin-top:10px"></div></div>

<div class="stats">
<div class="stat"><small style="color:#777;font-size:10px;font-weight:800;letter-spacing:1px">STOCK VALUE</small><b id="stockV" style="color:#0096B0;font-size:16px;display:block;margin-top:4px">KES 0</b><small id="stockCount" style="color:#555;font-size:10px">0 SKUs</small></div>
<div class="stat"><small style="color:#777;font-size:10px;font-weight:800;letter-spacing:1px">TODAY SALES</small><b id="salesV" style="color:#FFD700;font-size:16px;display:block;margin-top:4px">KES 0</b><small id="salesCount" style="color:#888;font-size:10px">0 receipts</small></div>
<div class="stat"><small style="color:#777;font-size:10px;font-weight:800;letter-spacing:1px">ITEMS</small><b id="itemsV" style="font-size:16px;display:block;margin-top:4px">0</b><small id="lowStock" style="color:#ff4444;font-size:10px"></small></div>
</div>

<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center"><small style="color:#0096B0;font-weight:900;font-size:10px;letter-spacing:1.5px">CATEGORIES</small><small style="color:#555;font-size:10px" id="resultCount">6 items</small></div>
<div class="cat-scroll" id="catTabs" style="margin:10px 0">
<div class="cat active" style="background:#fff;color:#000" onclick="filterCat('ALL',this)">ALL</div>
<div class="cat" style="background:#FF9800;color:#000" onclick="filterCat('FOOD',this)">🍞 FOOD</div>
<div class="cat" style="background:#0096B0;color:#fff" onclick="filterCat('DRINKS',this)">🥤 DRINKS</div>
<div class="cat" style="background:#9C27B0;color:#fff" onclick="filterCat('UTENSILS',this)">🍳 UTENSILS</div>
<div class="cat" style="background:#FFD700;color:#000" onclick="filterCat('ELECTRONICS',this)">🔌 ELECTRONICS</div>
</div>
<div style="display:flex;gap:8px"><div style="flex:1;position:relative"><input id="search" placeholder="🔍 Search product or barcode..." onkeyup="renderProducts()" style="padding-left:14px"><span style="position:absolute;right:12px;top:50%;transform:translateY(-50%);color:#555;font-size:12px;cursor:pointer" onclick="clearSearch()">✕</span></div><button onclick="openScan()" style="background:#0096B0;border:none;color:#fff;padding:0 18px;border-radius:12px;font-weight:900;font-size:13px;flex-shrink:0">📷 SCAN</button></div>
<div class="products" id="plist" style="margin-top:12px"></div>
</div>

<div class="card" style="border:1.5px solid rgba(0,150,176,0.35);box-shadow:0 4px 20px rgba(0,150,176,0.15)">
<div style="display:flex;justify-content:space-between;align-items:center"><b style="font-size:14px">🛒 CART - <span id="cartBranch" style="color:#0096B0">LONMA</span></b><div style="display:flex;gap:6px"><button onclick="clearCart()" style="background:#111;border:1px solid #333;color:#888;padding:6px 10px;border-radius:20px;font-size:10px">Clear</button><button onclick="showSales()" style="background:#111;border:1px solid #333;color:#888;padding:6px 10px;border-radius:20px;font-size:10px">History</button></div></div>
<div id="cart" style="margin:12px 0;color:#666;font-size:13px">Cart empty - Scan or Tap + ADD</div>
<div style="border-top:1px dashed #333;margin:12px 0"></div>
<div style="display:flex;justify-content:space-between;font-size:12px;color:#888"><span>Subtotal</span><span id="subtotal">KES 0</span></div>
<div style="display:flex;justify-content:space-between;font-size:12px;color:#888;margin:4px 0"><span>VAT 16%</span><span id="vat">KES 0</span></div>
<div style="display:flex;justify-content:space-between;margin-top:10px;font-size:20px;font-weight:900"><b>TOTAL</b><b id="total" style="color:#0096B0">KES 0</b></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px">
<button onclick="setPay('cash')" id="pay-cash" style="padding:12px;border-radius:12px;border:1.5px solid #333;background:#1a1a1a;color:#888;font-weight:800;font-size:12px">💵 CASH</button>
<button onclick="setPay('mpesa')" id="pay-mpesa" style="padding:12px;border-radius:12px;border:1.5px solid #0096B0;background:#0096B01a;color:#0096B0;font-weight:800;font-size:12px">📱 M-PESA</button>
</div>
<input id="mpesa-phone" placeholder="M-Pesa: 07xx or 2547xx" style="display:block;margin-top:8px" value="254">
<button class="btn" onclick="checkout()" style="margin-top:10px;font-size:15px;line-height:1.2">💳 CHECKOUT - Signed by Marlon<br><small style="font-size:11px;opacity:0.85">M-Pesa • Barcode • PDF Receipt</small></button>
</div>

<div class="card" id="usersBox" style="display:none"><b>👥 USERS - Signed</b><div id="usersList" style="margin-top:10px"></div></div>

<div class="fab" onclick="openAddModal()">+</div>
<div class="bottom-nav">
<div class="active" onclick="window.scrollTo({top:0,behavior:'smooth'})">🏠<br>Home</div>
<div onclick="openAddModal()">➕<br>Add</div>
<div onclick="document.getElementById('cart').scrollIntoView({behavior:'smooth'})">🛒<br>Cart (<span id="cartCount">0</span>)</div>
<div onclick="openScan()">📷<br>Scan</div>
<div onclick="showUsers()">👥<br>Users</div>
</div>

<!-- MODALS -->
<div class="modal" id="addModal" onclick="if(event.target==this)closeAddModal()"><div class="modal-box"><h3>➕ ADD PRODUCT - With Barcode</h3><small style="color:#888">To <span id="modalBranch">LONMA</span></small><input id="p-name" placeholder="Name - e.g., Bread Festive 400g"><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px"><input id="p-price" type="number" placeholder="Price KES"><input id="p-stock" type="number" placeholder="Stock Qty"></div><select id="p-cat"><option value="FOOD">🍞 FOOD</option><option value="DRINKS">🥤 DRINKS</option><option value="UTENSILS">🍳 UTENSILS</option><option value="ELECTRONICS">🔌 ELECTRONICS</option></select><div style="display:flex;gap:8px"><input id="p-barcode" placeholder="Barcode - e.g., 6161101100123"><button onclick="scanBarcodeForProduct()" style="background:#0096B0;border:none;color:#fff;padding:0 14px;border-radius:12px;font-size:12px;font-weight:800;flex-shrink:0">📷 SCAN</button></div><input id="p-emoji" placeholder="Emoji - e.g., 🍞 (optional)"><button class="btn" style="background:#FFD700;color:#000;margin-top:12px" onclick="addProduct()">💾 SAVE PRODUCT</button><button class="btn" style="background:#111;color:#666;margin-top:8px" onclick="closeAddModal()">Cancel</button></div></div>

<div class="modal" id="scanModal" onclick="if(event.target==this)closeScan()"><div class="modal-box" style="text-align:center"><div style="display:flex;justify-content:space-between;align-items:center"><h3>📷 SCAN BARCODE</h3><button onclick="closeScan()" style="background:#111;border:1px solid #333;color:#888;padding:6px 12px;border-radius:20px;font-size:11px">✕ Close</button></div><div id="reader" style="width:100%;margin:14px 0;border-radius:14px;overflow:hidden;background:#000;min-height:280px;border:2px solid #222"></div><small style="color:#888">Point camera at product barcode<br>Flashlight: Allow camera permission</small><div id="scanResult" style="margin-top:12px;color:#0096B0;font-weight:800;background:#0096B01a;padding:10px;border-radius:10px;display:none"></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px"><button class="btn" style="background:#111;color:#888" onclick="closeScan()">Cancel</button><button class="btn" style="background:#FFD700;color:#000" onclick="manualBarcode()">⌨️ Type Barcode</button></div></div></div>

<div class="modal" id="scanProductModal" onclick="if(event.target==this)closeScanProduct()"><div class="modal-box" style="text-align:center"><h3>📷 SCAN FOR PRODUCT</h3><div id="reader2" style="width:100%;margin:14px 0;border-radius:14px;overflow:hidden;background:#000;min-height:280px"></div><div id="scanResult2" style="margin-top:10px;color:#0096B0;font-weight:800"></div><button class="btn" style="background:#111;color:#888;margin-top:12px" onclick="closeScanProduct()">Close</button></div></div>

<div class="modal" id="salesModal" onclick="if(event.target==this)closeSales()"><div class="modal-box"><div style="display:flex;justify-content:space-between;align-items:center"><h3>📊 TODAY'S SALES - <span id="salesBranch">LONMA</span></h3><button onclick="closeSales()" style="background:#111;border:1px solid #333;color:#888;padding:6px 10px;border-radius:20px;font-size:11px">Close ✕</button></div><div id="salesList" style="margin-top:12px"></div></div></div>

<div class="modal" id="receiptModal"><div class="modal-box" style="text-align:center"><div style="width:64px;height:64px;background:#0096B0;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:32px">✅</div><h2>Sale Complete!</h2><small id="payMethodShow" style="color:#0096B0">M-Pesa Paid</small><div id="receiptContent" style="background:#000;border:1px solid #222;border-radius:14px;padding:14px;margin:14px 0;text-align:left;font-family:monospace;font-size:12px;line-height:1.5"></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px"><button class="btn" style="background:#111;color:#aaa" onclick="closeReceipt()">🛒 New Sale</button><button class="btn" style="background:#FFD700;color:#000" onclick="downloadPDF()">📄 PDF Receipt</button></div></div></div>
</div>

<script>
let current='lonma-westlands'; let branches={}; let cart=[]; let activeCat='ALL'; let me=null; let signatureData=''; let payMethod='mpesa'; let lastSale=null;
function switchAuth(t){document.getElementById('tab-login').classList.remove('active');document.getElementById('tab-signup').classList.remove('active');document.getElementById('loginBox').style.display='none';document.getElementById('signupBox').style.display='none';if(t=='login'){document.getElementById('tab-login').classList.add('active');document.getElementById('loginBox').style.display='block'}else{document.getElementById('tab-signup').classList.add('active');document.getElementById('signupBox').style.display='block';setTimeout(initSig,100);}}
function fill(u,p){document.getElementById('user').value=u; document.getElementById('pass').value=p;}
function setPay(m){payMethod=m; document.getElementById('pay-cash').style.borderColor=m=='cash'?'#FFD700':'#333'; document.getElementById('pay-cash').style.color=m=='cash'?'#FFD700':'#888'; document.getElementById('pay-mpesa').style.borderColor=m=='mpesa'?'#0096B0':'#333'; document.getElementById('pay-mpesa').style.color=m=='mpesa'?'#0096B0':'#888';}
async function doLogin(){let u=document.getElementById('user').value; let p=document.getElementById('pass').value; let agree=document.getElementById('agree').checked; if(!agree){document.getElementById('err').style.display='block';document.getElementById('err').innerText='Accept Terms';return} let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})}); if(!r.ok){document.getElementById('err').style.display='block';document.getElementById('err').innerText='Wrong';return} me=await r.json(); localStorage.setItem('lonma_user',JSON.stringify(me)); showMain();}
async function doSignup(){let name=document.getElementById('s-name').value; let user=document.getElementById('s-user').value; let pass=document.getElementById('s-pass').value; let role=document.getElementById('s-role').value; let branch=document.getElementById('s-branch').value; let agree=document.getElementById('agree2').checked; if(!name||!user||!pass){document.getElementById('err2').style.display='block';document.getElementById('err2').innerText='Fill all';return} if(!agree){document.getElementById('err2').style.display='block';document.getElementById('err2').innerText='Accept Terms';return} if(!signatureData){document.getElementById('err2').style.display='block';document.getElementById('err2').innerText='Draw signature';return} let r=await fetch('/api/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:user,password:pass,name:name,role:role,branch:branch,signature:signatureData})}); if(!r.ok){let d=await r.json(); document.getElementById('err2').style.display='block';document.getElementById('err2').innerText=d.detail;return} alert('✅ Created'); switchAuth('login'); document.getElementById('user').value=user;}
function showMain(){document.getElementById('authPage').style.display='none';document.getElementById('mainPage').style.display='block';document.getElementById('uInfo').innerText=me.name+' • '+me.role+' • Signed • Scanner Ready'; loadBranches();}
function logout(){localStorage.removeItem('lonma_user');location.reload();}
function clearSearch(){document.getElementById('search').value=''; renderProducts();}

let html5QrcodeScanner=null; let isScanning=false;
let html5QrcodeScanner2=null; let isScanning2=false;

async function openScan(){
  document.getElementById('scanModal').style.display='flex';
  document.getElementById('scanResult').style.display='block';
  document.getElementById('scanResult').innerText='📷 Starting camera... Please allow permission';

  try{
    html5QrcodeScanner = new Html5Qrcode("reader");
    const cameras = await Html5Qrcode.getCameras();
    if(cameras && cameras.length){
      await html5QrcodeScanner.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 280, height: 150 }, aspectRatio: 1.5 },
        (decodedText) => {
          document.getElementById('scanResult').innerText='✅ Scanned: '+decodedText;
          if(navigator.vibrate) navigator.vibrate([100,50,100]);
          // Find product by barcode or id
          let found = branches[current].products.find(p=> p.barcode===decodedText || p.id===decodedText);
          if(!found){
            // Try partial match
            found = branches[current].products.find(p=> decodedText.includes(p.barcode) || p.barcode.includes(decodedText));
          }
          if(found){
            addCart(found.id);
            document.getElementById('scanResult').innerText='✅ Added: '+found.name+' - KES '+found.price;
            setTimeout(()=>closeScan(), 1300);
          } else {
            document.getElementById('scanResult').innerText='⚠️ Barcode: '+decodedText+'\\nNot in stock - Add it via + button';
          }
        },
        (err)=>{}
      );
      isScanning=true;
    } else {
      document.getElementById('scanResult').innerText='❌ No camera found - Use HTTPS + Allow permission';
    }
  }catch(err){
    document.getElementById('scanResult').innerText='❌ Camera error: '+err.message+'\\nNeed HTTPS & Camera permission. Try manual entry.';
  }
}

async function closeScan(){
  document.getElementById('scanModal').style.display='none';
  if(html5QrcodeScanner && isScanning){
    try{ await html5QrcodeScanner.stop(); await html5QrcodeScanner.clear(); }catch(e){}
    isScanning=false;
  }
}

async function scanBarcodeForProduct(){
  document.getElementById('scanProductModal').style.display='flex';
  document.getElementById('scanResult2').innerText='Scanning barcode for new product...';
  try{
    html5QrcodeScanner2 = new Html5Qrcode("reader2");
    await html5QrcodeScanner2.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: { width: 250, height: 120 } },
      (decodedText)=>{
        document.getElementById('p-barcode').value=decodedText;
        document.getElementById('scanResult2').innerText='✅ Barcode: '+decodedText;
        if(navigator.vibrate) navigator.vibrate(50);
        setTimeout(()=>closeScanProduct(), 1000);
      },
      ()=>{}
    );
    isScanning2=true;
  }catch(err){ document.getElementById('scanResult2').innerText='❌ '+err.message; }
}

async function closeScanProduct(){
  document.getElementById('scanProductModal').style.display='none';
  if(html5QrcodeScanner2 && isScanning2){
    try{ await html5QrcodeScanner2.stop(); await html5QrcodeScanner2.clear(); }catch(e){}
    isScanning2=false;
  }
}

function manualBarcode(){
  let code = prompt('Enter barcode manually:','');
  if(code){
    document.getElementById('scanResult').innerText='⌨️ Manual: '+code;
    let found = branches[current].products.find(p=> p.barcode===code || p.id===code);
    if(found){ addCart(found.id); setTimeout(()=>closeScan(),800); }
    else { document.getElementById('p-barcode').value=code; closeScan(); openAddModal(); alert('Barcode '+code+' not found - Adding as new product'); }
  }
}

async function loadBranches(){
  let r=await fetch('/api/supermarkets'); branches=await r.json();
  document.getElementById('branchList').innerHTML=Object.entries(branches).map(([id,b])=>`<div class="pill ${id==current?'active':''}" onclick="selectBranch('${id}')"><span>${b.icon}</span><span>${b.name}</span></div>`).join('');
  let b=branches[current]; document.getElementById('bName').innerText=b.name; document.getElementById('cartBranch').innerText=b.name; document.getElementById('modalBranch').innerText=b.name; document.getElementById('salesBranch').innerText=b.name; document.getElementById('itemsV').innerText=b.products.length; document.getElementById('stockCount').innerText=b.products.length+' SKUs'; let tot=0; b.products.forEach(p=>tot+=p.price*p.stock); document.getElementById('stockV').innerText='KES '+tot.toLocaleString(); let low=b.products.filter(p=>p.stock<20).length; document.getElementById('lowStock').innerText=low?`⚠️ ${low} low`:'✅ OK'; renderProducts(); loadSales();
}
function selectBranch(id){current=id; loadBranches();}
function filterCat(c,el){activeCat=c; document.querySelectorAll('#catTabs.cat').forEach(x=>x.classList.remove('active')); el.classList.add('active'); renderProducts();}
function renderProducts(){
  let b=branches[current]; let q=document.getElementById('search').value.toLowerCase();
  let list=b.products.filter(p=>(activeCat=='ALL'||p.cat==activeCat)&&(p.name.toLowerCase().includes(q)||(p.barcode&&p.barcode.includes(q))||p.id.toLowerCase().includes(q)));
  document.getElementById('resultCount').innerText=list.length+' items';
  let col={"FOOD":"#FF9800","DRINKS":"#0096B0","UTENSILS":"#9C27B0","ELECTRONICS":"#FFD700"};
  document.getElementById('plist').innerHTML=list.map(p=>`<div class="prod" onclick="addCart('${p.id}')"><div class="badge-stock" style="color:${p.stock<20?'#ff5555':'#777'}">${p.stock} left</div><div style="font-size:26px;margin:6px 0 4px">${p.emoji||'📦'}</div><div><small style="background:${col[p.cat]};color:#000;padding:3px 8px;border-radius:6px;font-size:9px;font-weight:900">${p.cat}</small></div><div style="font-weight:700;margin:8px 0 2px;font-size:12px;line-height:1.3;min-height:32px">${p.name}</div><div style="color:#888;font-size:9px;font-family:monospace">🔢 ${p.barcode||p.id}</div><div style="color:#0096B0;font-weight:900;font-size:15px;margin-top:2px">KES ${p.price}</div><div style="margin-top:8px;background:#0096B0;color:#fff;text-align:center;padding:8px;border-radius:10px;font-size:11px;font-weight:800">+ ADD</div></div>`).join('') || `<div style="grid-column:span 2;text-align:center;padding:30px 20px;color:#555;background:#141414;border-radius:14px;border:1px dashed #333"><div style="font-size:30px">🔍</div><div style="margin-top:8px">No products - barcode: ${q}</div><small>Tap + to add this barcode</small></div>`;
}
function addCart(pid){let p=branches[current].products.find(x=>x.id==pid); if(p.stock<=0) return alert('Out of stock: '+p.name); let c=cart.find(x=>x.product_id==pid); if(c){ if(c.qty>=p.stock) return alert('Max stock: '+p.stock); c.qty++; } else cart.push({product_id:pid,qty:1,name:p.name,price:p.price,emoji:p.emoji||'📦',barcode:p.barcode||p.id}); renderCart(); if(navigator.vibrate) navigator.vibrate(30);}
function renderCart(){document.getElementById('cartCount').innerText=cart.reduce((a,b)=>a+b.qty,0); if(cart.length==0){document.getElementById('cart').innerHTML='<div style="text-align:center;padding:18px;color:#555"><div style="font-size:24px">🛒</div><div>Cart empty</div><small>Scan barcode or tap + ADD</small></div>'; document.getElementById('total').innerText='KES 0'; document.getElementById('subtotal').innerText='KES 0'; document.getElementById('vat').innerText='KES 0'; return} let total=0; document.getElementById('cart').innerHTML=cart.map(i=>{total+=i.price*i.qty; return `<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #222"><div style="display:flex;align-items:center;gap:10px;flex:1;min-width:0"><span style="font-size:18px">${i.emoji}</span><div style="min-width:0"><div style="font-weight:700;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${i.name}</div><div style="color:#666;font-size:10px;font-family:monospace">${i.barcode} • KES ${i.price}</div></div></div><div style="display:flex;align-items:center;gap:8px;flex-shrink:0"><button onclick="changeQty('${i.product_id}',-1)" style="width:30px;height:30px;border-radius:50%;border:1px solid #333;background:#111;color:#fff;font-weight:900">−</button><b style="min-width:22px;text-align:center">${i.qty}</b><button onclick="changeQty('${i.product_id}',1)" style="width:30px;height:30px;border-radius:50%;background:#0096B0;border:none;color:#fff;font-weight:900">+</button><span style="color:#0096B0;font-weight:900;min-width:68px;text-align:right;font-size:13px">KES ${i.price*i.qty}</span></div></div>`}).join(''); let vat=Math.round(total*0.16); let sub=total-vat; document.getElementById('subtotal').innerText='KES '+sub.toLocaleString(); document.getElementById('vat').innerText='KES '+vat.toLocaleString(); document.getElementById('total').innerText='KES '+total.toLocaleString();}
function changeQty(pid,d){let c=cart.find(x=>x.product_id==pid); if(!c) return; let p=branches[current].products.find(x=>x.id==pid); c.qty+=d; if(c.qty<=0) cart=cart.filter(x=>x.product_id!=pid); if(c.qty>p.stock) c.qty=p.stock; renderCart();}
function clearCart(){cart=[]; renderCart();}
async function checkout(){
  if(cart.length==0) return alert('Cart empty');
  let phone=document.getElementById('mpesa-phone').value;
  if(payMethod=='mpesa' && phone.length<9) return alert('Enter M-Pesa phone');
  let btn=event.target; btn.innerHTML='⏳ Processing '+payMethod.toUpperCase()+'...'; btn.disabled=true;
  await new Promise(r=>setTimeout(r,900));
  let r=await fetch(`/api/${current}/checkout`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cart.map(c=>({product_id:c.product_id,qty:c.qty})))});
  let d=await r.json(); lastSale=d;
  document.getElementById('payMethodShow').innerText=payMethod=='mpesa'?'📱 M-Pesa Paid: '+phone:'💵 Cash Paid';
  document.getElementById('receiptContent').innerHTML=`<div style="text-align:center"><b style="font-size:14px">LONMA ORBIT</b><br>${branches[current].name}<br><small style="color:#888">${new Date().toLocaleString()}<br>Cashier: ${me?me.name:'Marlon'} ✍️ Signed</small></div><hr style="border:1px dashed #333;margin:12px 0"><div>Receipt: <b style="color:#0096B0">${d.receipt}</b></div><div>Payment: <b>${payMethod.toUpperCase()}</b> ${payMethod=='mpesa'?'• '+phone:''}</div><hr style="border:1px dashed #333;margin:12px 0">${d.items.map(i=>`<div style="display:flex;justify-content:space-between"><span>${i.name} x${i.qty}</span><span>KES ${i.price*i.qty}</span></div>`).join('')}<hr style="border:1px dashed #333;margin:12px 0"><div style="display:flex;justify-content:space-between;font-size:16px;font-weight:900"><span>TOTAL</span><span style="color:#0096B0">KES ${d.total}</span></div><div style="text-align:center;margin-top:12px"><small style="color:#888">Thank you! Karibu tena!<br>VAT inclusive • Legal receipt<br>Signature on file ✍️<br>Barcodes: ${d.items.map(i=>i.name).join(', ')}</small></div>`;
  document.getElementById('receiptModal').style.display='flex'; cart=[]; renderCart(); loadBranches(); btn.innerHTML='💳 CHECKOUT - Signed by Marlon<br><small style="font-size:11px;opacity:0.85">M-Pesa • Barcode • PDF Receipt</small>'; btn.disabled=false;
}
function closeReceipt(){document.getElementById('receiptModal').style.display='none';}
function downloadPDF(){
  if(!lastSale){ alert('No sale'); return; }
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  doc.setFontSize(18); doc.text("LONMA ORBIT - RECEIPT", 10, 15);
  doc.setFontSize(10); doc.text(`Branch: ${branches[current].name}`, 10, 25);
  doc.text(`Receipt: ${lastSale.receipt}`, 10, 32); doc.text(`Date: ${new Date().toLocaleString()}`, 10, 39);
  doc.text(`Cashier: ${me?me.name:'Marlon'} - Signed`, 10, 46); doc.text(`Payment: ${payMethod.toUpperCase()}`, 10, 53);
  let y=65; lastSale.items.forEach(i=>{ doc.text(`${i.name} x${i.qty} - KES ${i.price*i.qty}`, 10, y); y+=7; });
  doc.setFontSize(14); doc.text(`TOTAL: KES ${lastSale.total}`, 10, y+10);
  doc.setFontSize(9); doc.text("Thank you! Karibu tena! VAT inclusive - Legal receipt", 10, y+20);
  doc.save(`LONMA-${lastSale.receipt}.pdf`);
}
function openAddModal(){document.getElementById('addModal').style.display='flex';}
function closeAddModal(){document.getElementById('addModal').style.display='none';}
async function addProduct(){
  let name=document.getElementById('p-name').value; let price=parseFloat(document.getElementById('p-price').value); let stock=parseInt(document.getElementById('p-stock').value); let cat=document.getElementById('p-cat').value; let barcode=document.getElementById('p-barcode').value||''; let emoji=document.getElementById('p-emoji').value||'📦';
  if(!name||!price||!stock) return alert('Fill Name, Price, Stock');
  let r=await fetch(`/api/${current}/products`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,price,stock,cat,barcode})});
  let p=await r.json(); p.emoji=emoji; p.barcode=barcode; let idx=branches[current].products.findIndex(x=>x.id==p.id); if(idx>=0){ branches[current].products[idx].emoji=emoji; branches[current].products[idx].barcode=barcode; }
  closeAddModal(); document.getElementById('p-name').value=''; document.getElementById('p-price').value=''; document.getElementById('p-stock').value=''; document.getElementById('p-barcode').value=''; document.getElementById('p-emoji').value=''; loadBranches(); alert('✅ Added: '+name+' - Barcode: '+(barcode||p.id));
}
async function loadSales(){let r=await fetch(`/api/${current}/sales`); let s=await r.json(); let tot=s.reduce((a,b)=>a+b.total,0); document.getElementById('salesV').innerText='KES '+tot.toLocaleString(); document.getElementById('salesCount').innerText=s.length+' receipts';}
async function showSales(){await loadSales(); let r=await fetch(`/api/${current}/sales`); let s=await r.json(); document.getElementById('salesList').innerHTML=s.slice(0,30).map(x=>`<div style="padding:12px 0;border-bottom:1px solid #222"><div style="display:flex;justify-content:space-between;align-items:center"><b style="color:#0096B0">${x.receipt}</b><b>KES ${x.total}</b></div><div style="color:#888;font-size:11px;margin-top:4px">${x.items.map(i=>i.name+' x'+i.qty).join(', ')} • ${new Date(x.time).toLocaleTimeString()} • ${x.payment||'M-Pesa'}</div></div>`).join('')||'<div style="text-align:center;padding:20px;color:#555">No sales today</div>'; document.getElementById('salesModal').style.display='flex';}
function closeSales(){document.getElementById('salesModal').style.display='none';}
async function showUsers(){let box=document.getElementById('usersBox'); box.style.display=box.style.display=='none'?'block':'none'; let r=await fetch('/api/users'); let u=await r.json(); document.getElementById('usersList').innerHTML=u.map(x=>`<div style="padding:10px 0;border-bottom:1px solid #222;display:flex;justify-content:space-between;align-items:center"><span><b>${x.name}</b><br><small style="color:#888">${x.role} • ${x.branch} • ${x.hasSignature?'✍️ Signed':''}</small></span><small style="color:#555">${x.created?.substring(0,10)}</small></div>`).join(''); if(box.style.display=='block') box.scrollIntoView({behavior:'smooth'});}
let canvas, ctx, drawing=false;
function initSig(){canvas=document.getElementById('sigCanvas'); if(!canvas) return; ctx=canvas.getContext('2d'); let rect=canvas.getBoundingClientRect(); canvas.width=rect.width*2; canvas.height=140*2; ctx.scale(2,2); ctx.strokeStyle='#0096B0'; ctx.lineWidth=2.5; ctx.lineCap='round'; ctx.lineJoin='round'; function pos(e){let r=canvas.getBoundingClientRect(); let x=(e.touches?e.touches[0].clientX:e.clientX)-r.left; let y=(e.touches?e.touches[0].clientY:e.clientY)-r.top; return {x,y};} canvas.addEventListener('mousedown', e=>{drawing=true; let p=pos(e); ctx.beginPath(); ctx.moveTo(p.x,p.y);}); canvas.addEventListener('mousemove', e=>{if(!drawing) return; let p=pos(e); ctx.lineTo(p.x,p.y); ctx.stroke();}); canvas.addEventListener('mouseup', ()=>{drawing=false; saveSig();}); canvas.addEventListener('mouseleave', ()=>{drawing=false;}); canvas.addEventListener('touchstart', e=>{e.preventDefault(); drawing=true; let p=pos(e); ctx.beginPath(); ctx.moveTo(p.x,p.y);}); canvas.addEventListener('touchmove', e=>{e.preventDefault(); if(!drawing) return; let p=pos(e); ctx.lineTo(p.x,p.y); ctx.stroke();}); canvas.addEventListener('touchend', e=>{e.preventDefault(); drawing=false; saveSig();});}
function clearSig(){if(!ctx) return; ctx.clearRect(0,0,canvas.width,canvas.height); signatureData=''; document.getElementById('sigStatus').innerText='Cleared'; document.getElementById('sigStatus').style.color='#666';}
function saveSig(){if(!canvas) return; signatureData=canvas.toDataURL(); document.getElementById('sigStatus').innerText='✅ Signature captured - Legal'; document.getElementById('sigStatus').style.color='#0096B0';}
(function(){let s=localStorage.getItem('lonma_user'); if(s){me=JSON.parse(s); showMain();}})();
</script></body></html>
    """
