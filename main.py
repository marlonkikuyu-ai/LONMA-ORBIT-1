from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, sqlite3, json, datetime, requests, base64, time, re
from threading import Thread
from collections import defaultdict

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DARAJA_KEY = os.getenv("DARAJA_KEY",""); DARAJA_SECRET=os.getenv("DARAJA_SECRET","")
DARAJA_SHORTCODE=os.getenv("DARAJA_SHORTCODE","174379"); DARAJA_PASSKEY=os.getenv("DARAJA_PASSKEY","")
DARAJA_CALLBACK=os.getenv("CALLBACK_URL","https://app.lonmaorbit.co.ke/mpesa/callback")
USE_PROD=os.getenv("DARAJA_ENV","sandbox")=="production"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD","Lonma#2026!Secure")

FAILED = defaultdict(list); BLOCKED = {}
def is_blocked(ip):
    now=time.time()
    FAILED[ip]=[t for t in FAILED[ip] if now-t<300]
    if ip in BLOCKED and now < BLOCKED[ip]: return True
    if len(FAILED[ip])>=5:
        BLOCKED[ip]=now+900; return True
    return False
def record_fail(ip): FAILED[ip].append(time.time())
def clean_input(s, maxlen=500):
    if not isinstance(s,str): return ""
    s=s.strip()[:maxlen]; s=re.sub(r'[<>\"\'`;]', '', s); return s

@app.middleware("http")
async def security_middleware(request, call_next):
    path=request.url.path.lower()
    bad=[".env","wp-admin","phpmyadmin",".git","config","admin.php",".sql","wp-login"]
    if any(b in path for b in bad): return HTMLResponse("Not Found", status_code=404)
    response=await call_next(request)
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["X-Frame-Options"]="DENY"
    response.headers["X-XSS-Protection"]="1; mode=block"
    response.headers["Strict-Transport-Security"]="max-age=31536000"
    return response

conn=sqlite3.connect("lonma.db",check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, code TEXT, image TEXT, category TEXT, stock INTEGER)")
conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, order_no TEXT, name TEXT, phone TEXT, area TEXT, location TEXT, items TEXT, total INTEGER, status TEXT, created TEXT, mpesa_receipt TEXT, checkout_id TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE, name TEXT, password TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, name TEXT, rating INTEGER, text TEXT, created TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS promos (code TEXT PRIMARY KEY, discount INTEGER)")
conn.execute("CREATE TABLE IF NOT EXISTS community_posts (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, phone TEXT, text TEXT, image TEXT, likes INTEGER DEFAULT 0, reposts INTEGER DEFAULT 0, created TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS community_comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, author TEXT, text TEXT, created TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS community_likes (post_id INTEGER, phone TEXT, UNIQUE(post_id, phone))")
cur=conn.cursor(); cur.execute("DELETE FROM products"); cur.execute("DELETE FROM promos")
cur.execute("INSERT OR IGNORE INTO promos VALUES ('LONMA10',10)"); cur.execute("INSERT OR IGNORE INTO promos VALUES ('WELCOME20',20)"); cur.execute("INSERT OR IGNORE INTO promos VALUES ('FREEDEL',100)")
PRODS=[
(1,"Diva Anti-Dandruff Pomade 250ml",250,"DIV-001","DIVA|#0A9EBB","Pomades",45),
(2,"Detrex Pine Drops Soap 110g",95,"DET-002","DETREX|#0F766E","Soaps",80),
(3,"Fresh Fri Cooking Oil 2L",890,"FRE-003","FRESH FRI|#B45309","Cooking Oils",50),
(4,"Detrex Citronella Soap 110g",95,"DET-004","DETREX|#0F766E","Soaps",100),
(5,"Sawa Men Lotion 72Hrs",320,"SAW-005","SAWA|#1E40AF","Lotions",12),
(6,"Detrex Cool Mint Soap 110g",95,"DET-006","DETREX|#0F766E","Soaps",4),
(7,"Diva Anti-Breakage Pomade 250ml",250,"DIV-007","DIVA|#0A9EBB","Pomades",30),
(8,"Sawa Cocoa Butter Lotion 72Hrs",320,"SAW-008","SAWA|#1E40AF","Lotions",28),
(9,"Detrex Germ Protection Soap 110g",95,"DET-009","DETREX|#0F766E","Soaps",60),
]
for pid,name,price,code,img,cat,stock in PRODS:
    cur.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?)",(pid,name,price,code,img,cat,stock))
cur.execute("SELECT COUNT(*) FROM community_posts")
if cur.fetchone()[0]==0:
    seeds=[
        ("LONMA ORBIT Official","0700000000","Welcome to LONMA Community. Share your shopping, recipes and reviews. Use #LONMA #Detrex #Diva","",42,5),
        ("Mary Wanjiru","0712345678","Just bought Detrex Pine Drops. My house smells amazing. Who else loves it? #Detrex #CleanHome", "DETREX|#0F766E",18,2),
        ("Kevin Otieno","0723456789","Fresh Fri Oil 2L for only 890. Best deal in Nairobi. #FreshFri #Deals","FRESH FRI|#B45309",25,4),
        ("Amina Hassan","0734567890","Diva Pomade made my hair so soft. Highly recommend. #Diva #HairCare","DIVA|#0A9EBB",31,3),
    ]
    for a,p,t,img,l,r in seeds:
        cur.execute("INSERT INTO community_posts (author,phone,text,image,likes,reposts,created) VALUES (?,?,?,?,?,?,?)",(a,p,t,img,l,r,datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
conn.commit()

def get_token():
    try:
        base="https://api.safaricom.co.ke" if USE_PROD else "https://sandbox.safaricom.co.ke"
        r=requests.get(f"{base}/oauth/v1/generate?grant_type=client_credentials",auth=(DARAJA_KEY,DARAJA_SECRET),timeout=10)
        return r.json().get("access_token")
    except: return None

@app.api_route("/mpesa/callback",methods=["GET","POST"])
async def callback(request:Request):
    try:
        data=await request.json(); stk=data.get("Body",{}).get("stkCallback",{})
        if stk.get("ResultCode")==0:
            receipt=""
            for it in stk.get("CallbackMetadata",{}).get("Item",[]):
                if it.get("Name")=="MpesaReceiptNumber": receipt=it.get("Value")
            conn.execute("UPDATE orders SET status='PAID', mpesa_receipt=? WHERE checkout_id=?",(receipt,stk.get("CheckoutRequestID",""))); conn.commit()
        return {"ResultCode":0,"ResultDesc":"Accepted"}
    except: return {"ResultCode":0,"ResultDesc":"Accepted"}

@app.get("/api/community/posts")
def get_posts(phone:str=""):
    cur=conn.cursor(); cur.execute("SELECT id,author,phone,text,image,likes,reposts,created FROM community_posts ORDER BY id DESC LIMIT 50")
    out=[]
    for r in cur.fetchall():
        cur2=conn.cursor(); cur2.execute("SELECT COUNT(*) FROM community_comments WHERE post_id=?",(r[0],)); cc=cur2.fetchone()[0]
        liked=False
        if phone:
            cur2.execute("SELECT 1 FROM community_likes WHERE post_id=? AND phone=?",(r[0],phone,)); liked=cur2.fetchone() is not None
        out.append({"id":r[0],"author":r[1],"phone":r[2],"text":r[3],"image":r[4],"likes":r[5],"reposts":r[6],"created":r[7],"comments":cc,"liked":liked})
    return out

@app.post("/api/community/post")
async def create_post(req:Request):
    d=await req.json(); text=clean_input(d.get("text",""),500); author=clean_input(d.get("author","Customer"),30); phone=clean_input(d.get("phone",""),15)
    if not text or len(text)<2: return {"status":"error"}
    conn.execute("INSERT INTO community_posts (author,phone,text,image,likes,reposts,created) VALUES (?,?,?,?,0,0,?)",(author,phone,text,"",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))); conn.commit()
    return {"status":"ok"}

@app.post("/api/community/like")
async def like_post(req:Request):
    d=await req.json()
    try: pid=int(d.get("post_id",0))
    except: return {"status":"error"}
    phone=clean_input(d.get("phone",""),15)
    cur=conn.cursor(); cur.execute("SELECT 1 FROM community_likes WHERE post_id=? AND phone=?",(pid,phone,))
    if cur.fetchone():
        conn.execute("DELETE FROM community_likes WHERE post_id=? AND phone=?",(pid,phone,)); conn.execute("UPDATE community_posts SET likes=likes-1 WHERE id=?",(pid,)); conn.commit(); return {"status":"unliked"}
    conn.execute("INSERT INTO community_likes VALUES (?,?)",(pid,phone,)); conn.execute("UPDATE community_posts SET likes=likes+1 WHERE id=?",(pid,)); conn.commit(); return {"status":"liked"}

@app.post("/api/community/repost")
async def repost(req:Request):
    d=await req.json()
    try: pid=int(d.get("post_id",0))
    except: return {"status":"error"}
    conn.execute("UPDATE community_posts SET reposts=reposts+1 WHERE id=?",(pid,)); conn.commit(); return {"status":"ok"}

@app.get("/api/community/comments/{pid}")
def get_comments(pid:int):
    cur=conn.cursor(); cur.execute("SELECT author,text,created FROM community_comments WHERE post_id=? ORDER BY id ASC",(pid,)); return [{"author":r[0],"text":r[1],"created":r[2]} for r in cur.fetchall()]

@app.post("/api/community/comment")
async def add_comment(req:Request):
    d=await req.json()
    try: pid=int(d.get("post_id",0))
    except: return {"status":"error"}
    conn.execute("INSERT INTO community_comments (post_id,author,text,created) VALUES (?,?,?,?)",(pid,clean_input(d.get("author","Customer"),30),clean_input(d.get("text",""),300),datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))); conn.commit()
    return {"status":"ok"}

@app.get("/api/community/trending")
def trending():
    cur=conn.cursor(); cur.execute("SELECT text FROM community_posts")
    tags={}
    for (t,) in cur.fetchall():
        for w in t.split():
            if w.startswith("#"):
                tags[w]=tags.get(w,0)+1
    sorted_tags=sorted(tags.items(), key=lambda x:-x[1])[:6]
    return [{"tag":k,"count":v} for k,v in sorted_tags] or [{"tag":"#LONMA","count":42},{"tag":"#Detrex","count":28},{"tag":"#Diva","count":19},{"tag":"#Deals","count":15}]

@app.get("/api/products")
def prods_api():
    cur=conn.cursor(); cur.execute("SELECT id,name,price,code,image,category,stock FROM products")
    out=[]
    for r in cur.fetchall():
        cur2=conn.cursor(); cur2.execute("SELECT AVG(rating), COUNT(*) FROM reviews WHERE product_id=?",(r[0],)); avg=cur2.fetchone()
        out.append({"id":r[0],"name":r[1],"price":r[2],"code":r[3],"image":r[4],"category":r[5],"stock":r[6],"rating":round(avg[0],1) if avg[0] else 4.5,"reviews":avg[1]})
    return out

@app.get("/api/verify/{code}")
def verify(code:str):
    code=clean_input(code,20).upper(); cur=conn.cursor(); cur.execute("SELECT name FROM products WHERE code=?",(code,)); row=cur.fetchone()
    return {"valid":True,"product":{"name":row[0]}} if row else {"valid":False}

@app.get("/api/orders")
def orders_api(phone:str=""):
    phone=clean_input(phone,15); cur=conn.cursor()
    if phone: cur.execute("SELECT order_no,name,total,status,created FROM orders WHERE phone=? ORDER BY id DESC",(phone,))
    else: cur.execute("SELECT order_no,name,total,status,created FROM orders ORDER BY id DESC LIMIT 50")
    return [{"order_no":r[0],"name":r[1],"total":r[2],"status":r[3],"created":r[4]} for r in cur.fetchall()]

@app.get("/api/track/{order_no}")
def track(order_no:str):
    cur=conn.cursor(); cur.execute("SELECT order_no,total,status,created FROM orders WHERE order_no=?",(clean_input(order_no,20),)); r=cur.fetchone()
    if not r: return {"found":False}
    steps=["Pending","PAID","Shipped","Delivered"]; idx=steps.index(r[2]) if r[2] in steps else 0
    return {"found":True,"order_no":r[0],"total":r[1],"status":r[2],"created":r[3],"progress":(idx+1)*25}

@app.post("/api/promo/check")
async def promo_check(req:Request):
    d=await req.json(); cur=conn.cursor(); cur.execute("SELECT discount FROM promos WHERE code=?",(clean_input(d.get("code",""),20).upper(),)); r=cur.fetchone()
    return {"valid":True,"discount":r[0]} if r else {"valid":False}

@app.get("/api/reviews/{pid}")
def get_reviews(pid:int):
    cur=conn.cursor(); cur.execute("SELECT name,rating,text,created FROM reviews WHERE product_id=? ORDER BY id DESC LIMIT 10",(pid,)); return [{"name":r[0],"rating":r[1],"text":r[2],"created":r[3]} for r in cur.fetchall()]

@app.post("/api/reviews/add")
async def add_review(req:Request):
    d=await req.json()
    try: pid=int(d.get("product_id",0)); rating=int(d.get("rating",5))
    except: return {"status":"error"}
    conn.execute("INSERT INTO reviews (product_id,name,rating,text,created) VALUES (?,?,?,?,?)",(pid,clean_input(d.get("name","Customer"),30),rating,clean_input(d.get("text",""),200),datetime.datetime.now().strftime("%Y-%m-%d"))); conn.commit()
    return {"status":"ok"}

@app.post("/api/admin/check")
async def admin_check(req:Request):
    ip=req.client.host if req.client else "unknown"
    if is_blocked(ip): return {"status":"blocked","message":"Too many tries. Wait 15 mins"}
    d=await req.json()
    if d.get("password","")==ADMIN_PASSWORD:
        FAILED[ip]=[]; return {"status":"ok"}
    record_fail(ip); return {"status":"error","message":"Wrong password"}

@app.get("/api/admin/dashboard")
def admin_dash(password:str=""):
    if password!=ADMIN_PASSWORD: return {"error":"unauthorized"}
    cur=conn.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM orders"); o=cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM users"); u=cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM products"); p=cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM community_posts"); cp=cur.fetchone()
    cur.execute("SELECT order_no,name,phone,total,status,created FROM orders ORDER BY id DESC LIMIT 30"); orders=[{"order_no":r[0],"name":r[1],"phone":r[2],"total":r[3],"status":r[4],"created":r[5]} for r in cur.fetchall()]
    cur.execute("SELECT phone,name FROM users ORDER BY id DESC LIMIT 30"); customers=[{"phone":r[0],"name":r[1]} for r in cur.fetchall()]
    for c in customers:
        cur.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM orders WHERE phone=?",(c["phone"],)); r=cur.fetchone(); c["orders"]=r[0]; c["spent"]=r[1]
    cur.execute("SELECT id,name,price,stock,category FROM products ORDER BY stock ASC"); prods=[{"id":r[0],"name":r[1],"price":r[2],"stock":r[3],"category":r[4]} for r in cur.fetchall()]
    return {"total_orders":o[0],"total_sales":o[1],"total_customers":u[0],"total_products":p[0],"total_posts":cp[0],"orders":orders,"customers":customers,"products":prods}

@app.post("/api/admin/update_status")
async def upd_status(req:Request):
    d=await req.json()
    if d.get("password")!=ADMIN_PASSWORD: return {"status":"error"}
    conn.execute("UPDATE orders SET status=? WHERE order_no=?",(clean_input(d.get("status",""),20),clean_input(d.get("order_no",""),20))); conn.commit()
    return {"status":"ok"}

@app.post("/api/admin/add_product")
async def add_prod(req:Request):
    d=await req.json()
    if d.get("password")!=ADMIN_PASSWORD: return {"status":"error"}
    cur=conn.cursor(); cur.execute("SELECT MAX(id) FROM products"); nid=(cur.fetchone()[0] or 0)+1
    conn.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?)",(nid,clean_input(d.get("name",""),80),int(d.get("price",0)),clean_input(d.get("code",""),20),d.get("image","LONMA|#0A9EBB"),clean_input(d.get("category",""),20),int(d.get("stock",0)))); conn.commit()
    return {"status":"ok"}

@app.post("/api/admin/delete_product")
async def del_prod(req:Request):
    d=await req.json()
    if d.get("password")!=ADMIN_PASSWORD: return {"status":"error"}
    conn.execute("DELETE FROM products WHERE id=?",(int(d.get("id",0)),)); conn.commit()
    return {"status":"ok"}

@app.get("/api/customer/dashboard")
def cust_dash(phone:str=""):
    phone=clean_input(phone,15); cur=conn.cursor()
    cur.execute("SELECT name FROM users WHERE phone=?",(phone,)); u=cur.fetchone()
    cur.execute("SELECT order_no,total,status,created FROM orders WHERE phone=? ORDER BY id DESC",(phone,)); orders=[{"order_no":r[0],"total":r[1],"status":r[2],"created":r[3]} for r in cur.fetchall()]
    total=sum(o["total"] for o in orders)
    return {"name":u[0] if u else "Customer","phone":phone,"orders":orders,"total_orders":len(orders),"total_spent":total,"points":total//100}

@app.post("/mpesa/stkpush")
async def stk(req:Request):
    d=await req.json(); raw=clean_input(d.get('phone',''),15); phone=raw.replace(" ","").replace("+254","0")
    if phone.startswith("0"): phone="254"+phone[1:]
    phone="".join([c for c in phone if c.isdigit()])
    try: amount=int(d.get('amount',1))
    except: amount=1
    if amount<1 or amount>500000: return {"status":"error","message":"Invalid amount"}
    if len(phone)!=12: return {"status":"error","message":"Invalid phone"}
    order_no='LONMA'+datetime.datetime.now().strftime("%H%M%S")
    name=clean_input(d.get('name','Guest'),50); area=clean_input(d.get('area',''),20); loc=clean_input(d.get('location',''),100)
    conn.execute("INSERT INTO orders (order_no,name,phone,area,location,items,total,status,created,mpesa_receipt,checkout_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(order_no,name,raw,area,loc,json.dumps(d.get('cart',[]))[:2000],amount,'Pending',datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"",order_no)); conn.commit()
    if DARAJA_KEY and DARAJA_PASSKEY:
        token=get_token()
        if token:
            ts=datetime.datetime.now().strftime("%Y%m%d%H%M%S"); pwd=base64.b64encode(f"{DARAJA_SHORTCODE}{DARAJA_PASSKEY}{ts}".encode()).decode()
            payload={"BusinessShortCode":DARAJA_SHORTCODE,"Password":pwd,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":amount,"PartyA":phone,"PartyB":DARAJA_SHORTCODE,"PhoneNumber":phone,"CallBackURL":DARAJA_CALLBACK,"AccountReference":order_no,"TransactionDesc":order_no}
            try:
                base="https://api.safaricom.co.ke" if USE_PROD else "https://sandbox.safaricom.co.ke"
                r=requests.post(f"{base}/mpesa/stkpush/v1/processrequest",json=payload,headers={"Authorization":f"Bearer {token}"},timeout=15); res=r.json()
                if res.get("ResponseCode")=="0":
                    conn.execute("UPDATE orders SET checkout_id=? WHERE order_no=?",(res.get("CheckoutRequestID",order_no),order_no)); conn.commit()
                    return {"status":"ok","message":f"STK sent to {raw}","order_no":order_no}
            except: pass
    return {"status":"ok","message":f"Order {order_no} saved","order_no":order_no}

@app.post("/api/auth/register")
async def reg(req:Request):
    d=await req.json(); phone=clean_input(d.get("phone",""),15); name=clean_input(d.get("name",""),50); pwd=d.get("password","").strip()[:50]
    if len(phone)<10 or len(pwd)<4: return {"status":"error","message":"Invalid input"}
    cur=conn.cursor(); cur.execute("SELECT id FROM users WHERE phone=?",(phone,))
    if cur.fetchone(): return {"status":"error","message":"Exists"}
    cur.execute("INSERT INTO users (phone,name,password) VALUES (?,?,?)",(phone,name,pwd)); conn.commit()
    return {"status":"ok","user":{"phone":phone,"name":name}}

@app.post("/api/auth/login")
async def log(req:Request):
    ip=req.client.host if req.client else "unknown"
    if is_blocked(ip): return {"status":"error","message":"Too many tries. Wait 15 mins"}
    d=await req.json(); cur=conn.cursor(); cur.execute("SELECT phone,name FROM users WHERE phone=? AND password=?",(clean_input(d.get("phone",""),15),d.get("password","").strip()[:50])); row=cur.fetchone()
    if not row: record_fail(ip); return {"status":"error","message":"Wrong"}
    FAILED[ip]=[]; return {"status":"ok","user":{"phone":row[0],"name":row[1]}}

HTML="""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>LONMA ORBIT - Online Supermarket</title><style>
:root{--teal:#0A9EBB;--dark:#0F172A;--line:#E2E8F0;--muted:#64748B;--bg:#F8FAFC}*{box-sizing:border-box}body{margin:0;font-family:Inter,-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--dark);-webkit-font-smoothing:antialiased}
.nav{position:fixed;top:0;width:100%;background:#fff;z-index:1000;border-bottom:1px solid var(--line)}.nav-top{padding:10px 16px;display:flex;justify-content:space-between;align-items:center;height:60px}
.logo{display:flex;align-items:center;gap:10px;cursor:pointer;min-width:0}.logo-img-wrap{width:44px;height:44px;border-radius:50%;background:#fff;border:1px solid var(--line);display:flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0}.logo-img-wrap img{width:40px;height:40px;object-fit:contain}
.logo img.slide{transform:translateX(14px) rotate(360deg) scale(1.12)}
.logo b{font-size:15px;letter-spacing:.4px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.logo b small{display:block;font-size:9px;letter-spacing:2.2px;color:var(--muted);font-weight:700}
.header-actions{display:flex;gap:8px;flex-shrink:0}.pill{padding:9px 14px;border-radius:30px;font-weight:700;font-size:12px;cursor:pointer;border:1px solid var(--line);background:#fff}.pill-dark{background:var(--dark);color:#fff;border-color:var(--dark);position:relative}.cart-num{position:absolute;top:-6px;right:-6px;background:var(--teal);color:#fff;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700}
.search-wrap{padding:0 16px 10px}.search-box{background:#F1F5F9;border-radius:12px;height:46px;display:flex;align-items:center;gap:12px;padding:0 12px;border:1px solid var(--line)}
.search-box input{border:none;outline:none;background:transparent;flex:1;font-size:14px;min-width:0}.burger{font-size:12px;cursor:pointer;font-weight:800;letter-spacing:1px;color:var(--dark);white-space:nowrap}
.cat-chips{display:flex;gap:8px;overflow-x:auto;padding:0 16px 10px;scrollbar-width:none}.chip{white-space:nowrap;padding:8px 16px;border-radius:20px;background:#fff;border:1px solid var(--line);font-size:12px;font-weight:700;cursor:pointer}.chip.active{background:var(--dark);color:#fff}
.page{display:none;padding:168px 14px 92px;max-width:480px;margin:0 auto}.page.active{display:block}
.banner{background:linear-gradient(135deg,#0A9EBB 0%,#0F172A 100%);color:#fff;border-radius:16px;padding:16px;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;gap:10px}
.card{background:#fff;border-radius:16px;padding:14px;margin:10px 0;border:1px solid #F1F5F9;box-shadow:0 2px 10px rgba(15,23,42,.04);display:flex;gap:12px}
.pimg{width:84px;height:84px;border-radius:12px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;letter-spacing:.5px;color:#fff;text-align:center;line-height:1.2;padding:6px}
.btn{background:var(--dark);color:#fff;border:none;padding:13px;border-radius:12px;width:100%;font-weight:700;cursor:pointer;font-size:14px}.btn-teal{background:var(--teal)}
input,select,textarea{width:100%;padding:12px;border-radius:12px;border:1px solid var(--line);margin:6px 0;font-size:14px;background:#fff;outline:none}
.bottom{position:fixed;bottom:0;width:100%;background:#fff;border-top:1px solid var(--line);display:flex;justify-content:space-around;padding:10px 0 calc(10px + env(safe-area-inset-bottom));z-index:1000}
.bottom div{font-size:11px;text-align:center;flex:1;cursor:pointer;color:#94A3B8;font-weight:700;letter-spacing:.3px;line-height:1.2}.bottom div.active{color:var(--dark)}.bottom .bicon{font-size:10px;font-weight:800;letter-spacing:1.2px;color:#94A3B8;margin-bottom:2px}.bottom div.active .bicon{color:var(--teal)}
.side{position:fixed;top:0;left:-320px;width:300px;height:100%;background:#fff;z-index:2000;transition:.35s;box-shadow:20px 0 60px rgba(0,0,0,.12);overflow-y:auto}.side.open{left:0}.overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(15,23,42,.4);z-index:1999}.overlay.open{display:block}
.top-box{background:var(--dark);padding:24px 20px;color:#fff;text-align:center}.lc{width:72px;height:72px;background:#fff;border-radius:50%;margin:0 auto;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:pointer;border:1px solid #E2E8F0}.lc img{width:66px;height:66px;object-fit:contain;transition:transform .6s cubic-bezier(.34,1.56,.64,1)}.lc img.slide{transform:translateX(10px) rotate(360deg) scale(1.08)}
.menu{padding:12px 0}.mi{display:flex;align-items:center;gap:14px;padding:14px 20px;cursor:pointer}.mi:hover{background:#F8FAFC}.mi b{font-size:14px;font-weight:600;flex:1}.ico{width:38px;height:38px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;letter-spacing:.5px;background:#F1F5F9;color:var(--dark);flex-shrink:0}.tag{font-size:11px;font-weight:800;padding:5px 10px;border-radius:20px}.div{height:1px;background:#F1F5F9;margin:8px 20px}.label{font-size:10px;font-weight:800;letter-spacing:.18em;color:#94A3B8;padding:14px 20px 6px}
.stat{display:grid;grid-template-columns:1fr 1fr;gap:10px}.statbox{background:#fff;border-radius:14px;padding:14px;border:1px solid #F1F5F9}.statbox b{font-size:20px}.statbox span{font-size:11px;color:var(--muted)}
.dashtab{display:flex;gap:8px;overflow-x:auto;padding:8px 0}.dtab{white-space:nowrap;padding:8px 16px;border-radius:20px;background:#fff;border:1px solid var(--line);font-size:12px;font-weight:700;cursor:pointer}.dtab.active{background:var(--dark);color:#fff}
.wa{position:fixed;bottom:84px;right:12px;background:#0A9EBB;color:#fff;height:40px;padding:0 14px;border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;z-index:900;box-shadow:0 6px 16px rgba(10,158,187,.35);cursor:pointer;letter-spacing:.6px}
.progress{height:8px;background:#E2E8F0;border-radius:10px;overflow:hidden}.progress div{height:100%;background:var(--teal)}
.avatar{width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#0A9EBB,#0F172A);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;flex-shrink:0;font-size:15px}
.post-actions{display:flex;gap:14px;margin-top:12px;color:#64748B;font-size:12px;font-weight:600;flex-wrap:wrap}.post-actions span{cursor:pointer;white-space:nowrap}.post-actions small{display:block;color:#94A3B8;font-weight:600;font-size:11px}
.hashtag{color:#0A9EBB;font-weight:700}
.star{color:#F59E0B;letter-spacing:1px}
.brand-tag{display:inline-flex;align-items:center;background:#F0F9FB;color:#0A9EBB;border:1px solid #CFF0F5;padding:5px 10px;border-radius:20px;font-size:11px;font-weight:800;letter-spacing:.5px;margin-top:10px}
.trend-row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid #F1F5F9}.trend-row:last-child{border-bottom:none}
</style></head><body>
<div class="nav"><div class="nav-top"><div class="logo" onclick="logoSlide(this);show('products')"><div class="logo-img-wrap"><img src="/logo.png" alt="LONMA"></div><b>LONMA ORBIT<small>ONLINE SUPERMARKET</small></b></div><div class="header-actions"><div class="pill" onclick="show('wishlist')">Saved <span id="wishCount">0</span></div><div class="pill pill-dark" onclick="show('cart')">CART <span id="cartCount" class="cart-num" style="display:none">0</span></div></div></div><div class="search-wrap"><div class="search-box"><span class="burger" onclick="openMenu()">MENU</span><input id="searchInput" placeholder="Search Diva, Detrex, Sawa..." oninput="filterProducts()"></div></div><div class="cat-chips"><div class="chip active" onclick="filterCat('All',this)">All</div><div class="chip" onclick="filterCat('Soaps',this)">Soaps</div><div class="chip" onclick="filterCat('Lotions',this)">Lotions</div><div class="chip" onclick="filterCat('Pomades',this)">Pomades</div><div class="chip" onclick="filterCat('Cooking Oils',this)">Oils</div></div></div>
<div class="wa" onclick="openWA()">CHAT WITH US</div>
<div class="overlay" id="overlay" onclick="closeMenu()"></div>
<div class="side" id="side"><div class="top-box"><div style="text-align:right"><span style="background:rgba(255,255,255,.15);padding:7px 14px;border-radius:20px;font-size:11px;font-weight:700;cursor:pointer" onclick="show('cart');closeMenu()">VIEW CART</span></div><div class="lc" onclick="logoSlide(this);show('products');closeMenu()"><img src="/logo.png" alt="LONMA"></div><div style="font-weight:800;font-size:19px;margin-top:12px;letter-spacing:.5px">LONMA ORBIT</div><div style="opacity:.85;font-size:12px;margin-top:4px">100% Genuine &middot; Fast Delivery &middot; Secured</div><div style="margin-top:12px;background:#0A9EBB;padding:10px;border-radius:10px;font-size:12px;font-weight:700;line-height:1.5">Promo: LONMA10 = 10% OFF &middot; WELCOME20 = 20% OFF</div></div><div class="menu"><div class="label">SHOP</div><div class="mi" onclick="show('products');closeMenu()"><div class="ico">HOME</div><b>Home &middot; Products</b><span class="tag" style="background:var(--teal);color:#fff">NEW</span></div><div class="mi" onclick="show('wishlist');closeMenu()"><div class="ico">SAVED</div><b>Wishlist</b><span class="tag" style="background:#F1F5F9" id="mcWish">0</span></div><div class="mi" onclick="show('cart');closeMenu()"><div class="ico">CART</div><b>Cart</b><span class="tag" style="background:#F1F5F9" id="mc">0</span></div><div class="mi" onclick="show('track');closeMenu()"><div class="ico">TRACK</div><b>Track Order</b></div><div class="div"></div><div class="label">COMMUNITY</div><div class="mi" onclick="show('community');closeMenu()"><div class="ico" style="background:#0A9EBB;color:#fff">COM</div><b>Community</b><span class="tag" style="background:#0A9EBB;color:#fff">NEW</span></div><div class="div"></div><div class="label">MY DASHBOARD</div><div class="mi" onclick="show('account');closeMenu()"><div class="ico">ACCT</div><b>My Dashboard</b><span class="tag" style="background:#DCFCE7;color:#166534">CUSTOMER</span></div><div class="div"></div><div class="label">SUPPORT</div><div class="mi" onclick="show('scan');closeMenu()"><div class="ico">VERIFY</div><b>Verify Product</b></div><div class="mi" onclick="openWA()"><div class="ico">CHAT</div><b>WhatsApp Us</b></div><div class="mi" onclick="show('terms');closeMenu()"><div class="ico">TERMS</div><b>Terms</b></div><div class="div"></div><div class="mi" onclick="show('admin');closeMenu()"><div class="ico" style="background:#0F172A;color:#fff">ADMIN</div><b>Admin Dashboard</b><span class="tag" style="background:#0F172A;color:#fff">ADMIN</span></div><div style="text-align:center;padding:18px;color:#94A3B8;font-size:11px">v11.0 Professional &middot; Kenya</div></div></div>

<div id="products" class="page active"><div class="banner"><div><div style="font-weight:800;font-size:15px">FREE Delivery</div><div style="font-size:12px;opacity:.9">Orders over KSh 2000 &middot; Use LONMA10</div></div><div style="background:#fff;color:var(--dark);padding:8px 14px;border-radius:20px;font-weight:800;font-size:12px;cursor:pointer;white-space:nowrap" onclick="show('community')">JOIN COMMUNITY</div></div><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;gap:8px"><h3 style="margin:0;font-size:17px">Products</h3><select id="sortSelect" onchange="filterProducts()" style="width:auto;padding:8px 12px;font-size:12px;font-weight:700;margin:0"><option value="featured">Sort: Featured</option><option value="low">Price: Low to High</option><option value="high">Price: High to Low</option><option value="name">Name: A to Z</option><option value="rating">Top Rated</option></select></div><div style="text-align:right;font-size:12px;color:#64748B;margin-bottom:4px" id="pCount">9 items</div><div id="plist"></div></div>

<div id="community" class="page"><div style="display:flex;justify-content:space-between;align-items:center"><h3 style="margin:0;font-size:17px">Community</h3><span style="font-size:11px;background:#0A9EBB;color:#fff;padding:6px 12px;border-radius:20px;font-weight:700">LONMA COMMUNITY</span></div><div class="card" style="display:block;margin-top:12px"><div style="display:flex;gap:10px"><div class="avatar" id="myAvatar">?</div><textarea id="postText" placeholder="Share deals, recipes, reviews... Use #Detrex #Diva" style="flex:1;border:none;outline:none;resize:none" rows="3"></textarea></div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;gap:10px"><span style="font-size:12px;color:#64748B">Post a review and earn points</span><button class="btn" style="width:auto;padding:10px 22px;border-radius:20px;background:#0A9EBB" onclick="createPost()">Post</button></div></div><div class="card" style="display:block"><h4 style="margin:0 0 4px;font-size:15px">Trending in LONMA</h4><div id="trendingList"></div></div><div id="feed"></div></div>

<div id="wishlist" class="page"><h3>My Wishlist</h3><div id="wishList"></div></div>
<div id="track" class="page"><h3>Track Order</h3><div class="card" style="display:block"><input id="trackNo" placeholder="Enter order number e.g. LONMA123456"><button class="btn btn-teal" onclick="trackOrder()">Track Order</button><div id="trackRes" style="margin-top:14px"></div></div></div>
<div id="productDetail" class="page"><div id="detailContent"></div></div>

<div id="cart" class="page"><h3>Cart</h3><div id="cartItems"></div><div id="cartSum" style="display:none"><div class="card" style="display:block"><div style="display:flex;gap:8px"><input id="promoCode" placeholder="Promo code e.g. LONMA10" style="flex:1"><button class="btn" style="width:auto;padding:12px 18px" onclick="applyPromo()">Apply</button></div><p id="promoMsg" style="font-size:12px;font-weight:700"></p><div style="display:flex;justify-content:space-between"><span>Subtotal (<span id="tItems">0</span>)</span><b>KSh <span id="sub">0</span></b></div><div style="display:flex;justify-content:space-between;margin-top:8px"><span>Discount</span><b id="discFee" style="color:#16A34A">KSh 0</b></div><div style="display:flex;justify-content:space-between;margin-top:8px"><span>Delivery</span><b id="delFee"></b></div><div style="display:flex;justify-content:space-between;margin-top:12px;font-size:18px;border-top:1px solid #F1F5F9;padding-top:12px"><span>Total</span><b>KSh <span id="tot">0</span></b></div><div style="margin-top:16px"><input id="custName" placeholder="Full Name"><input id="phone" placeholder="M-Pesa 07..."><select id="area"><option value="">Select Area</option><option value="CBD">CBD - 150</option><option value="Westlands">Westlands - 200</option><option value="Upcountry">Upcountry - 350</option></select><textarea id="loc" placeholder="Exact location / building"></textarea><label style="font-size:12px;display:flex;gap:8px;align-items:center;margin:12px 0"><input type="checkbox" id="agree" style="width:auto"> I agree to <a href="#" onclick="show('terms');return false" style="color:#0A9EBB;font-weight:800">Terms</a></label></div><button class="btn" onclick="checkout()">Pay KSh <span id="pay">0</span> with M-Pesa</button><button class="btn" style="background:#0A9EBB;margin-top:8px" onclick="orderViaWA()">Order via WhatsApp</button><p id="ps" style="text-align:center;font-size:13px"></p></div></div><div id="emptyCart" class="card" style="text-align:center;padding:30px;display:block"><h4>Your cart is empty</h4><p style="font-size:13px;color:#64748B">Browse products and add items to your cart.</p><button class="btn btn-teal" onclick="show('products')">Start Shopping</button></div></div>

<div id="orders" class="page"><h3>Orders</h3><div style="display:flex;gap:8px;margin-bottom:12px"><input id="phLookup" placeholder="Enter phone 07..."><button class="btn" style="width:auto;padding:10px 20px" onclick="loadOrders()">Load</button></div><div id="olist"></div><div id="noOrd" class="card" style="text-align:center;display:block"><p>No orders yet</p></div></div>
<div id="scan" class="page"><h3>Verify Authenticity</h3><div class="card" style="display:block;padding:20px;text-align:center"><h4>Check Product</h4><p style="font-size:12px;color:#64748B">Enter code like DIV-001</p><input id="vcode" placeholder="DIV-001"><button class="btn btn-teal" onclick="verify()" style="margin-top:10px">Verify Now</button><p id="vres" style="font-weight:700;margin-top:12px"></p></div></div>
<div id="account" class="page"><div id="out"><div class="card" style="display:block"><h4>Create Account</h4><input id="rn" placeholder="Full name"><input id="rp" placeholder="07xxxxxxxx"><input id="rpass" type="password" placeholder="Password"><button class="btn" onclick="register()">Create Account</button><p id="rs"></p></div><div class="card" style="display:block"><h4>Sign In</h4><input id="lp" placeholder="07xxxxxxxx"><input id="lpass" type="password" placeholder="Password"><button class="btn" style="background:var(--teal)" onclick="login()">Sign In</button><p id="ls"></p></div></div><div id="in" style="display:none"><div class="card" style="display:block;background:var(--dark);color:#fff;text-align:center;padding:24px"><h3 id="an" style="margin:12px 0 4px">Welcome</h3><p id="ap" style="opacity:.7;font-size:13px"></p><button class="btn" style="background:#fff;color:var(--dark);margin-top:16px" onclick="logout()">Sign Out</button></div><div class="stat" style="margin-top:12px"><div class="statbox"><b id="cOrders">0</b><br><span>My Orders</span></div><div class="statbox"><b id="cSpent">KSh 0</b><br><span>Total Spent</span></div><div class="statbox"><b id="cPoints">0</b><br><span>Points</span></div><div class="statbox"><b id="cPhone">-</b><br><span>Phone</span></div></div><h4 style="margin:18px 0 6px">My Orders History</h4><div id="cList"></div></div></div>
<div id="terms" class="page"><h3>Terms and Conditions</h3><div class="card" style="display:block;line-height:1.7;font-size:13px;padding:18px"><h4>1. Delivery</h4><p>CBD KSh 150, Westlands KSh 200, Upcountry KSh 350. FREE for orders KSh 2000+. Promo LONMA10 = 10% OFF.</p><h4>2. Payments</h4><p>All payments via M-Pesa STK Push. Order confirmed after receipt.</p><h4>3. Community Rules</h4><p>Be respectful. No spam, no insults, no fake reviews. Admin can remove posts.</p><p style="margin-top:16px;font-size:11px;color:#94A3B8">v11.0 &middot; Made in Kenya</p><button class="btn" style="margin-top:14px" onclick="show('cart')">Back to Cart</button></div></div>
<div id="admin" class="page"><h3>Admin Dashboard</h3><div id="adminLoginBox" class="card" style="display:block"><input id="apass" type="password" placeholder="Admin Password"><button class="btn" onclick="adminLogin()">Secure Login</button><p id="ast"></p></div><div id="acont" style="display:none"><div class="stat"><div class="statbox" style="background:#0F172A;color:#fff"><b id="aSales">KSh 0</b><br><span style="color:#CBD5E1">Total Sales</span></div><div class="statbox"><b id="aOrders">0</b><br><span>Total Orders</span></div><div class="statbox"><b id="aCust">0</b><br><span>Customers</span></div><div class="statbox"><b id="aProd">0</b><br><span>Products</span></div></div><div class="stat" style="margin-top:10px"><div class="statbox" style="background:#0A9EBB;color:#fff"><b id="aPosts">0</b><br><span>Community Posts</span></div><div class="statbox"><b>Live</b><br><span>Community Active</span></div></div><div class="dashtab"><div class="dtab active" onclick="switchAdminTab('orders',this)">Orders</div><div class="dtab" onclick="switchAdminTab('customers',this)">Customers</div><div class="dtab" onclick="switchAdminTab('stock',this)">Stock</div><div class="dtab" onclick="switchAdminTab('add',this)">Add Product</div></div><div id="aOrdersList"></div><div id="aCustList" style="display:none"></div><div id="aStockList" style="display:none"></div><div id="aAdd" style="display:none"><div class="card" style="display:block"><input id="npName" placeholder="Product Name"><input id="npPrice" type="number" placeholder="Price"><input id="npCode" placeholder="Code e.g. DIV-010"><select id="npCat"><option>Soaps</option><option>Lotions</option><option>Pomades</option><option>Cooking Oils</option></select><input id="npStock" type="number" placeholder="Stock"><button class="btn btn-teal" onclick="addProduct()">Add Product</button><p id="npMsg"></p></div></div></div></div>
<div id="receipt" class="page"><div class="card" style="display:block;text-align:center;padding:24px" id="rcont"></div><button class="btn" onclick="show('products')">Continue Shopping</button></div>
<div class="bottom"><div id="b-products" class="active" onclick="show('products')"><div class="bicon">HOME</div>Home</div><div id="b-community" onclick="show('community')"><div class="bicon">COMMUNITY</div>Community</div><div id="b-cart" onclick="show('cart')"><div class="bicon">CART</div>Cart</div><div id="b-orders" onclick="show('orders')"><div class="bicon">ORDERS</div>Orders</div><div id="b-account" onclick="show('account')"><div class="bicon">ACCOUNT</div>Dashboard</div></div>
<script>
let all=[],cart=[],wishlist=JSON.parse(localStorage.getItem('lonma_wish')||'[]'),myOrders=JSON.parse(localStorage.getItem('my_orders')||'[]'),activeCat='All',adminPass='',adminData=null,promoDiscount=0,promoCode='',feedCache=[];
try{let s=localStorage.getItem('lonma_cart');if(s)cart=JSON.parse(s);}catch(e){cart=[];}
function save(){localStorage.setItem('lonma_cart',JSON.stringify(cart));updateCount();}
function saveWish(){localStorage.setItem('lonma_wish',JSON.stringify(wishlist));updateCount();}
function updateCount(){let c=0;for(let i of cart)c+=i.qty;let el=document.getElementById('cartCount');if(el){el.innerText=c;el.style.display=c>0?'flex':'none';}document.getElementById('mc').innerText=c;document.getElementById('wishCount').innerText=wishlist.length;document.getElementById('mcWish').innerText=wishlist.length;}
function logoSlide(el){
  let img = el.querySelector('img');
  if(!img) return;
  img.classList.remove('slide');
  void img.offsetWidth;
  img.classList.add('slide');
  setTimeout(()=>img.classList.remove('slide'),650);
  let other = document.querySelectorAll('.logo img, .lc img');
  other.forEach(o=>{ if(o!==img){ o.classList.remove('slide'); void o.offsetWidth; o.classList.add('slide'); setTimeout(()=>o.classList.remove('slide'),650); }});
}
function openMenu(){document.getElementById('side').classList.add('open');document.getElementById('overlay').classList.add('open');}
function closeMenu(){document.getElementById('side').classList.remove('open');document.getElementById('overlay').classList.remove('open');}
function openWA(){let msg=encodeURIComponent('Hi LONMA ORBIT. I want to order.');window.open('https://wa.me/254700000000?text='+msg,'_blank');}
function orderViaWA(){let txt='Hi LONMA. I want to order:\\n';for(let i of cart)txt+=i.name+' x'+i.qty+' = KSh '+(i.price*i.qty)+'\\n';txt+='Total: KSh '+document.getElementById('tot').innerText;window.open('https://wa.me/254700000000?text='+encodeURIComponent(txt),'_blank');}
function getUser(){try{return JSON.parse(localStorage.getItem('lonma_user')||'null');}catch(e){return null;}}
function formatText(t){return t.replace(/#(\\w+)/g,'<span class="hashtag">#$1</span>');}
function avatarLetter(name){return (name||'L').charAt(0).toUpperCase();}
async function loadCommunity(){
  let u=getUser(); let phone=u?u.phone:'';
  let r=await fetch('/api/community/posts?phone='+encodeURIComponent(phone)); feedCache=await r.json();
  let tr=await fetch('/api/community/trending'); let trends=await tr.json();
  document.getElementById('trendingList').innerHTML=trends.map(t=>`<div class="trend-row"><b style="font-size:14px">${t.tag}</b><span style="color:#64748B;font-size:12px">${t.count} posts</span></div>`).join('');
  document.getElementById('myAvatar').innerText=u?avatarLetter(u.name):'?';
  renderFeed();
}
function renderFeed(){
  document.getElementById('feed').innerHTML=feedCache.map(p=>{
    let imgHtml='';
    if(p.image){let parts=p.image.split('|'); imgHtml=`<span class="brand-tag">${parts[0]}</span>`;}
    return `<div class="card" style="display:block;padding:16px"><div style="display:flex;gap:10px"><div class="avatar">${avatarLetter(p.author)}</div><div style="flex:1;min-width:0"><div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap"><b style="font-size:14px">${p.author}</b><span style="font-size:11px;color:#94A3B8">${p.created}</span></div><div style="font-size:14px;line-height:1.55;margin-top:5px;word-break:break-word">${formatText(p.text)}</div>${imgHtml}<div class="post-actions"><span onclick="likePost(${p.id})">${p.liked?'Liked':'Like'}<small>${p.likes} likes</small></span><span onclick="toggleComments(${p.id})">Comments<small>${p.comments}</small></span><span onclick="repostPost(${p.id})">Repost<small>${p.reposts}</small></span><span onclick="sharePost(${p.id})">Share<small>Send</small></span><span onclick="shopFromPost()">Shop<small>Products</small></span></div><div id="comments-${p.id}" style="display:none;margin-top:10px"></div><div id="commentBox-${p.id}" style="display:none;margin-top:10px"><input id="cInput-${p.id}" placeholder="Write a comment..."><button class="btn btn-teal" style="padding:10px" onclick="sendComment(${p.id})">Reply</button></div></div></div></div>`;
  }).join('')||'No posts yet. Be the first to post.';
}
async function createPost(){
  let u=getUser(); if(!u){alert('Please Sign In first to post.'); show('account'); return;}
  let txt=document.getElementById('postText').value.trim(); if(!txt)return;
  await fetch('/api/community/post',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author:u.name,phone:u.phone,text:txt})});
  document.getElementById('postText').value=''; loadCommunity();
}
async function likePost(id){
  let u=getUser(); let phone=u?u.phone:'guest-'+Math.random();
  await fetch('/api/community/like',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({post_id:id,phone})}); loadCommunity();
}
async function repostPost(id){ await fetch('/api/community/repost',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({post_id:id})}); loadCommunity();}
async function toggleComments(id){
  let box=document.getElementById('commentBox-'+id); let list=document.getElementById('comments-'+id);
  let showBox=box.style.display==='none'; box.style.display=showBox?'block':'none'; list.style.display=showBox?'block':'none';
  if(showBox){ let r=await fetch('/api/community/comments/'+id); let cs=await r.json(); list.innerHTML=cs.map(c=>`<div style="background:#F8FAFC;padding:8px 10px;border-radius:10px;margin:4px 0"><b style="font-size:12px">${c.author}</b> <span style="font-size:12px">${c.text}</span></div>`).join('')||'<div style="font-size:12px;color:#94A3B8">No comments yet</div>';}
}
async function sendComment(id){
  let u=getUser(); if(!u){alert('Sign in to comment'); show('account'); return;}
  let txt=document.getElementById('cInput-'+id).value.trim(); if(!txt)return;
  await fetch('/api/community/comment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({post_id:id,author:u.name,text:txt})}); toggleComments(id); toggleComments(id); loadCommunity();
}
function sharePost(id){let p=feedCache.find(x=>x.id===id); if(!p)return; let url='https://app.lonmaorbit.co.ke'; if(navigator.share){navigator.share({title:'LONMA Community',text:p.text,url});} else {navigator.clipboard.writeText(p.text+' - '+url); alert('Copied.');}}
function shopFromPost(){show('products'); filterProducts();}
function filterCat(cat,el){activeCat=cat;document.querySelectorAll('.chip').forEach(c=>c.classList.remove('active'));el.classList.add('active');filterProducts();}
function filterProducts(){let q=document.getElementById('searchInput').value.toLowerCase();let sort=document.getElementById('sortSelect').value;let f=all.filter(p=>{let matchCat=activeCat==='All'||p.category===activeCat;let matchSearch=!q||p.name.toLowerCase().includes(q);return matchCat&&matchSearch;});if(sort==='low')f.sort((a,b)=>a.price-b.price);if(sort==='high')f.sort((a,b)=>b.price-a.price);if(sort==='name')f.sort((a,b)=>a.name.localeCompare(b.name));if(sort==='rating')f.sort((a,b)=>b.rating-a.rating);render(f);}
function parseImg(s){let parts=(s||'LONMA|#0A9EBB').split('|');return {label:parts[0],bg:parts[1]||'#0A9EBB'};}
function stars(r){let full=Math.round(r); return '<span class="star">'+'★'.repeat(full)+'</span> <span style="color:#64748B">'+r+'</span>';}
function render(list){let h='';for(let p of list){let inC=cart.find(c=>c.id===p.id);let isWish=wishlist.includes(p.id);let low=p.stock<=8?`<span style="color:#EF4444;font-size:10px;font-weight:800;background:#FEF2F2;padding:3px 8px;border-radius:20px;margin-left:6px">Only ${p.stock} left</span>`:'';let im=parseImg(p.image);h+=`<div class="card"><div class="pimg" style="background:${im.bg};cursor:pointer" onclick="openDetail(${p.id})">${im.label}</div><div style="flex:1;min-width:0"><div style="display:flex;justify-content:space-between;gap:8px"><div style="font-weight:700;font-size:13px;line-height:1.3;cursor:pointer" onclick="openDetail(${p.id})">${p.name}${low}</div><span style="cursor:pointer;font-size:11px;font-weight:700;color:${isWish?'#0A9EBB':'#94A3B8'};flex-shrink:0" onclick="toggleWish(${p.id})">${isWish?'SAVED':'SAVE'}</span></div><div style="font-size:11px;margin-top:4px">${stars(p.rating)} <span style="color:#94A3B8">(${p.reviews} reviews)</span></div><div style="font-size:11px;color:#94A3B8;margin-top:2px">${p.category} &middot; ${p.code}</div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px"><b style="font-size:16px">KSh ${p.price}</b><button class="btn" style="width:auto;padding:8px 16px;border-radius:20px;font-size:12px" onclick="add(${p.id})">${inC?'Added '+inC.qty:'Add to Cart'}</button></div></div></div>`;}document.getElementById('plist').innerHTML=h||'<div class="card" style="display:block;text-align:center">No products found</div>';document.getElementById('pCount').innerText=list.length+' items';}
function toggleWish(id){if(wishlist.includes(id))wishlist=wishlist.filter(x=>x!==id);else wishlist.push(id);saveWish();filterProducts();renderWishlist();}
function renderWishlist(){let list=all.filter(p=>wishlist.includes(p.id));document.getElementById('wishList').innerHTML=list.length?list.map(p=>{let im=parseImg(p.image);return `<div class="card"><div class="pimg" style="background:${im.bg}">${im.label}</div><div style="flex:1"><b style="font-size:13px">${p.name}</b><div>KSh ${p.price}</div><button class="btn" style="width:auto;padding:8px 18px;margin-top:8px" onclick="add(${p.id});show('cart')">Add to Cart</button></div></div>`}).join(''):'<div class="card" style="display:block;text-align:center">No saved items yet. Tap SAVE on products.</div>';}
async function openDetail(id){let p=all.find(x=>x.id===id);let im=parseImg(p.image);let r=await fetch('/api/reviews/'+id);let revs=await r.json();document.getElementById('detailContent').innerHTML=`<div class="card" style="display:block;text-align:center;padding:20px"><div style="background:${im.bg};border-radius:14px;font-size:15px;font-weight:800;color:#fff;padding:28px;letter-spacing:1px">${im.label}</div><h3>${p.name}</h3><div>${stars(p.rating)} <span style="color:#64748B">(${p.reviews} reviews)</span></div><p style="color:#64748B">${p.category} &middot; ${p.code} &middot; Stock: ${p.stock}</p><h2>KSh ${p.price}</h2><div style="display:flex;gap:8px"><button class="btn" onclick="add(${id})">Add to Cart</button><button class="btn" style="background:#fff;color:#000;border:1px solid #E2E8F0" onclick="toggleWish(${id})">Save Item</button></div><button class="btn" style="background:#0A9EBB;margin-top:8px" onclick="shareToCommunity(${id})">Share to Community</button></div><div class="card" style="display:block"><h4>Reviews</h4><div id="revList">${revs.map(x=>`<div style="border-bottom:1px solid #F1F5F9;padding:8px 0"><b>${x.name}</b> <span class="star">${'★'.repeat(x.rating)}</span><div style="font-size:13px">${x.text}</div></div>`).join('')||'No reviews yet'}</div><input id="revName" placeholder="Your name"><select id="revRating"><option value="5">5 Stars - Excellent</option><option value="4">4 Stars - Good</option><option value="3">3 Stars - Average</option></select><input id="revText" placeholder="Write review..."><button class="btn btn-teal" onclick="submitReview(${id})">Submit Review</button></div>`;show('productDetail');}
async function shareToCommunity(id){let p=all.find(x=>x.id===id);let u=getUser();if(!u){alert('Sign in first');show('account');return;}await fetch('/api/community/post',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author:u.name,phone:u.phone,text:'Just bought '+p.name+' for KSh '+p.price+'. Who else has tried it? #LONMA #'+p.category.replace(' ','')})});show('community');loadCommunity();}
async function submitReview(id){let name=document.getElementById('revName').value||'Customer';let rating=document.getElementById('revRating').value;let text=document.getElementById('revText').value;await fetch('/api/reviews/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:id,name,rating,text})});openDetail(id);}
function add(id){let p=all.find(x=>x.id===id);let f=cart.find(c=>c.id===id);if(f)f.qty++;else cart.push({id:p.id,name:p.name,price:p.price,image:p.image,qty:1});save();filterProducts();}
async function applyPromo(){let code=document.getElementById('promoCode').value.trim();let r=await fetch('/api/promo/check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code})});let d=await r.json();if(d.valid){promoDiscount=d.discount;promoCode=code;document.getElementById('promoMsg').innerText='Applied: '+d.discount+'% OFF ('+code+')';}else{promoDiscount=0;document.getElementById('promoMsg').innerText='Invalid code';}renderCart();}
function calcTotals(){let sub=0;for(let i of cart)sub+=i.price*i.qty;let disc=Math.round(sub*promoDiscount/100);let area=document.getElementById('area').value;let del=area==='CBD'?150:area==='Upcountry'?350:200;if(sub-disc>=2000)del=0;if(promoCode==='FREEDEL')del=0;let tot=sub-disc+del;return {sub,disc,del,tot};}
function renderCart(){let cont=document.getElementById('cartItems'),sum=document.getElementById('cartSum'),empty=document.getElementById('emptyCart');if(cart.length===0){cont.innerHTML='';sum.style.display='none';empty.style.display='block';return;}empty.style.display='none';sum.style.display='block';let html='';for(let it of cart){let im=parseImg(it.image);html+=`<div class="card"><div class="pimg" style="width:60px;height:60px;font-size:11px;background:${im.bg}">${im.label}</div><div style="flex:1"><b style="font-size:13px">${it.name}</b><div style="display:flex;gap:8px;align-items:center;margin-top:6px"><button onclick="chg(${it.id},-1)" style="width:28px;height:28px;border-radius:50%;border:1px solid #E2E8F0;background:#fff">-</button><span>${it.qty}</span><button onclick="chg(${it.id},1)" style="width:28px;height:28px;border-radius:50%;border:1px solid #E2E8F0;background:#fff">+</button><span style="margin-left:auto;font-weight:800">KSh ${it.price*it.qty}</span></div></div></div>`;}cont.innerHTML=html;let t=calcTotals();document.getElementById('sub').innerText=t.sub;document.getElementById('discFee').innerText='- KSh '+t.disc;document.getElementById('tItems').innerText=cart.reduce((a,b)=>a+b.qty,0);document.getElementById('delFee').innerText=t.del==0?'FREE':'KSh '+t.del;document.getElementById('tot').innerText=t.tot;document.getElementById('pay').innerText=t.tot;}
function chg(id,d){let f=cart.find(c=>c.id===id);if(!f)return;f.qty+=d;if(f.qty<=0)cart=cart.filter(c=>c.id!==id);save();renderCart();}
function show(id){document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('.bottom div').forEach(b=>b.classList.remove('active'));let btn=document.getElementById('b-'+id);if(btn)btn.classList.add('active');if(id==='cart')renderCart();if(id==='account')loadCustomerDashboard();if(id==='wishlist')renderWishlist();if(id==='community')loadCommunity();closeMenu();window.scrollTo(0,0);}
async function loadP(){let r=await fetch('/api/products');all=await r.json();render(all);renderWishlist();}
async function verify(){let c=document.getElementById('vcode').value.trim();let r=await fetch('/api/verify/'+c);let d=await r.json();document.getElementById('vres').innerText=d.valid?'Authentic: '+d.product.name:'Invalid Code';}
async function trackOrder(){let no=document.getElementById('trackNo').value.trim();let r=await fetch('/api/track/'+no);let d=await r.json();if(!d.found){document.getElementById('trackRes').innerHTML='Order not found';return;}document.getElementById('trackRes').innerHTML=`<b>${d.order_no}</b> &middot; KSh ${d.total} &middot; ${d.status}<div class="progress" style="margin-top:10px"><div style="width:${d.progress}%"></div></div><div style="display:flex;justify-content:space-between;font-size:11px;margin-top:6px"><span>Pending</span><span>Paid</span><span>Shipped</span><span>Delivered</span></div>`;}
async function checkout(){let name=document.getElementById('custName').value.trim(),phone=document.getElementById('phone').value.trim(),area=document.getElementById('area').value,loc=document.getElementById('loc').value.trim();if(!name||!phone||!area||!loc||!document.getElementById('agree').checked){document.getElementById('ps').innerText='Please fill all fields and agree to Terms';return;}let t=calcTotals();document.getElementById('ps').innerText='Sending M-Pesa prompt...';let r=await fetch('/mpesa/stkpush',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone,amount:t.tot,cart,name,area,location:loc})});let d=await r.json();document.getElementById('ps').innerText=d.message;if(d.status==='ok'){myOrders.unshift({order_no:d.order_no,total:t.tot,status:'Pending',created:new Date().toLocaleString()});localStorage.setItem('my_orders',JSON.stringify(myOrders));document.getElementById('rcont').innerHTML=`<h3>${d.order_no}</h3><p>Total KSh ${t.tot} ${promoDiscount?'('+promoDiscount+'% OFF)':''}</p><p style="font-size:12px;color:#64748B">Check your phone for the M-Pesa prompt</p><button class="btn" style="margin-top:12px" onclick="document.getElementById('trackNo').value='${d.order_no}';show('track');trackOrder()">Track This Order</button>`;cart=[];promoDiscount=0;localStorage.removeItem('lonma_cart');save();show('receipt');}}
async function loadOrders(){let ph=document.getElementById('phLookup').value.trim();let r=await fetch('/api/orders?phone='+ph);let data=await r.json();document.getElementById('olist').innerHTML=data.map(o=>`<div class="card" style="display:block"><div style="display:flex;justify-content:space-between"><b>${o.order_no}</b><span style="background:#F1F5F9;padding:4px 10px;border-radius:20px;font-size:11px">${o.status}</span></div><div style="margin-top:6px">KSh ${o.total} &middot; ${o.created}</div></div>`).join('');document.getElementById('noOrd').style.display=data.length?'none':'block';}
function switchAdminTab(tab,el){document.querySelectorAll('.dtab').forEach(t=>t.classList.remove('active'));el.classList.add('active');document.getElementById('aOrdersList').style.display=tab==='orders'?'block':'none';document.getElementById('aCustList').style.display=tab==='customers'?'block':'none';document.getElementById('aStockList').style.display=tab==='stock'?'block':'none';document.getElementById('aAdd').style.display=tab==='add'?'block':'none';}
async function adminLogin(){let p=document.getElementById('apass').value;let r=await fetch('/api/admin/check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p})});let d=await r.json();document.getElementById('ast').innerText=d.message||'';if(d.status==='ok'){adminPass=p;document.getElementById('adminLoginBox').style.display='none';document.getElementById('acont').style.display='block';let r2=await fetch('/api/admin/dashboard?password='+encodeURIComponent(p));adminData=await r2.json();document.getElementById('aSales').innerText='KSh '+adminData.total_sales;document.getElementById('aOrders').innerText=adminData.total_orders;document.getElementById('aCust').innerText=adminData.total_customers;document.getElementById('aProd').innerText=adminData.total_products;document.getElementById('aPosts').innerText=adminData.total_posts;document.getElementById('aOrdersList').innerHTML=adminData.orders.map(o=>`<div class="card" style="display:block"><div style="display:flex;justify-content:space-between"><b>${o.order_no}</b><select onchange="changeStatus('${o.order_no}',this.value)" style="width:auto;padding:6px;margin:0;font-size:11px"><option ${o.status==='Pending'?'selected':''}>Pending</option><option ${o.status==='PAID'?'selected':''}>PAID</option><option ${o.status==='Shipped'?'selected':''}>Shipped</option><option ${o.status==='Delivered'?'selected':''}>Delivered</option></select></div><div style="font-size:12px;margin-top:6px">${o.name} &middot; ${o.phone}<br>KSh ${o.total} &middot; ${o.created}</div></div>`).join('')||'No orders';document.getElementById('aCustList').innerHTML=adminData.customers.map(c=>`<div class="card" style="display:block"><b>${c.name}</b><div style="font-size:12px;color:#64748B">${c.phone} &middot; ${c.orders} orders &middot; Spent KSh ${c.spent}</div></div>`).join('')||'No customers';document.getElementById('aStockList').innerHTML=adminData.products.map(p=>`<div class="card" style="display:block"><div style="display:flex;justify-content:space-between"><b style="font-size:13px">${p.name}</b><span style="font-weight:800;color:${p.stock<=8?'#EF4444':'#16A34A'}">${p.stock} left</span></div><div style="font-size:12px;color:#64748B">${p.category} &middot; KSh ${p.price}</div><button style="margin-top:8px;background:#FEE2E2;border:none;padding:6px 12px;border-radius:10px;font-size:11px" onclick="deleteProduct(${p.id})">Delete</button></div>`).join('');}}
async function changeStatus(order_no,status){await fetch('/api/admin/update_status',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminPass,order_no,status})});}
async function addProduct(){let name=document.getElementById('npName').value,price=document.getElementById('npPrice').value,code=document.getElementById('npCode').value,cat=document.getElementById('npCat').value,stock=document.getElementById('npStock').value;let r=await fetch('/api/admin/add_product',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminPass,name,price,code,category:cat,stock})});let d=await r.json();document.getElementById('npMsg').innerText=d.status==='ok'?'Added. Refresh page.':'Error';if(d.status==='ok')loadP();}
async function deleteProduct(id){if(!confirm('Delete this product?'))return;await fetch('/api/admin/delete_product',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminPass,id})});adminLogin();}
async function loadCustomerDashboard(){let u=getUser();if(!u){document.getElementById('out').style.display='block';document.getElementById('in').style.display='none';return;}document.getElementById('out').style.display='none';document.getElementById('in').style.display='block';document.getElementById('an').innerText='Welcome, '+u.name;document.getElementById('ap').innerText=u.phone;let r=await fetch('/api/customer/dashboard?phone='+encodeURIComponent(u.phone));let d=await r.json();document.getElementById('cOrders').innerText=d.total_orders;document.getElementById('cSpent').innerText='KSh '+d.total_spent;document.getElementById('cPoints').innerText=d.points;document.getElementById('cPhone').innerText=d.phone;document.getElementById('cList').innerHTML=d.orders.map(o=>`<div class="card" style="display:block"><div style="display:flex;justify-content:space-between"><b>${o.order_no}</b><span style="background:#F1F5F9;padding:4px 10px;border-radius:20px;font-size:11px">${o.status}</span></div><div style="margin-top:6px">KSh ${o.total} &middot; ${o.created}</div></div>`).join('')||'<div class="card" style="display:block;text-align:center">No orders yet</div>';}
async function register(){let name=document.getElementById('rn').value.trim(),phone=document.getElementById('rp').value.trim(),pass=document.getElementById('rpass').value.trim();let r=await fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,phone,password:pass})});let d=await r.json();document.getElementById('rs').innerText=d.status==='ok'?'Account created':'Error';if(d.status==='ok'){localStorage.setItem('lonma_user',JSON.stringify(d.user));loadCustomerDashboard();}}
async function login(){let phone=document.getElementById('lp').value.trim(),pass=document.getElementById('lpass').value.trim();let r=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone,password:pass})});let d=await r.json();document.getElementById('ls').innerText=d.status==='ok'?'Welcome back':'Wrong credentials';if(d.status==='ok'){localStorage.setItem('lonma_user',JSON.stringify(d.user));loadCustomerDashboard();}}
function logout(){localStorage.removeItem('lonma_user');document.getElementById('out').style.display='block';document.getElementById('in').style.display='none';}
document.getElementById('area')?.addEventListener('change',renderCart);
loadP();updateCount();loadCustomerDashboard();
</script></body></html>
"""

@app.api_route("/",methods=["GET","HEAD"])
def home(): return HTMLResponse(HTML)
@app.get("/logo.png")
def logo():
    for f in ["logo.png","static/logo.png","./logo.png","images/logo.png"]:
        if os.path.exists(f): return FileResponse(f)
    return HTMLResponse("",200)

def keep_alive():
    while True:
        time.sleep(500)
        try: requests.get("https://app.lonmaorbit.co.ke",timeout=5)
        except: pass
Thread(target=keep_alive, daemon=True).start()
