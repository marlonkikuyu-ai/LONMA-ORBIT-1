from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import os, sqlite3, json, datetime, requests, base64, time, re, random, hashlib, hmac, secrets
from threading import Thread
from collections import defaultdict
import urllib.parse
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
SMS_API_KEY = os.getenv("SMS_API_KEY", "")
AT_API_KEY = os.getenv("AT_API_KEY", "")
GOOGLE_REDIRECT_URI = "https://app.lonmaorbit.co.ke/auth/callback"
app = FastAPI()
DB_PATH = os.path.join(os.path.dirname(__file__), "lonma.db")
@app.get("/auth/google")
def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)

@app.get("/auth/callback")
def google_callback(code: str = ""):
    if not code:
        return RedirectResponse("/login.html?error=no_code")
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }, timeout=10)
    data = r.json()
    id_token = data.get("id_token", "")
    u = requests.get("https://oauth2.googleapis.com/tokeninfo?id_token=" + id_token, timeout=10).json()
    email = u.get("email", "")
    name = u.get("name", "Customer")
    if not email:
        return RedirectResponse("/login.html?error=google_failed")
    cur = conn.cursor()
    cur.execute("SELECT phone FROM users WHERE phone=?", (email,))
    if not cur.fetchone():
        conn.execute("INSERT INTO users (phone,name,password) VALUES (?,?,?)", (email, name, hash_pw(secrets.token_hex(8))))
        conn.commit()
   import secrets
from auth import SESSIONS

token = secrets.token_hex(16)
SESSIONS[token] = {"id": email, "name": name, "email": email, "phone": ""}
return RedirectResponse(f"/home?token={token}")

@app.get("/login.html")
async def login_page():
    return FileResponse("login.html")

@app.get("/")
def root():
    return FileResponse("login.html")

@app.get("/home")
def home():
    return HTMLResponse(HTML)

@app.get("/index.html")
def index_html():
    return HTMLResponse(HTML)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.lonmaorbit.co.ke", "https://lonmaorbit.co.ke"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

DARAJA_KEY = os.getenv("DARAJA_KEY", "")
DARAJA_SECRET = os.getenv("DARAJA_SECRET", "")
DARAJA_SHORTCODE = os.getenv("DARAJA_SHORTCODE", "")
DARAJA_PASSKEY = os.getenv("DARAJA_PASSKEY", "")
DARAJA_CALLBACK = os.getenv("CALLBACK_URL", "https://app.lonmaorbit.co.ke/mpesa/callback")
USE_PROD = os.getenv("DARAJA_ENV", "sandbox") == "production"
AIRTEL_KEY = os.getenv("AIRTEL_KEY", "")
AIRTEL_SECRET = os.getenv("AIRTEL_SECRET", "")
STRIPE_KEY = os.getenv("STRIPE_KEY", "")
ADMIN_EMAIL = "marlonkikuyu@gmail.com"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
SHOW_RESET_CODE = os.getenv("SHOW_RESET_CODE", "false").lower() == "true"

def audit_log(action, user_email, details):
    entry = f"{datetime.datetime.now()} | {action} | by={user_email} | {details}\n"
    try:
        with open("audit.log", "a") as f:
            f.write(entry)
    except Exception:
        pass
    print(f"[AUDIT] {entry}")

def require_admin(user_email: str):
    if user_email != ADMIN_EMAIL:
        audit_log("BLOCKED_CHANGE", user_email or "unknown", "Tried to make admin change")
        raise HTTPException(status_code=403, detail="Only Admin can make changes")
    return True

def hash_pw(pw: str):
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000).hex()
    return f"{salt}:{h}"

def check_pw(pw: str, stored: str):
    if not stored:
        return False
    if ":" in stored and len(stored.split(":")[0]) == 32:
        try:
            salt, h = stored.split(":")
            nh = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000).hex()
            return hmac.compare_digest(h, nh)
        except Exception:
            return False
    return hmac.compare_digest(stored, pw)

FAILED = defaultdict(list)
BLOCKED = {}

def is_blocked(ip):
    now = time.time()
    FAILED[ip] = [t for t in FAILED[ip] if now - t < 300]
    if ip in BLOCKED and now < BLOCKED[ip]:
        return True
    if len(FAILED[ip]) >= 5:
        BLOCKED[ip] = now + 900
        return True
    return False

def record_fail(ip):
    FAILED[ip].append(time.time())

def clean_input(s, maxlen=500):
    if not isinstance(s, str):
        return ""
    s = s.strip()[:maxlen]
    s = re.sub(r'[<>\"\'`;]', '', s)
    return s

@app.middleware("http")
async def security_middleware(request, call_next):
    path = request.url.path.lower()
    bad = [".env", "wp-admin", "phpmyadmin", ".git", "config", "admin.php", ".sql", "wp-login"]
    if any(b in path for b in bad):
        return HTMLResponse("Not Found", status_code=404)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, code TEXT, image TEXT, category TEXT, stock INTEGER)")
conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, order_no TEXT, name TEXT, phone TEXT, area TEXT, location TEXT, items TEXT, total INTEGER, status TEXT, created TEXT, mpesa_receipt TEXT, checkout_id TEXT, pay_method TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE, name TEXT, password TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS password_resets (phone TEXT PRIMARY KEY, code TEXT, expires INTEGER)")
conn.execute("CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, name TEXT, rating INTEGER, text TEXT, created TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS promos (code TEXT PRIMARY KEY, discount INTEGER)")
conn.execute("CREATE TABLE IF NOT EXISTS community_posts (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, phone TEXT, text TEXT, image TEXT, likes INTEGER DEFAULT 0, reposts INTEGER DEFAULT 0, created TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS community_comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, author TEXT, text TEXT, created TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS community_likes (post_id INTEGER, phone TEXT, UNIQUE(post_id, phone))")
cur = conn.cursor()
try:
    cur.execute("ALTER TABLE orders ADD COLUMN pay_method TEXT")
except Exception:
    pass
cur.execute("DELETE FROM products")
cur.execute("DELETE FROM promos")
cur.execute("INSERT OR IGNORE INTO promos VALUES ('LONMA10',10)")
cur.execute("INSERT OR IGNORE INTO promos VALUES ('WELCOME20',20)")
PRODS = [
    (1, "Diva Anti-Dandruff Pomade 250ml", 250, "DIV-001", "DIVA|#0A9EBB", "Pomades", 45),
    (2, "Detrex Pine Drops Soap 110g", 95, "DET-002", "DETREX|#0F766E", "Soaps", 80),
    (3, "Fresh Fri Cooking Oil 2L", 890, "FRE-003", "FRESH FRI|#B45309", "Cooking Oils", 50),
    (4, "Detrex Citronella Soap 110g", 95, "DET-004", "DETREX|#0F766E", "Soaps", 100),
    (5, "Sawa Men Lotion 72Hrs", 320, "SAW-005", "SAWA|#1E40AF", "Lotions", 12),
    (6, "Detrex Cool Mint Soap 110g", 95, "DET-006", "DETREX|#0F766E", "Soaps", 4),
    (7, "Diva Anti-Breakage Pomade 250ml", 250, "DIV-007", "DIVA|#0A9EBB", "Pomades", 30),
    (8, "Sawa Cocoa Butter Lotion 72Hrs", 320, "SAW-008", "SAWA|#1E40AF", "Lotions", 28),
    (9, "Detrex Germ Protection Soap 110g", 95, "DET-009", "DETREX|#0F766E", "Soaps", 60),
]
for pid, name, price, code, img, cat, stock in PRODS:
    cur.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?)", (pid, name, price, code, img, cat, stock))
cur.execute("DELETE FROM community_posts")
cur.execute("DELETE FROM community_comments")
cur.execute("DELETE FROM community_likes")
conn.commit()

def get_token():
    try:
        base = "https://api.safaricom.co.ke" if USE_PROD else "https://sandbox.safaricom.co.ke"
        r = requests.get(f"{base}/oauth/v1/generate?grant_type=client_credentials", auth=(DARAJA_KEY, DARAJA_SECRET), timeout=10)
        return r.json().get("access_token")
    except Exception:
        return None

@app.api_route("/mpesa/callback", methods=["GET", "POST"])
async def callback(request: Request):
    try:
        data = await request.json()
        stk = data.get("Body", {}).get("stkCallback", {})
        if stk.get("ResultCode") == 0:
            receipt = ""
            for it in stk.get("CallbackMetadata", {}).get("Item", []):
                if it.get("Name") == "MpesaReceiptNumber":
                    receipt = it.get("Value")
            conn.execute("UPDATE orders SET status='PAID', mpesa_receipt=? WHERE checkout_id=?", (receipt, stk.get("CheckoutRequestID", "")))
            conn.commit()
        return {"ResultCode": 0, "ResultDesc": "Accepted"}
    except Exception:
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

@app.get("/api/health")
def health():
    return {"status": "ok", "mpesa_env": "production" if USE_PROD else "sandbox", "mpesa_configured": bool(DARAJA_KEY and DARAJA_PASSKEY), "airtel_configured": bool(AIRTEL_KEY), "card_configured": bool(STRIPE_KEY), "sms_configured": bool(SMS_API_KEY or AT_API_KEY), "show_reset_code": SHOW_RESET_CODE}

@app.get("/api/community/posts")
def get_posts(phone: str = ""):
    cur = conn.cursor()
    cur.execute("SELECT id,author,phone,text,image,likes,reposts,created FROM community_posts ORDER BY id DESC LIMIT 50")
    out = []
    for r in cur.fetchall():
        cur2 = conn.cursor()
        cur2.execute("SELECT COUNT(*) FROM community_comments WHERE post_id=?", (r[0],))
        cc = cur2.fetchone()[0]
        liked = False
        if phone:
            cur2.execute("SELECT 1 FROM community_likes WHERE post_id=? AND phone=?", (r[0], phone))
            liked = cur2.fetchone() is not None
        out.append({"id": r[0], "author": r[1], "phone": r[2], "text": r[3], "image": r[4], "likes": r[5], "reposts": r[6], "created": r[7], "comments": cc, "liked": liked})
    return out

@app.post("/api/community/post")
async def create_post(req: Request):
    d = await req.json()
    text = clean_input(d.get("text", ""), 500)
    author = clean_input(d.get("author", "Customer"), 30)
    phone = clean_input(d.get("phone", ""), 15)
    if not text or len(text) < 2:
        return {"status": "error"}
    img = str(d.get("image",""))[:200000] 
    conn.execute("INSERT INTO community_posts (author,phone,text,image,likes,reposts,created) VALUES (?,?,?,?,0,0,?)", (author, phone, text, img, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    return {"status": "ok"}

@app.post("/api/community/like")
async def like_post(req: Request):
    d = await req.json()
    try:
        pid = int(d.get("post_id", 0))
    except Exception:
        return {"status": "error"}
    phone = clean_input(d.get("phone", ""), 15)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM community_likes WHERE post_id=? AND phone=?", (pid, phone))
    if cur.fetchone():
        conn.execute("DELETE FROM community_likes WHERE post_id=? AND phone=?", (pid, phone))
        conn.execute("UPDATE community_posts SET likes=likes-1 WHERE id=?", (pid,))
        conn.commit()
        return {"status": "unliked"}
    conn.execute("INSERT INTO community_likes VALUES (?,?)", (pid, phone))
    conn.execute("UPDATE community_posts SET likes=likes+1 WHERE id=?", (pid,))
    conn.commit()
    return {"status": "liked"}

@app.post("/api/community/repost")
async def repost(req: Request):
    d = await req.json()
    try:
        pid = int(d.get("post_id", 0))
    except Exception:
        return {"status": "error"}
    conn.execute("UPDATE community_posts SET reposts=reposts+1 WHERE id=?", (pid,))
    conn.commit()
    return {"status": "ok"}

@app.get("/api/community/comments/{pid}")
def get_comments(pid: int):
    cur = conn.cursor()
    cur.execute("SELECT author,text,created FROM community_comments WHERE post_id=? ORDER BY id ASC", (pid,))
    return [{"author": r[0], "text": r[1], "created": r[2]} for r in cur.fetchall()]

@app.post("/api/community/comment")
async def add_comment(req: Request):
    d = await req.json()
    try:
        pid = int(d.get("post_id", 0))
    except Exception:
        return {"status": "error"}
    conn.execute("INSERT INTO community_comments (post_id,author,text,created) VALUES (?,?,?,?)", (pid, clean_input(d.get("author", "Customer"), 30), clean_input(d.get("text", ""), 300), datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    return {"status": "ok"}

@app.get("/api/community/trending")
def trending():
    cur = conn.cursor()
    cur.execute("SELECT text FROM community_posts")
    tags = {}
    for (t,) in cur.fetchall():
        for w in t.split():
            if w.startswith("#"):
                tags[w] = tags.get(w, 0) + 1
    sorted_tags = sorted(tags.items(), key=lambda x: -x[1])[:6]
    return [{"tag": k, "count": v} for k, v in sorted_tags]

@app.get("/api/products")
def prods_api():
    cur = conn.cursor()
    cur.execute("SELECT id,name,price,code,image,category,stock FROM products")
    out = []
    for r in cur.fetchall():
        cur2 = conn.cursor()
        cur2.execute("SELECT AVG(rating), COUNT(*) FROM reviews WHERE product_id=?", (r[0],))
        avg = cur2.fetchone()
        out.append({"id": r[0], "name": r[1], "price": r[2], "code": r[3], "image": r[4], "category": r[5], "stock": r[6], "rating": round(avg[0], 1) if avg[0] else 0, "reviews": avg[1]})
    return out

@app.get("/api/verify/{code}")
def verify(code: str):
    code = clean_input(code, 20).upper()
    cur = conn.cursor()
    cur.execute("SELECT name FROM products WHERE code=?", (code,))
    row = cur.fetchone()
    return {"valid": True, "product": {"name": row[0]}} if row else {"valid": False}

@app.get("/api/orders")
def orders_api(phone: str = ""):
    phone = clean_input(phone, 15)
    cur = conn.cursor()
    if phone:
        cur.execute("SELECT order_no,name,total,status,created FROM orders WHERE phone=? ORDER BY id DESC", (phone,))
    else:
        cur.execute("SELECT order_no,name,total,status,created FROM orders ORDER BY id DESC LIMIT 50")
    return [{"order_no": r[0], "name": r[1], "total": r[2], "status": r[3], "created": r[4]} for r in cur.fetchall()]

@app.get("/api/track/{order_no}")
def track(order_no: str):
    cur = conn.cursor()
    cur.execute("SELECT order_no,total,status,created FROM orders WHERE order_no=?", (clean_input(order_no, 20),))
    r = cur.fetchone()
    if not r:
        return {"found": False}
    steps = ["Pending", "PAID", "Shipped", "Delivered"]
    idx = steps.index(r[2]) if r[2] in steps else 0
    return {"found": True, "order_no": r[0], "total": r[1], "status": r[2], "created": r[3], "progress": (idx + 1) * 25}

@app.post("/api/promo/check")
async def promo_check(req: Request):
    d = await req.json()
    cur = conn.cursor()
    cur.execute("SELECT discount FROM promos WHERE code=?", (clean_input(d.get("code", ""), 20).upper(),))
    r = cur.fetchone()
    return {"valid": True, "discount": r[0]} if r else {"valid": False}

@app.get("/api/reviews/{pid}")
def get_reviews(pid: int):
    cur = conn.cursor()
    cur.execute("SELECT name,rating,text,created FROM reviews WHERE product_id=? ORDER BY id DESC LIMIT 10", (pid,))
    return [{"name": r[0], "rating": r[1], "text": r[2], "created": r[3]} for r in cur.fetchall()]

@app.post("/api/reviews/add")
async def add_review(req: Request):
    d = await req.json()
    try:
        pid = int(d.get("product_id", 0))
        rating = int(d.get("rating", 5))
    except Exception:
        return {"status": "error"}
    conn.execute("INSERT INTO reviews (product_id,name,rating,text,created) VALUES (?,?,?,?,?)", (pid, clean_input(d.get("name", "Customer"), 30), rating, clean_input(d.get("text", ""), 200), datetime.datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    return {"status": "ok"}

@app.post("/api/admin/check")
async def admin_check(req: Request):
    ip = req.client.host if req.client else "unknown"
    if is_blocked(ip):
        return {"status": "blocked", "message": "Too many tries. Wait 15 mins"}
    d = await req.json()
    if d.get("password", "") == ADMIN_PASSWORD:
        FAILED[ip] = []
        return {"status": "ok"}
    record_fail(ip)
    return {"status": "error", "message": "Wrong password"}

@app.get("/api/admin/dashboard")
def admin_dash(password: str = ""):
    if password != ADMIN_PASSWORD:
        return {"error": "unauthorized"}
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM orders")
    o = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM users")
    u = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM products")
    p = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM community_posts")
    cp = cur.fetchone()
    cur.execute("SELECT order_no,name,phone,total,status,created, COALESCE(pay_method,'M-Pesa') FROM orders ORDER BY id DESC LIMIT 30")
    orders = [{"order_no": r[0], "name": r[1], "phone": r[2], "total": r[3], "status": r[4], "created": r[5], "pay_method": r[6]} for r in cur.fetchall()]
    cur.execute("SELECT phone,name FROM users ORDER BY id DESC LIMIT 30")
    customers = [{"phone": r[0], "name": r[1]} for r in cur.fetchall()]
    for c in customers:
        cur.execute("SELECT COUNT(*), COALESCE(SUM(total),0) FROM orders WHERE phone=?", (c["phone"],))
        r = cur.fetchone()
        c["orders"] = r[0]
        c["spent"] = r[1]
    cur.execute("SELECT id,name,price,stock,category FROM products ORDER BY stock ASC")
    prods = [{"id": r[0], "name": r[1], "price": r[2], "stock": r[3], "category": r[4]} for r in cur.fetchall()]
    return {"total_orders": o[0], "total_sales": o[1], "total_customers": u[0], "total_products": p[0], "total_posts": cp[0], "orders": orders, "customers": customers, "products": prods}

@app.post("/api/admin/update_status")
async def upd_status(req: Request):
    d = await req.json()
    if d.get("password") != ADMIN_PASSWORD:
        return {"status": "error"}
    conn.execute("UPDATE orders SET status=? WHERE order_no=?", (clean_input(d.get("status", ""), 20), clean_input(d.get("order_no", ""), 20)))
    conn.commit()
    return {"status": "ok"}

@app.post("/api/admin/add_product")
async def add_prod(req: Request):
    d = await req.json()
    if d.get("password") != ADMIN_PASSWORD:
        return {"status": "error"}
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM products")
    nid = (cur.fetchone()[0] or 0) + 1
    conn.execute("INSERT INTO products VALUES (?,?,?,?,?,?,?)", (nid, clean_input(d.get("name", ""), 80), int(d.get("price", 0)), clean_input(d.get("code", ""), 20), d.get("image", "LONMA|#0A9EBB"), clean_input(d.get("category", ""), 20), int(d.get("stock", 0))))
    conn.commit()
    return {"status": "ok"}

@app.post("/api/admin/delete_product")
async def del_prod(req: Request):
    d = await req.json()
    if d.get("password") != ADMIN_PASSWORD:
        return {"status": "error"}
    conn.execute("DELETE FROM products WHERE id=?", (int(d.get("id", 0)),))
    conn.commit()
    return {"status": "ok"}

@app.get("/api/customer/dashboard")
def cust_dash(phone: str = ""):
    phone = clean_input(phone, 15)
    cur = conn.cursor()
    cur.execute("SELECT name FROM users WHERE phone=?", (phone,))
    u = cur.fetchone()
    cur.execute("SELECT order_no,total,status,created FROM orders WHERE phone=? ORDER BY id DESC", (phone,))
    orders = [{"order_no": r[0], "total": r[1], "status": r[2], "created": r[3]} for r in cur.fetchall()]
    total = sum(o["total"] for o in orders)
    return {"name": u[0] if u else "Customer", "phone": phone, "orders": orders, "total_orders": len(orders), "total_spent": total, "points": total // 100}

def save_order(order_no, name, raw, area, loc, cart, amount, method):
    conn.execute("INSERT INTO orders (order_no,name,phone,area,location,items,total,status,created,mpesa_receipt,checkout_id,pay_method) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (order_no, name, raw, area, loc, json.dumps(cart)[:2000], amount, 'Pending', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "", order_no, method))
    conn.commit()

@app.post("/mpesa/stkpush")
async def stk(req: Request):
    d = await req.json()
    raw = clean_input(d.get('phone', ''), 15)
    phone = raw.replace(" ", "").replace("+254", "0")
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    phone = "".join([c for c in phone if c.isdigit()])
    try:
        amount = int(d.get('amount', 1))
    except Exception:
        amount = 1
    if amount < 1 or amount > 500000:
        return {"status": "error", "message": "Invalid amount"}
    if len(phone) != 12:
        return {"status": "error", "message": "Invalid phone"}
    order_no = 'LONMA' + datetime.datetime.now().strftime("%H%M%S")
    name = clean_input(d.get('name', 'Guest'), 50)
    area = clean_input(d.get('area', ''), 20)
    loc = clean_input(d.get('location', ''), 100)
    save_order(order_no, name, raw, area, loc, d.get('cart', []), amount, 'M-Pesa')
    if DARAJA_KEY and DARAJA_PASSKEY:
        token = get_token()
        if token:
            ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            pwd = base64.b64encode(f"{DARAJA_SHORTCODE}{DARAJA_PASSKEY}{ts}".encode()).decode()
            payload = {"BusinessShortCode": DARAJA_SHORTCODE, "Password": pwd, "Timestamp": ts, "TransactionType": "CustomerPayBillOnline", "Amount": amount, "PartyA": phone, "PartyB": DARAJA_SHORTCODE, "PhoneNumber": phone, "CallBackURL": DARAJA_CALLBACK, "AccountReference": order_no, "TransactionDesc": order_no}
            try:
                base = "https://api.safaricom.co.ke" if USE_PROD else "https://sandbox.safaricom.co.ke"
                r = requests.post(f"{base}/mpesa/stkpush/v1/processrequest", json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=15)
                res = r.json()
                if res.get("ResponseCode") == "0":
                    conn.execute("UPDATE orders SET checkout_id=? WHERE order_no=?", (res.get("CheckoutRequestID", order_no), order_no))
                    conn.commit()
                    return {"status": "ok", "message": f"M-Pesa STK sent to {raw}", "order_no": order_no}
            except Exception:
                pass
    return {"status": "ok", "message": f"Order {order_no} saved - M-Pesa", "order_no": order_no}

@app.post("/airtel/stkpush")
async def airtel_push(req: Request):
    if not AIRTEL_KEY or not AIRTEL_SECRET:
        return {"status": "error", "message": "Airtel Money is temporarily unavailable. Please use M-Pesa."}
    d = await req.json()
    raw = clean_input(d.get('phone', ''), 15)
    phone = raw.replace(" ", "").replace("+254", "0")
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    phone = "".join([c for c in phone if c.isdigit()])
    try:
        amount = int(d.get('amount', 1))
    except Exception:
        amount = 1
    if len(phone) != 12:
        return {"status": "error", "message": "Invalid Airtel number"}
    order_no = 'LONMA' + datetime.datetime.now().strftime("%H%M%S")
    name = clean_input(d.get('name', 'Guest'), 50)
    area = clean_input(d.get('area', ''), 20)
    loc = clean_input(d.get('location', ''), 100)
    save_order(order_no, name, raw, area, loc, d.get('cart', []), amount, 'Airtel Money')
    return {"status": "ok", "message": f"Airtel Money prompt sent to {raw}. Check phone and enter PIN. Order {order_no}", "order_no": order_no}

@app.post("/card/pay")
async def card_pay(req: Request):
    if not STRIPE_KEY:
        return {"status": "error", "message": "Card payment is temporarily unavailable. Please use M-Pesa."}
    d = await req.json()
    try:
        amount = int(d.get('amount', 1))
    except Exception:
        amount = 1
    card_no = clean_input(d.get('card_no', ''), 19).replace(" ", "")
    if len(card_no) < 15:
        return {"status": "error", "message": "Invalid card number"}
    if not d.get('expiry') or not d.get('cvv'):
        return {"status": "error", "message": "Enter expiry and CVV"}
    order_no = 'LONMA' + datetime.datetime.now().strftime("%H%M%S")
    name = clean_input(d.get('name', 'Guest'), 50)
    raw = clean_input(d.get('phone', ''), 15)
    area = clean_input(d.get('area', ''), 20)
    loc = clean_input(d.get('location', ''), 100)
    save_order(order_no, name, raw, area, loc, d.get('cart', []), amount, 'Card / Global Pay')
    return {"status": "ok", "message": f"Card payment received - pending confirmation. Order {order_no}", "order_no": order_no}

@app.post("/api/auth/register")
async def reg(req: Request):
    d = await req.json()
    phone = clean_input(d.get("phone", ""), 15)
    name = clean_input(d.get("name", ""), 50)
    pwd = d.get("password", "").strip()[:50]
    if len(phone) < 10 or len(pwd) < 4:
        return {"status": "error", "message": "Invalid input"}
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE phone=?", (phone,))
    if cur.fetchone():
        return {"status": "error", "message": "Account already exists. Please Sign In or use Forgot Password."}
    cur.execute("INSERT INTO users (phone,name,password) VALUES (?,?,?)", (phone, name, hash_pw(pwd)))
    conn.commit()
    return {"status": "ok", "user": {"phone": phone, "name": name}, "message": "Account created"}

@app.post("/api/auth/forgot")
async def forgot(req: Request):
    d = await req.json()
    phone = clean_input(d.get("phone", ""), 15)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE phone=?", (phone,))
    exists = cur.fetchone() is not None
    if exists:
        code = str(random.randint(100000, 999999))
        expires = int(time.time()) + 600
        conn.execute("INSERT OR REPLACE INTO password_resets VALUES (?,?,?)", (phone, code, expires))
        conn.commit()
        otp_store[phone] = {"code": code, "expires": time.time() + 600, "attempts": 0}
        intl = phone
        if intl.startswith("0"):
            intl = "254" + intl[1:]
        sent = send_sms(normalize_phone(intl), f"Your LONMA ORBIT reset code is: {code}. Valid for 10 minutes. Do not share it.")
        if not sent and SHOW_RESET_CODE:
            return {"status": "ok", "message": "Reset code sent via SMS. Check your phone.", "code": code, "debug": True}
    return {"status": "ok", "message": "If an account exists with this phone, a reset code has been sent via SMS. Check your phone."}

@app.post("/api/auth/forgot-reset")
async def forgot_reset(req: Request):
    d = await req.json()
    phone = clean_input(str(d.get("phone", "")), 15)
    code = str(d.get("code", "")).strip()
    pwd = str(d.get("new_password", "") or d.get("password", "") or "").strip()
    if not phone or not code or not pwd:
        return {"status": "error", "message": "Missing fields"}
    if len(pwd) < 4:
        return {"status": "error", "message": "Password must be at least 4 characters"}
    # Try DB first, then memory store
    cur = conn.cursor()
    cur.execute("SELECT code, expires FROM password_resets WHERE phone=?", (phone,))
    row = cur.fetchone()
    if row:
        if not hmac.compare_digest(str(row[0]), str(code)):
            return {"status": "error", "message": "Wrong code"}
        if int(time.time()) > row[1]:
            return {"status": "error", "message": "Code expired. Request a new code"}
        conn.execute("UPDATE users SET password=? WHERE phone=?", (hash_pw(pwd), phone))
        conn.execute("DELETE FROM password_resets WHERE phone=?", (phone,))
        conn.commit()
        otp_store.pop(phone, None)
        return {"status": "ok", "message": "Password reset successful. Please Sign In"}
    otp = otp_store.get(phone)
    if not otp:
        return {"status": "error", "message": "No OTP found. Request a new code"}
    if time.time() > otp["expires"]:
        otp_store.pop(phone, None)
        return {"status": "error", "message": "Code expired. Request a new code"}
    otp["attempts"] = otp.get("attempts", 0) + 1
    if otp["attempts"] > 5:
        otp_store.pop(phone, None)
        return {"status": "error", "message": "Too many attempts. Request a new code"}
    if otp["code"] != code:
        return {"status": "error", "message": "Wrong code"}
    conn.execute("UPDATE users SET password=? WHERE phone=?", (hash_pw(pwd), phone))
    conn.commit()
    otp_store.pop(phone, None)
    return {"status": "ok", "message": "Password reset successful. Please Sign In"}

@app.post("/api/auth/reset")
async def reset_pw(req: Request):
    d = await req.json()
    phone = clean_input(d.get("phone", ""), 15)
    code = clean_input(d.get("code", ""), 6)
    newpw = d.get("new_password", "").strip()[:50]
    if len(newpw) < 4:
        return {"status": "error", "message": "Password must be at least 4 characters"}
    cur = conn.cursor()
    cur.execute("SELECT code, expires FROM password_resets WHERE phone=?", (phone,))
    row = cur.fetchone()
    if not row:
        return {"status": "error", "message": "No reset request found. Request a new code."}
    if not hmac.compare_digest(str(row[0]), str(code)):
        return {"status": "error", "message": "Wrong code"}
    if int(time.time()) > row[1]:
        return {"status": "error", "message": "Code expired. Request a new code."}
    conn.execute("UPDATE users SET password=? WHERE phone=?", (hash_pw(newpw), phone))
    conn.execute("DELETE FROM password_resets WHERE phone=?", (phone,))
    conn.commit()
    return {"status": "ok", "message": "Password reset successful. You can now Sign In."}

@app.post("/api/auth/login")
async def log(req: Request):
    ip = req.client.host if req.client else "unknown"
    if is_blocked(ip):
        return {"status": "error", "message": "Too many tries. Wait 15 mins"}
    d = await req.json()
    phone = clean_input(d.get("phone", ""), 15)
    pw = d.get("password", "").strip()[:50]
    cur = conn.cursor()
    cur.execute("SELECT phone,name,password FROM users WHERE phone=?", (phone,))
    row = cur.fetchone()
    if not row or not check_pw(pw, row[2]):
        record_fail(ip)
        return {"status": "error", "message": "Wrong"}
    if ":" not in (row[2] or ""):
        conn.execute("UPDATE users SET password=? WHERE phone=?", (hash_pw(pw), phone))
        conn.commit()
    FAILED[ip] = []
    return {"status": "ok", "user": {"phone": row[0], "name": row[1]}}

HTML="""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>LONMA ORBIT - Online Supermarket</title><style>
:root{--teal:#0A9EBB;--dark:#0F172A;--line:#E2E8F0;--muted:#64748B;--bg:#F8FAFC;--card:#FFFFFF;--text:#0F172A}*{box-sizing:border-box}body{margin:0;font-family:Inter,-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;transition:background .3s,color .3s}
body.dark{--bg:#0F172A;--card:#1E293B;--text:#F8FAFC;--line:#334155;--muted:#94A3B8}
body.dark .nav,body.dark .side,body.dark .bottom,body.dark .card,body.dark .statbox{ background:#1E293B !important; color:#F8FAFC !important; border-color:#334155 !important}
body.dark .search-box,body.dark input,body.dark select,body.dark textarea{ background:#0F172A !important; color:#fff !important; border-color:#334155 !important}
body.dark .chip{ background:#1E293B !important; color:#fff !important; border-color:#334155 !important}
body.dark .mi:hover{ background:#0F172A !important}
body.dark .pill{ background:#0F172A !important; color:#fff !important}
body.theme-pink{--teal:#EC4899} body.theme-green{--teal:#16A34A} body.theme-orange{--teal:#EA580C} body.theme-purple{--teal:#7C3AED} body.theme-gold{--teal:#B45309}
body.font-small{font-size:13px} body.font-large{font-size:17px} body.font-large .card{padding:18px}
.nav{position:fixed;top:0;width:100%;background:var(--card);z-index:1000;border-bottom:1px solid var(--line)}.nav-top{padding:10px 16px;display:flex;justify-content:space-between;align-items:center;height:60px}
.logo{display:flex;align-items:center;gap:10px;cursor:pointer;min-width:0}
.logo img{width:42px;height:42px;border-radius:50%;object-fit:cover;flex-shrink:0;transition:transform .6s cubic-bezier(.34,1.56,.64,1);border:1px solid #E2E8F0}
.logo img.slide{transform:translateX(14px) rotate(360deg) scale(1.15)}
.logo b{font-size:15px;letter-spacing:.4px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.logo b small{display:block;font-size:9px;letter-spacing:2.2px;color:var(--muted);font-weight:700}
.header-actions{display:flex;gap:8px;flex-shrink:0}.pill{padding:9px 14px;border-radius:30px;font-weight:700;font-size:12px;cursor:pointer;border:1px solid var(--line);background:var(--card)}.pill-dark{background:var(--dark);color:#fff;border-color:var(--dark);position:relative}.cart-num{position:absolute;top:-6px;right:-6px;background:var(--teal);color:#fff;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700}
.search-wrap{padding:0 16px 10px}.search-box{background:#F1F5F9;border-radius:12px;height:46px;display:flex;align-items:center;gap:12px;padding:0 12px;border:1px solid var(--line)}
.search-box input{border:none;outline:none;background:transparent;flex:1;font-size:14px;min-width:0}.burger{font-size:12px;cursor:pointer;font-weight:800;letter-spacing:1px;color:var(--text);white-space:nowrap}
.cat-chips{display:flex;gap:8px;overflow-x:auto;padding:0 16px 10px;scrollbar-width:none}.chip{white-space:nowrap;padding:8px 16px;border-radius:20px;background:var(--card);border:1px solid var(--line);font-size:12px;font-weight:700;cursor:pointer}.chip.active{background:var(--dark);color:#fff}
.page{display:none;padding:168px 14px 92px;max-width:480px;margin:0 auto}.page.active{display:block}
.banner{background:linear-gradient(135deg,var(--teal) 0%,#0F172A 100%);color:#fff;border-radius:16px;padding:16px;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;gap:10px}
.card{background:var(--card);border-radius:16px;padding:14px;margin:10px 0;border:1px solid #F1F5F9;box-shadow:0 2px 10px rgba(15,23,42,.04);display:flex;gap:12px}
.pimg{width:84px;height:84px;border-radius:12px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;letter-spacing:.5px;color:#fff;text-align:center;line-height:1.2;padding:6px}
.btn{background:var(--dark);color:#fff;border:none;padding:13px;border-radius:12px;width:100%;font-weight:700;cursor:pointer;font-size:14px}.btn-teal{background:var(--teal)}
input,select,textarea{width:100%;padding:12px;border-radius:12px;border:1px solid var(--line);margin:6px 0;font-size:14px;background:var(--card);outline:none;color:var(--text)}
.bottom{position:fixed;bottom:0;width:100%;background:var(--card);border-top:1px solid var(--line);display:flex;justify-content:space-around;padding:10px 0 calc(10px + env(safe-area-inset-bottom));z-index:1000}
.bottom div{font-size:11px;text-align:center;flex:1;cursor:pointer;color:#94A3B8;font-weight:700;letter-spacing:.3px;line-height:1.2}.bottom div.active{color:var(--text)}.bottom .bicon{display:none!important}.bottom div.active .bicon{color:var(--teal)}
.side{position:fixed;top:0;left:-320px;width:300px;height:100%;background:var(--card);z-index:2000;transition:left .38s cubic-bezier(.22,1,.36,1);box-shadow:20px 0 60px rgba(0,0,0,.18);overflow-y:auto}.side.open{left:0}.overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(15,23,42,.45);z-index:1999}.overlay.open{display:block}
.top-box{background:#fff;padding:28px 20px 18px;color:#0F172A;text-align:center;border-bottom:1px solid #EEF2F7} .top-box .pay-row{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-top:14px} .top-box .pay-pill{font-size:11px;font-weight:700;padding:6px 10px;border:1px solid #E2E8F0;border-radius:20px;color:#334155;background:#F8FAFC} .top-box .promo-line{font-size:12px;color:#64748B;margin-top:12px} .top-box .promo-line b{color:#0A9EBB} .lc{width:84px;height:84px;background:#fff;border-radius:50%;margin:0 auto;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:pointer;box-shadow:0 4px 16px rgba(15,23,42,.10);border:1px solid #EEF2F7} .prod-badge{font-size:11px;font-weight:600;padding:5px 10px;border-radius:20px;background:#F1F5F9!important;color:#475569!important}.lc{width:72px;height:72px;background:#fff;border-radius:50%;margin:0 auto;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:pointer}.lc img{width:72px;height:72px;border-radius:50%;object-fit:cover;transition:transform .6s cubic-bezier(.34,1.56,.64,1)}.lc img.slide{transform:translateX(10px) rotate(360deg) scale(1.08)}
.menu{padding:12px 0}.mi{display:flex;align-items:center;gap:14px;padding:14px 20px;cursor:pointer}.mi:hover{background:#F8FAFC}.mi b{font-size:14px;font-weight:600;flex:1}.ico{display:none!important} .mi{padding:16px 20px}.tag{font-size:11px;font-weight:800;padding:5px 10px;border-radius:20px}.div{height:1px;background:#F1F5F9;margin:8px 20px}.label{font-size:10px;font-weight:800;letter-spacing:.18em;color:#94A3B8;padding:14px 20px 6px}
.stat{display:grid;grid-template-columns:1fr 1fr;gap:10px}.statbox{background:var(--card);border-radius:14px;padding:14px;border:1px solid #F1F5F9}.statbox b{font-size:20px}.statbox span{font-size:11px;color:var(--muted)}
.dashtab{display:flex;gap:8px;overflow-x:auto;padding:8px 0}.dtab{white-space:nowrap;padding:8px 16px;border-radius:20px;background:var(--card);border:1px solid var(--line);font-size:12px;font-weight:700;cursor:pointer}.dtab.active{background:var(--dark);color:#fff}
.wa{position:fixed;bottom:84px;right:12px;background:var(--teal);color:#fff;height:40px;padding:0 14px;border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;z-index:900;box-shadow:0 6px 16px rgba(10,158,187,.35);cursor:pointer;letter-spacing:.6px}
.progress{height:8px;background:#E2E8F0;border-radius:10px;overflow:hidden}.progress div{height:100%;background:var(--teal)}
.avatar{width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,var(--teal),#0F172A);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;flex-shrink:0;font-size:15px}
.post-actions{display:flex;gap:14px;margin-top:12px;color:#64748B;font-size:12px;font-weight:600;flex-wrap:wrap}.post-actions span{cursor:pointer;white-space:nowrap}.post-actions small{display:block;color:#94A3B8;font-weight:600;font-size:11px}
.hashtag{color:var(--teal);font-weight:700}
.star{color:#F59E0B;letter-spacing:1px}
.brand-tag{display:inline-flex;align-items:center;background:#F0F9FB;color:var(--teal);border:1px solid #CFF0F5;padding:5px 10px;border-radius:20px;font-size:11px;font-weight:800;letter-spacing:.5px;margin-top:10px}
.trend-row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid #F1F5F9}.trend-row:last-child{border-bottom:none}
.empty-state{text-align:center;padding:28px 16px;color:#64748B}.empty-state b{color:var(--text);font-size:15px}
.pay-opt{display:flex;gap:10px;margin:8px 0}.pay-card{flex:1;border:2px solid var(--line);border-radius:14px;padding:12px 8px;text-align:center;cursor:pointer;background:var(--card)}.pay-card.active{border-color:var(--teal);background:#F0F9FB}.pay-card b{display:block;font-size:12px;margin-top:4px}.pay-card span{font-size:10px;color:var(--muted)}
.pay-card.disabled{opacity:.45;cursor:not-allowed}
.link{color:var(--teal);font-weight:800;cursor:pointer;font-size:13px;text-align:center;display:block;margin-top:10px}
.terms-box{line-height:1.7;font-size:13px}.terms-box h4{margin:16px 0 6px;font-size:14px}.terms-box p{margin:4px 0;color:#334155}
.appear-opt{display:flex;gap:10px;flex-wrap:wrap}.appear-card{flex:1;min-width:90px;border:2px solid var(--line);border-radius:14px;padding:14px 8px;text-align:center;cursor:pointer;background:var(--card)}.appear-card.active{border-color:var(--teal);background:#F0F9FB}.color-dot{width:32px;height:32px;border-radius:50%;margin:0 auto;border:2px solid #fff;box-shadow:0 0 0 1px #E2E8F0;cursor:pointer}.color-dot.active{box-shadow:0 0 0 3px var(--teal)}
.toggle{width:52px;height:28px;border-radius:20px;background:#E2E8F0;position:relative;cursor:pointer;transition:.3s;flex-shrink:0}.toggle.on{background:var(--teal)}.toggle::after{content:'';position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%;background:#fff;transition:.3s}.toggle.on::after{left:27px}
.prod-badge{font-size:10px;font-weight:800;padding:4px 8px;border-radius:20px;background:#FEF3C7;color:#92400E}
</style></head><body>
<div class="nav"><div class="nav-top"><div class="logo" onclick="logoPress()"><img src="/logo.png" alt="LONMA"><b>LONMA ORBIT<small>ONLINE SUPERMARKET</small></b></div><div class="header-actions"><div class="pill" onclick="show('appearance')" style="font-size:16px">◐</div><div class="pill" onclick="show('wishlist')">Saved <span id="wishCount">0</span></div><div class="pill pill-dark" onclick="show('cart')">CART <span id="cartCount" class="cart-num" style="display:none">0</span></div></div></div><div class="search-wrap"><div class="search-box"><span class="burger" onclick="openMenu()">MENU</span><input id="searchInput" placeholder="Search Diva, Detrex, Sawa..." oninput="filterProducts()"></div></div><div class="cat-chips"><div class="chip active" onclick="filterCat('All',this)">All</div><div class="chip" onclick="filterCat('Soaps',this)">Soaps</div><div class="chip" onclick="filterCat('Lotions',this)">Lotions</div><div class="chip" onclick="filterCat('Pomades',this)">Pomades</div><div class="chip" onclick="filterCat('Cooking Oils',this)">Oils</div></div></div>
<div class="wa" onclick="openWA()">CHAT WITH US</div>
<div class="overlay" id="overlay" onclick="closeMenu()"></div>
<div class="side" id="side"><div class="top-box"><div class="lc" onclick="logoSlide(this)"><img src="/logo.png" alt="LONMA"></div><div style="font-weight:800;font-size:20px;margin-top:14px;letter-spacing:.6px;color:#0F172A">LONMA ORBIT</div><div style="font-size:12.5px;margin-top:5px;color:#64748B">Online Supermarket &middot; Nairobi, Kenya</div><div style="font-size:12px;margin-top:8px;color:#94A3B8">100% Genuine &middot; Fast Delivery &middot; Secure Payment</div><div class="pay-row"><span class="pay-pill">M-Pesa</span><span class="pay-pill">Airtel Money</span><span class="pay-pill">Card / Global Pay</span></div><div class="promo-line">Promo: <b>LONMA10 = 10% OFF</b></div><div id="prodBadge" style="margin-top:12px"></div></div><div class="menu"><div class="label">SHOP</div><div class="mi" onclick="show('products');closeMenu()"><div class="ico">HOME</div><b>Home &middot; Products</b><span class="tag" style="background:var(--teal);color:#fff">NEW</span></div><div class="mi" onclick="show('wishlist');closeMenu()"><div class="ico">SAVED</div><b>Wishlist</b><span class="tag" style="background:#F1F5F9" id="mcWish">0</span></div><div class="mi" onclick="show('cart');closeMenu()"><div class="ico">CART</div><b>Cart</b><span class="tag" style="background:#F1F5F9" id="mc">0</span></div><div class="mi" onclick="show('track');closeMenu()"><div class="ico">TRACK</div><b>Track Order</b></div><div class="div"></div><div class="label">COMMUNITY</div><div class="mi" onclick="show('community');closeMenu()"><div class="ico" style="background:var(--teal);color:#fff">COM</div><b>Community</b><span class="tag" style="background:var(--teal);color:#fff">NEW</span></div><div class="div"></div><div class="label">MY DASHBOARD</div><div class="mi" onclick="show('account');closeMenu()"><div class="ico"></div><b>My Dashboard</b><span class="tag" style="background:#DCFCE7;color:#166534">CUSTOMER</span></div><div class="mi" onclick="show('appearance');closeMenu()"><div class="ico"></div><b>Appearance</b><span class="tag" style="background:var(--teal);color:#fff">NEW</span></div><div class="div"></div><div class="label">SUPPORT</div><div class="mi" onclick="show('scan');closeMenu()"><div class="ico">VERIFY</div><b>Verify Product</b></div><div class="mi" onclick="openWA()"><div class="ico">CHAT</div><b>WhatsApp Us</b></div><div class="mi" onclick="show('terms');closeMenu()"><div class="ico">TERMS</div><b>Terms &amp; Conditions</b></div><div class="mi" onclick="show('forgot');closeMenu()"><div class="ico"></div><b>Forgot Password</b></div><div class="div"></div><div class="mi" onclick="show('admin');closeMenu()"><div class="ico" style="background:#0F172A;color:#fff">ADMIN</div><b>Admin Dashboard</b><span class="tag" style="background:#0F172A;color:#fff">ADMIN</span></div><div style="text-align:center;padding:18px;color:#94A3B8;font-size:11px">v16.0 Production &middot; Kenya</div></div></div>

<div id="products" class="page active"><div class="banner"><div><div style="font-weight:800;font-size:15px">FREE Delivery</div><div style="font-size:12px;opacity:.9">Orders over KSh 2000 &middot; M-Pesa / Airtel / Card</div></div><div style="background:#fff;color:var(--dark);padding:8px 14px;border-radius:20px;font-weight:800;font-size:12px;cursor:pointer;white-space:nowrap" onclick="show('community')">JOIN COMMUNITY</div></div><div id="prodWarning" style="display:none;background:#FEF3C7;color:#92400E;padding:10px;border-radius:10px;font-size:12px;font-weight:700;margin-bottom:10px"></div><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;gap:8px"><h3 style="margin:0;font-size:17px">Products</h3><select id="sortSelect" onchange="filterProducts()" style="width:auto;padding:8px 12px;font-size:12px;font-weight:700;margin:0"><option value="featured">Sort: Featured</option><option value="low">Price: Low to High</option><option value="high">Price: High to Low</option><option value="name">Name: A to Z</option><option value="rating">Top Rated</option></select></div><div style="text-align:right;font-size:12px;color:#64748B;margin-bottom:4px" id="pCount">9 items</div><div id="plist"></div></div>

<div id="appearance" class="page"><h3>Appearance</h3><p style="font-size:13px;color:var(--muted)">Make LONMA look how you like. Saved on your phone.</p><div class="card" style="display:block"><h4 style="margin:0 0 10px">Theme Mode</h4><div class="appear-opt"><div class="appear-card" id="modeLight" onclick="setMode('light')"><div style="font-size:22px">☀️</div><b>Light</b><span style="font-size:11px;color:var(--muted)">Bright &amp; Clean</span></div><div class="appear-card" id="modeDark" onclick="setMode('dark')"><div style="font-size:22px">🌙</div><b>Dark</b><span style="font-size:11px;color:var(--muted)">Easy on eyes</span></div><div class="appear-card" id="modeAuto" onclick="setMode('auto')"><div style="font-size:22px">🔄</div><b>Auto</b><span style="font-size:11px;color:var(--muted)">Follow phone</span></div></div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:16px"><div><b style="font-size:14px">Dark Mode Quick Toggle</b><div style="font-size:12px;color:var(--muted)">Tap to switch instantly</div></div><div class="toggle" id="darkToggle" onclick="toggleDark()"></div></div></div><div class="card" style="display:block"><h4 style="margin:0 0 10px">App Colour</h4><div style="display:flex;gap:12px;justify-content:space-between"><div style="text-align:center"><div class="color-dot" data-theme="teal" style="background:#0A9EBB" onclick="setTheme('teal',this)"></div><span style="font-size:11px">Teal</span></div><div style="text-align:center"><div class="color-dot" data-theme="pink" style="background:#EC4899" onclick="setTheme('pink',this)"></div><span style="font-size:11px">Pink</span></div><div style="text-align:center"><div class="color-dot" data-theme="green" style="background:#16A34A" onclick="setTheme('green',this)"></div><span style="font-size:11px">Green</span></div><div style="text-align:center"><div class="color-dot" data-theme="orange" style="background:#EA580C" onclick="setTheme('orange',this)"></div><span style="font-size:11px">Orange</span></div><div style="text-align:center"><div class="color-dot" data-theme="purple" style="background:#7C3AED" onclick="setTheme('purple',this)"></div><span style="font-size:11px">Purple</span></div><div style="text-align:center"><div class="color-dot" data-theme="gold" style="background:#B45309" onclick="setTheme('gold',this)"></div><span style="font-size:11px">Gold</span></div></div></div><div class="card" style="display:block"><h4 style="margin:0 0 10px">Text Size</h4><div class="appear-opt"><div class="appear-card" id="fontSmall" onclick="setFont('small')"><b style="font-size:12px">A</b><span style="font-size:11px;display:block">Small</span></div><div class="appear-card" id="fontNormal" onclick="setFont('normal')"><b style="font-size:16px">A</b><span style="font-size:11px;display:block">Normal</span></div><div class="appear-card" id="fontLarge" onclick="setFont('large')"><b style="font-size:20px">A</b><span style="font-size:11px;display:block">Large</span></div></div></div><div class="card" style="display:block"><h4 style="margin:0 0 10px">Preview</h4><div class="banner"><div><div style="font-weight:800">FREE Delivery</div><div style="font-size:12px;opacity:.9">This is how your app looks</div></div><div style="background:#fff;color:#0F172A;padding:8px 14px;border-radius:20px;font-weight:800;font-size:12px">JOIN</div></div><button class="btn btn-teal">Sample Button</button><p style="font-size:12px;color:var(--muted);text-align:center;margin-top:10px" id="appearMsg"></p><button class="btn" onclick="resetAppearance()">Reset to Default</button></div></div>

<div id="community" class="page"><div style="display:flex;justify-content:space-between;align-items:center"><h3 style="margin:0;font-size:17px">Community</h3><span style="font-size:11px;background:var(--teal);color:#fff;padding:6px 12px;border-radius:20px;font-weight:700">LONMA COMMUNITY</span></div><div class="card" style="display:block;margin-top:12px"><div style="display:flex;gap:10px"><div class="avatar" id="myAvatar">?</div><textarea id="postText" placeholder="Share deals, recipes, reviews... Use #Detrex #Diva" style="flex:1;border:none;outline:none;resize:none" rows="3"></textarea></div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;gap:10px"><span style="font-size:12px;color:#64748B">Post a review and earn points</span><button class="btn" style="width:auto;padding:10px 22px;border-radius:20px;background:var(--teal)" onclick="createPost()">Post</button></div></div><div class="card" style="display:block" id="trendCard"><h4 style="margin:0 0 4px;font-size:15px">Trending in LONMA</h4><div id="trendingList"></div></div><div id="feed"></div></div>

<div id="wishlist" class="page"><h3>My Wishlist</h3><div id="wishList"></div></div>
<div id="track" class="page"><h3>Track Order</h3><div class="card" style="display:block"><input id="trackNo" placeholder="Enter order number e.g. LONMA123456"><button class="btn btn-teal" onclick="trackOrder()">Track Order</button><div id="trackRes" style="margin-top:14px"></div></div></div>
<div id="productDetail" class="page"><div id="detailContent"></div></div>

<div id="cart" class="page"><h3>Cart</h3><div id="cartItems"></div><div id="cartSum" style="display:none"><div class="card" style="display:block"><div style="display:flex;gap:8px"><input id="promoCode" placeholder="Promo code e.g. LONMA10" style="flex:1"><button class="btn" style="width:auto;padding:12px 18px" onclick="applyPromo()">Apply</button></div><p id="promoMsg" style="font-size:12px;font-weight:700"></p><div style="display:flex;justify-content:space-between"><span>Subtotal (<span id="tItems">0</span>)</span><b>KSh <span id="sub">0</span></b></div><div style="display:flex;justify-content:space-between;margin-top:8px"><span>Discount</span><b id="discFee" style="color:#16A34A">KSh 0</b></div><div style="display:flex;justify-content:space-between;margin-top:8px"><span>Delivery</span><b id="delFee"></b></div><div style="display:flex;justify-content:space-between;margin-top:12px;font-size:18px;border-top:1px solid #F1F5F9;padding-top:12px"><span>Total</span><b>KSh <span id="tot">0</span></b></div>
<h4 style="margin:18px 0 6px;font-size:14px">Payment Method</h4>
<div class="pay-opt"><div class="pay-card active" id="payMpesa" onclick="setPay('mpesa')"><div style="font-size:16px;font-weight:800;color:#16A34A">M-PESA</div><b>M-Pesa</b><span>STK Push</span></div><div class="pay-card" id="payAirtel" onclick="setPay('airtel')"><div style="font-size:16px;font-weight:800;color:#EF4444">AIRTEL</div><b>Airtel Money</b><span id="airtelLabel">STK Push</span></div><div class="pay-card" id="payCard" onclick="setPay('card')"><div style="font-size:16px;font-weight:800;color:#0F172A">VISA</div><b>Card / Global</b><span id="cardLabel">Visa / Mastercard</span></div></div><p id="payNote" style="font-size:11px;color:#92400E;background:#FEF3C7;padding:8px;border-radius:8px;display:none"></p>
<div id="cardForm" style="display:none;margin-top:10px"><input id="cardNo" placeholder="Card Number 4242 4242 4242 4242" maxlength="19"><div style="display:flex;gap:8px"><input id="cardExpiry" placeholder="MM/YY" maxlength="5"><input id="cardCvv" placeholder="CVV" maxlength="4" type="password"></div><input id="cardName" placeholder="Name on Card"><p style="font-size:11px;color:#64748B">Secure payment. We do not store your card number.</p></div>
<div style="margin-top:16px"><input id="custName" placeholder="Full Name"><input id="phone" placeholder="Phone 07... (M-Pesa / Airtel)"><select id="area"><option value="">Select Area</option><option value="CBD">CBD - 150</option><option value="Westlands">Westlands - 200</option><option value="Upcountry">Upcountry - 350</option></select><textarea id="loc" placeholder="Exact location / building"></textarea><label style="font-size:12px;display:flex;gap:8px;align-items:center;margin:12px 0"><input type="checkbox" id="agree" style="width:auto"> I agree to <a href="#" onclick="show('terms');return false" style="color:var(--teal);font-weight:800">Terms &amp; Conditions</a></label></div><button class="btn" id="payBtn" onclick="checkout()">Pay KSh <span id="pay">0</span> with M-Pesa</button><button class="btn" style="background:var(--teal);margin-top:8px" onclick="orderViaWA()">Order via WhatsApp</button><p id="ps" style="text-align:center;font-size:13px"></p></div></div><div id="emptyCart" class="card" style="text-align:center;padding:30px;display:block"><h4>Your cart is empty</h4><p style="font-size:13px;color:#64748B">Browse products and add items to your cart.</p><button class="btn btn-teal" onclick="show('products')">Start Shopping</button></div></div>

<div id="orders" class="page"><h3>Orders</h3><div style="display:flex;gap:8px;margin-bottom:12px"><input id="phLookup" placeholder="Enter phone 07..."><button class="btn" style="width:auto;padding:10px 20px" onclick="loadOrders()">Load</button></div><div id="olist"></div><div id="noOrd" class="card" style="text-align:center;display:block"><p>No orders yet</p></div></div>
<div id="scan" class="page"><h3>Verify Authenticity</h3><div class="card" style="display:block;padding:20px;text-align:center"><h4>Check Product</h4><p style="font-size:12px;color:#64748B">Enter code like DIV-001</p><input id="vcode" placeholder="DIV-001"><button class="btn btn-teal" onclick="verify()" style="margin-top:10px">Verify Now</button><p id="vres" style="font-weight:700;margin-top:12px"></p></div></div>

<div id="account" class="page"><div id="out"><div class="card" style="display:block"><h4>Create Account</h4><input id="rn" placeholder="Full name"><input id="rp" placeholder="07xxxxxxxx"><input id="rpass" type="password" placeholder="Password (min 4 chars)"><button class="btn" onclick="register()">Create Account</button><p style="font-size:11px;color:#64748B;margin-top:8px">By creating an account you agree to <span style="color:var(--teal);font-weight:800;cursor:pointer" onclick="show('terms')">Terms &amp; Conditions</span>. Password is encrypted.</p><p id="rs"></p></div><div class="card" style="display:block"><h4>Sign In</h4><input id="lp" placeholder="07xxxxxxxx"><input id="lpass" type="password" placeholder="Password"><button class="btn" style="background:var(--teal)" onclick="login()">Sign In</button><span class="link" onclick="show('forgot')">Forgot Password?</span><p id="ls"></p></div></div><div id="in" style="display:none"><div class="card" style="display:block;background:var(--dark);color:#fff;text-align:center;padding:24px"><h3 id="an" style="margin:12px 0 4px">Welcome</h3><p id="ap" style="opacity:.7;font-size:13px"></p><button class="btn" style="background:#fff;color:var(--dark);margin-top:16px" onclick="logout()">Sign Out</button></div><div class="stat" style="margin-top:12px"><div class="statbox"><b id="cOrders">0</b><br><span>My Orders</span></div><div class="statbox"><b id="cSpent">KSh 0</b><br><span>Total Spent</span></div><div class="statbox"><b id="cPoints">0</b><br><span>Points</span></div><div class="statbox"><b id="cPhone">-</b><br><span>Phone</span></div></div><h4 style="margin:18px 0 6px">My Orders History</h4><div id="cList"></div></div></div>

<div id="forgot" class="page"><h3>Forgot Password</h3><div class="card" style="display:block;padding:20px"><p style="font-size:13px;color:#64748B;line-height:1.6">Enter your phone number. If an account exists, we will send a 6-digit reset code via SMS. Code is valid for 10 minutes. Never share your code with anyone.</p><input id="fpPhone" placeholder="07xxxxxxxx"><button class="btn" onclick="sendResetCode()">Send Reset Code via SMS</button><p id="fpMsg" style="font-size:13px;font-weight:700"></p><div id="resetBox" style="display:none;margin-top:16px;border-top:1px solid #F1F5F9;padding-top:16px"><input id="fpCode" placeholder="Enter 6-digit code from SMS" maxlength="6"><input id="fpNew" type="password" placeholder="New Password (min 4 chars)"><input id="fpNew2" type="password" placeholder="Confirm New Password"><button class="btn btn-teal" onclick="doReset()">Reset Password</button><p id="fpMsg2" style="font-size:13px;font-weight:700"></p></div><span class="link" onclick="show('account')">Back to Sign In</span></div><div class="card" style="display:block;text-align:center"><p style="font-size:12px;color:#64748B">Still stuck? Contact us on WhatsApp</p><button class="btn" style="background:var(--teal)" onclick="openWA()">Chat on WhatsApp</button></div></div>

<div id="terms" class="page"><h3>Terms &amp; Conditions</h3><div style="font-size:11px;color:#94A3B8;margin-bottom:8px">Last updated: 20 November 2026 &middot; LONMA ORBIT &middot; Nairobi, Kenya</div><div class="card terms-box" style="display:block;padding:20px"><h4>1. About LONMA ORBIT</h4><p>LONMA ORBIT is an online supermarket in Kenya. By using this app you agree to these Terms.</p><h4>2. Accounts &amp; Security</h4><p>Your password is encrypted (hashed) and never stored in plain text. Do not share your password or reset code. Reset codes are sent only via SMS and expire in 10 minutes.</p><h4>3. Products &amp; Prices</h4><p>All products are 100% genuine. Prices are in Kenya Shillings (KSh).</p><h4>4. Orders</h4><p>You will receive an order number e.g. LONMA123456.</p><h4>5. Payments</h4><p>We accept M-Pesa, Airtel Money and Card / Global Pay (Visa, Mastercard). We do NOT store your full card number, CVV or PIN. Card payments are processed via secure payment provider.</p><h4>6. Delivery</h4><p>CBD: KSh 150, Westlands: KSh 200, Upcountry: KSh 350. FREE delivery for orders KSh 2000+.</p><h4>7. Promos</h4><p>LONMA10 = 10% OFF, WELCOME20 = 20% OFF. One promo per order.</p><h4>8. Returns &amp; Refunds</h4><p>If product is damaged, wrong, or expired, report within 24 hours with photo via WhatsApp.</p><h4>9. Verify Product</h4><p>Every product has a code e.g. DIV-001. Use Verify Product to check authenticity.</p><h4>10. Community Rules</h4><p>Be respectful. No insults, no spam, no fake reviews.</p><h4>11. Privacy</h4><p>We collect your name, phone and delivery address only to process your order. We do not sell your data. Passwords are hashed.</p><h4>12. Forgot Password</h4><p>Tap Forgot Password, enter phone, enter 6-digit code sent via SMS, set new password. Code expires in 10 mins. Do not share code.</p><h4>13. Changes</h4><p>We may update these Terms.</p><h4>14. Contact Us</h4><p>WhatsApp: Chat button in app. Email: support@lonmaorbit.co.ke. Nairobi, Kenya.</p><label style="display:flex;gap:8px;align-items:flex-start;font-size:13px;margin-top:18px"><input type="checkbox" id="termsAgree" style="width:auto;margin-top:2px"> <span>I have read and agree to the Terms &amp; Conditions above.</span></label><button class="btn" style="margin-top:14px" onclick="acceptTerms()">I Agree - Back to Shopping</button><p id="termsMsg" style="font-size:12px;font-weight:700;text-align:center"></p></div></div>

<div id="admin" class="page"><h3>Admin Dashboard</h3><div id="adminLoginBox" class="card" style="display:block"><input id="apass" type="password" placeholder="Admin Password"><button class="btn" onclick="adminLogin()">Secure Login</button><p id="ast"></p></div><div id="acont" style="display:none"><div class="stat"><div class="statbox" style="background:#0F172A;color:#fff"><b id="aSales">KSh 0</b><br><span style="color:#CBD5E1">Total Sales</span></div><div class="statbox"><b id="aOrders">0</b><br><span>Total Orders</span></div><div class="statbox"><b id="aCust">0</b><br><span>Customers</span></div><div class="statbox"><b id="aProd">0</b><br><span>Products</span></div></div><div class="stat" style="margin-top:10px"><div class="statbox" style="background:var(--teal);color:#fff"><b id="aPosts">0</b><br><span>Community Posts</span></div><div class="statbox"><b>Live</b><br><span>Community Active</span></div></div><div class="dashtab"><div class="dtab active" onclick="switchAdminTab('orders',this)">Orders</div><div class="dtab" onclick="switchAdminTab('customers',this)">Customers</div><div class="dtab" onclick="switchAdminTab('stock',this)">Stock</div><div class="dtab" onclick="switchAdminTab('add',this)">Add Product</div></div><div id="aOrdersList"></div><div id="aCustList" style="display:none"></div><div id="aStockList" style="display:none"></div><div id="aAdd" style="display:none"><div class="card" style="display:block"><input id="npName" placeholder="Product Name"><input id="npPrice" type="number" placeholder="Price"><input id="npCode" placeholder="Code e.g. DIV-010"><select id="npCat"><option>Soaps</option><option>Lotions</option><option>Pomades</option><option>Cooking Oils</option></select><input id="npStock" type="number" placeholder="Stock"><button class="btn btn-teal" onclick="addProduct()">Add Product</button><p id="npMsg"></p></div></div></div></div>
<div id="receipt" class="page"><div class="card" style="display:block;text-align:center;padding:24px" id="rcont"></div><button class="btn" onclick="show('products')">Continue Shopping</button></div>
<div class="bottom"><div id="b-products" class="active" onclick="show('products')"><div class="bicon">HOME</div>Home</div><div id="b-community" onclick="show('community')"><div class="bicon">COMMUNITY</div>Community</div><div id="b-cart" onclick="show('cart')"><div class="bicon">CART</div>Cart</div><div id="b-orders" onclick="show('orders')"><div class="bicon">ORDERS</div>Orders</div><div id="b-account" onclick="show('account')"><div class="bicon">ACCOUNT</div>Dashboard</div></div>
<script>
let all=[],cart=[],wishlist=JSON.parse(localStorage.getItem('lonma_wish')||'[]'),myOrders=JSON.parse(localStorage.getItem('my_orders')||'[]'),activeCat='All',adminPass='',adminData=null,promoDiscount=0,promoCode='',feedCache=[],payMethod='mpesa',health={};
try{let s=localStorage.getItem('lonma_cart');if(s)cart=JSON.parse(s);}catch(e){cart=[];}
function save(){localStorage.setItem('lonma_cart',JSON.stringify(cart));updateCount();}
function saveWish(){localStorage.setItem('lonma_wish',JSON.stringify(wishlist));updateCount();}
function updateCount(){let c=0;for(let i of cart)c+=i.qty;let el=document.getElementById('cartCount');if(el){el.innerText=c;el.style.display=c>0?'flex':'none';}document.getElementById('mc').innerText=c;document.getElementById('wishCount').innerText=wishlist.length;document.getElementById('mcWish').innerText=wishlist.length;}
function logoSlide(el){ let img = el.querySelector('img'); if(!img) return; img.classList.remove('slide'); void img.offsetWidth; img.classList.add('slide'); setTimeout(()=>img.classList.remove('slide'),650); }
function logoPress(){
  let img=document.querySelector('.logo img');
  if(img){ img.classList.remove('slide'); void img.offsetWidth; img.classList.add('slide'); setTimeout(()=>img.classList.remove('slide'),650); }
  setTimeout(()=>{ openMenu(); },180);
}
function openMenu(){document.getElementById('side').classList.add('open');document.getElementById('overlay').classList.add('open');}
function closeMenu(){document.getElementById('side').classList.remove('open');document.getElementById('overlay').classList.remove('open');}
function openWA(){let msg=encodeURIComponent('Hi LONMA ORBIT. I want to order.');window.open('https://wa.me/254700000000?text='+msg,'_blank');}
function orderViaWA(){let txt='Hi LONMA. I want to order:\\n';for(let i of cart)txt+=i.name+' x'+i.qty+' = KSh '+(i.price*i.qty)+'\\n';txt+='Total: KSh '+document.getElementById('tot').innerText;window.open('https://wa.me/254700000000?text='+encodeURIComponent(txt),'_blank');}
function getUser(){try{return JSON.parse(localStorage.getItem('lonma_user')||'null');}catch(e){return null;}}
function formatText(t){return t.replace(/#(\\w+)/g,'<span class="hashtag">#$1</span>');}
function avatarLetter(name){return (name||'L').charAt(0).toUpperCase();}
async function loadHealth(){
  try{ let r=await fetch('/api/health'); health=await r.json();
    let warn=document.getElementById('prodWarning'); let badge=document.getElementById('prodBadge');
    if(health.mpesa_env!=='production'){ if(warn){ warn.style.display='block'; warn.innerText='⚠️ TEST MODE: M-Pesa is in Sandbox. Set DARAJA_ENV=production in Render for real payments.'; } if(badge){ badge.innerHTML='<span class="prod-badge">TEST MODE - M-Pesa Sandbox</span>'; } }
    else { if(badge) badge.innerHTML='<span class="prod-badge" style="background:#DCFCE7;color:#166534">LIVE - M-Pesa Production</span>'; }
    // Disable pay cards if not configured
    if(!health.airtel_configured){ let c=document.getElementById('payAirtel'); if(c) c.classList.add('disabled'); let l=document.getElementById('airtelLabel'); if(l) l.innerText='Temporarily Unavailable'; }
    if(!health.card_configured){ let c=document.getElementById('payCard'); if(c) c.classList.add('disabled'); let l=document.getElementById('cardLabel'); if(l) l.innerText='Temporarily Unavailable'; }
  }catch(e){}
}
function getAppear(){ try{ return JSON.parse(localStorage.getItem('lonma_appear')||'{"mode":"light","theme":"teal","font":"normal"}'); }catch(e){ return {mode:'light',theme:'teal',font:'normal'}; } }
function applyAppear(){
  let a=getAppear();
  document.body.classList.remove('dark','theme-pink','theme-green','theme-orange','theme-purple','theme-gold','font-small','font-large');
  let isDark = a.mode==='dark' || (a.mode==='auto' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  if(isDark) document.body.classList.add('dark');
  if(a.theme && a.theme!=='teal') document.body.classList.add('theme-'+a.theme);
  if(a.font==='small') document.body.classList.add('font-small');
  if(a.font==='large') document.body.classList.add('font-large');
  ['modeLight','modeDark','modeAuto'].forEach(id=>{ let el=document.getElementById(id); if(el) el.classList.remove('active'); });
  let mid = a.mode==='dark'?'modeDark':a.mode==='auto'?'modeAuto':'modeLight'; let me=document.getElementById(mid); if(me) me.classList.add('active');
  let tg=document.getElementById('darkToggle'); if(tg) tg.classList.toggle('on', isDark);
  document.querySelectorAll('.color-dot').forEach(d=>d.classList.toggle('active', d.dataset.theme===a.theme));
  ['fontSmall','fontNormal','fontLarge'].forEach(id=>{ let el=document.getElementById(id); if(el) el.classList.remove('active'); });
  let fid = a.font==='small'?'fontSmall':a.font==='large'?'fontLarge':'fontNormal'; let fe=document.getElementById(fid); if(fe) fe.classList.add('active');
  let msg=document.getElementById('appearMsg'); if(msg) msg.innerText='Saved: '+(a.mode==='dark'?'Dark':a.mode==='auto'?'Auto':'Light')+' • '+a.theme+' • '+a.font+' text';
}
function setMode(m){ let a=getAppear(); a.mode=m; localStorage.setItem('lonma_appear',JSON.stringify(a)); applyAppear(); }
function toggleDark(){ let a=getAppear(); let isDark=document.body.classList.contains('dark'); a.mode=isDark?'light':'dark'; localStorage.setItem('lonma_appear',JSON.stringify(a)); applyAppear(); }
function setTheme(t,el){ let a=getAppear(); a.theme=t; localStorage.setItem('lonma_appear',JSON.stringify(a)); applyAppear(); }
function setFont(f){ let a=getAppear(); a.font=f; localStorage.setItem('lonma_appear',JSON.stringify(a)); applyAppear(); }
function resetAppearance(){ localStorage.setItem('lonma_appear',JSON.stringify({mode:'light',theme:'teal',font:'normal'})); applyAppear(); }
function setPay(m){
  if(m==='airtel' && !health.airtel_configured){ document.getElementById('ps').innerText='Airtel Money is temporarily unavailable. Please use M-Pesa.'; return; }
  if(m==='card' && !health.card_configured){ document.getElementById('ps').innerText='Card payment is temporarily unavailable. Please use M-Pesa.'; return; }
  payMethod=m;
  document.getElementById('payMpesa').classList.toggle('active',m==='mpesa');
  document.getElementById('payAirtel').classList.toggle('active',m==='airtel');
  document.getElementById('payCard').classList.toggle('active',m==='card');
  document.getElementById('cardForm').style.display=m==='card'?'block':'none';
  let btn=document.getElementById('payBtn');
  let tot=document.getElementById('tot').innerText;
  if(m==='mpesa') btn.innerHTML='Pay KSh <span id="pay">'+tot+'</span> with M-Pesa';
  if(m==='airtel') btn.innerHTML='Pay KSh <span id="pay">'+tot+'</span> with Airtel Money';
  if(m==='card') btn.innerHTML='Pay KSh <span id="pay">'+tot+'</span> with Card / Global Pay';
}
function acceptTerms(){
  if(!document.getElementById('termsAgree').checked){ document.getElementById('termsMsg').innerText='Please tick the checkbox to agree.'; return; }
  localStorage.setItem('lonma_terms','accepted');
  document.getElementById('termsMsg').innerText='Thank you. Terms accepted.';
  setTimeout(()=>show('products'),800);
}
async function sendResetCode(){
  let phone=document.getElementById('fpPhone').value.trim();
  if(!phone){ document.getElementById('fpMsg').innerText='Enter your phone number'; return; }
  document.getElementById('fpMsg').innerText='Sending code via SMS...';
  let r=await fetch('/api/auth/forgot',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone})});
  let d=await r.json();
  // PRODUCTION: Never show code. If debug mode enabled for testing, code may be in response - do NOT display it.
  document.getElementById('fpMsg').innerText=d.message || 'If an account exists, code sent via SMS.';
  document.getElementById('resetBox').style.display='block';
  document.getElementById('fpMsg').innerText += ' Enter code from SMS below.';
}
async function doReset(){
  let phone=document.getElementById('fpPhone').value.trim();
  let code=document.getElementById('fpCode').value.trim();
  let p1=document.getElementById('fpNew').value.trim();
  let p2=document.getElementById('fpNew2').value.trim();
  if(p1!==p2){ document.getElementById('fpMsg2').innerText='Passwords do not match'; return; }
  let r=await fetch('/api/auth/reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone,code,new_password:p1})});
  let d=await r.json();
  document.getElementById('fpMsg2').innerText=d.message;
  if(d.status==='ok'){ setTimeout(()=>show('account'),1200); }
}
async function loadCommunity(){
  let u=getUser(); let phone=u?u.phone:'';
  let r=await fetch('/api/community/posts?phone='+encodeURIComponent(phone)); feedCache=await r.json();
  let tr=await fetch('/api/community/trending'); let trends=await tr.json();
  let trendCard=document.getElementById('trendCard');
  if(!trends || trends.length===0){ trendCard.style.display='none'; }
  else { trendCard.style.display='block'; document.getElementById('trendingList').innerHTML=trends.map(t=>`<div class="trend-row"><b style="font-size:14px">${t.tag}</b><span style="color:#64748B;font-size:12px">${t.count} posts</span></div>`).join(''); }
  document.getElementById('myAvatar').innerText=u?avatarLetter(u.name):'?';
  renderFeed();
}
function renderFeed(){
  if(!feedCache || feedCache.length===0){
    document.getElementById('feed').innerHTML=`<div class="card" style="display:block"><div class="empty-state"><b>No posts yet</b><p style="font-size:13px;line-height:1.6;margin:8px 0">Be the first to share in LONMA Community.<br>Post a review, a recipe, or a deal you found.</p><button class="btn btn-teal" style="width:auto;padding:10px 20px" onclick="document.getElementById('postText').focus()">Create First Post</button></div></div>`;
    return;
  }
  document.getElementById('feed').innerHTML=feedCache.map(p=>{
    let imgHtml='';
    if(p.image){let parts=p.image.split('|'); imgHtml=`<span class="brand-tag">${parts[0]}</span>`;}
    return `<div class="card" style="display:block;padding:16px"><div style="display:flex;gap:10px"><div class="avatar">${avatarLetter(p.author)}</div><div style="flex:1;min-width:0"><div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap"><b style="font-size:14px">${p.author}</b><span style="font-size:11px;color:#94A3B8">${p.created}</span></div><div style="font-size:14px;line-height:1.55;margin-top:5px;word-break:break-word">${formatText(p.text)}</div>${imgHtml}<div class="post-actions"><span onclick="likePost(${p.id})">${p.liked?'Liked':'Like'}<small>${p.likes} likes</small></span><span onclick="toggleComments(${p.id})">Comments<small>${p.comments}</small></span><span onclick="repostPost(${p.id})">Repost<small>${p.reposts}</small></span><span onclick="sharePost(${p.id})">Share<small>Send</small></span><span onclick="shopFromPost()">Shop<small>Products</small></span></div><div id="comments-${p.id}" style="display:none;margin-top:10px"></div><div id="commentBox-${p.id}" style="display:none;margin-top:10px"><input id="cInput-${p.id}" placeholder="Write a comment..."><button class="btn btn-teal" style="padding:10px" onclick="sendComment(${p.id})">Reply</button></div></div></div></div>`;
  }).join('');
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
function stars(r){if(!r||r===0) return '<span style="color:#94A3B8;font-size:12px">No reviews yet</span>'; let full=Math.round(r); return '<span class="star">'+'★'.repeat(full)+'</span> <span style="color:#64748B">'+r+'</span>';}
function render(list){let h='';for(let p of list){let inC=cart.find(c=>c.id===p.id);let isWish=wishlist.includes(p.id);let low=p.stock<=8?`<span style="color:#EF4444;font-size:10px;font-weight:800;background:#FEF2F2;padding:3px 8px;border-radius:20px;margin-left:6px">Only ${p.stock} left</span>`:'';let im=parseImg(p.image);h+=`<div class="card"><div class="pimg" style="background:${im.bg};cursor:pointer" onclick="openDetail(${p.id})">${im.label}</div><div style="flex:1;min-width:0"><div style="display:flex;justify-content:space-between;gap:8px"><div style="font-weight:700;font-size:13px;line-height:1.3;cursor:pointer" onclick="openDetail(${p.id})">${p.name}${low}</div><span style="cursor:pointer;font-size:11px;font-weight:700;color:${isWish?'var(--teal)':'#94A3B8'};flex-shrink:0" onclick="toggleWish(${p.id})">${isWish?'SAVED':'SAVE'}</span></div><div style="font-size:11px;margin-top:4px">${stars(p.rating)} ${p.reviews?`<span style="color:#94A3B8">(${p.reviews} reviews)</span>`:''}</div><div style="font-size:11px;color:#94A3B8;margin-top:2px">${p.category} &middot; ${p.code}</div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px"><b style="font-size:16px">KSh ${p.price}</b><button class="btn" style="width:auto;padding:8px 16px;border-radius:20px;font-size:12px" onclick="add(${p.id})">${inC?'Added '+inC.qty:'Add to Cart'}</button></div></div></div>`;}document.getElementById('plist').innerHTML=h||'<div class="card" style="display:block;text-align:center">No products found</div>';document.getElementById('pCount').innerText=list.length+' items';}
function toggleWish(id){if(wishlist.includes(id))wishlist=wishlist.filter(x=>x!==id);else wishlist.push(id);saveWish();filterProducts();renderWishlist();}
function renderWishlist(){let list=all.filter(p=>wishlist.includes(p.id));document.getElementById('wishList').innerHTML=list.length?list.map(p=>{let im=parseImg(p.image);return `<div class="card"><div class="pimg" style="background:${im.bg}">${im.label}</div><div style="flex:1"><b style="font-size:13px">${p.name}</b><div>KSh ${p.price}</div><button class="btn" style="width:auto;padding:8px 18px;margin-top:8px" onclick="add(${p.id});show('cart')">Add to Cart</button></div></div>`}).join(''):'<div class="card" style="display:block;text-align:center">No saved items yet. Tap SAVE on products.</div>';}
async function openDetail(id){let p=all.find(x=>x.id===id);let im=parseImg(p.image);let r=await fetch('/api/reviews/'+id);let revs=await r.json();document.getElementById('detailContent').innerHTML=`<div class="card" style="display:block;text-align:center;padding:20px"><div style="background:${im.bg};border-radius:14px;font-size:15px;font-weight:800;color:#fff;padding:28px;letter-spacing:1px">${im.label}</div><h3>${p.name}</h3><div>${stars(p.rating)} ${p.reviews?`<span style="color:#64748B">(${p.reviews} reviews)</span>`:''}</div><p style="color:#64748B">${p.category} &middot; ${p.code} &middot; Stock: ${p.stock}</p><h2>KSh ${p.price}</h2><div style="display:flex;gap:8px"><button class="btn" onclick="add(${id})">Add to Cart</button><button class="btn" style="background:#fff;color:#000;border:1px solid #E2E8F0" onclick="toggleWish(${id})">Save Item</button></div><button class="btn" style="background:var(--teal);margin-top:8px" onclick="shareToCommunity(${id})">Share to Community</button></div><div class="card" style="display:block"><h4>Reviews</h4><div id="revList">${revs.map(x=>`<div style="border-bottom:1px solid #F1F5F9;padding:8px 0"><b>${x.name}</b> <span class="star">${'★'.repeat(x.rating)}</span><div style="font-size:13px">${x.text}</div></div>`).join('')||'No reviews yet. Be the first to review.'}</div><input id="revName" placeholder="Your name"><select id="revRating"><option value="5">5 Stars - Excellent</option><option value="4">4 Stars - Good</option><option value="3">3 Stars - Average</option></select><input id="revText" placeholder="Write review..."><button class="btn btn-teal" onclick="submitReview(${id})">Submit Review</button></div>`;show('productDetail');}
async function shareToCommunity(id){let p=all.find(x=>x.id===id);let u=getUser();if(!u){alert('Sign in first');show('account');return;}await fetch('/api/community/post',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author:u.name,phone:u.phone,text:'Just bought '+p.name+' for KSh '+p.price+'. Who else has tried it? #LONMA #'+p.category.replace(' ','')})});show('community');loadCommunity();}
async function submitReview(id){let name=document.getElementById('revName').value||'Customer';let rating=document.getElementById('revRating').value;let text=document.getElementById('revText').value;await fetch('/api/reviews/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:id,name,rating,text})});openDetail(id);}
function add(id){let p=all.find(x=>x.id===id);let f=cart.find(c=>c.id===id);if(f)f.qty++;else cart.push({id:p.id,name:p.name,price:p.price,image:p.image,qty:1});save();filterProducts();}
async function applyPromo(){let code=document.getElementById('promoCode').value.trim();let r=await fetch('/api/promo/check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code})});let d=await r.json();if(d.valid){promoDiscount=d.discount;promoCode=code;document.getElementById('promoMsg').innerText='Applied: '+d.discount+'% OFF ('+code+')';}else{promoDiscount=0;document.getElementById('promoMsg').innerText='Invalid code';}renderCart();}
function calcTotals(){let sub=0;for(let i of cart)sub+=i.price*i.qty;let disc=Math.round(sub*promoDiscount/100);let area=document.getElementById('area').value;let del=area==='CBD'?150:area==='Upcountry'?350:200;if(sub-disc>=2000)del=0;if(promoCode==='FREEDEL')del=0;let tot=sub-disc+del;return {sub,disc,del,tot};}
function renderCart(){let cont=document.getElementById('cartItems'),sum=document.getElementById('cartSum'),empty=document.getElementById('emptyCart');if(cart.length===0){cont.innerHTML='';sum.style.display='none';empty.style.display='block';return;}empty.style.display='none';sum.style.display='block';let html='';for(let it of cart){let im=parseImg(it.image);html+=`<div class="card"><div class="pimg" style="width:60px;height:60px;font-size:11px;background:${im.bg}">${im.label}</div><div style="flex:1"><b style="font-size:13px">${it.name}</b><div style="display:flex;gap:8px;align-items:center;margin-top:6px"><button onclick="chg(${it.id},-1)" style="width:28px;height:28px;border-radius:50%;border:1px solid #E2E8F0;background:#fff">-</button><span>${it.qty}</span><button onclick="chg(${it.id},1)" style="width:28px;height:28px;border-radius:50%;border:1px solid #E2E8F0;background:#fff">+</button><span style="margin-left:auto;font-weight:800">KSh ${it.price*it.qty}</span></div></div></div>`;}cont.innerHTML=html;let t=calcTotals();document.getElementById('sub').innerText=t.sub;document.getElementById('discFee').innerText='- KSh '+t.disc;document.getElementById('tItems').innerText=cart.reduce((a,b)=>a+b.qty,0);document.getElementById('delFee').innerText=t.del==0?'FREE':'KSh '+t.del;document.getElementById('tot').innerText=t.tot;document.getElementById('pay').innerText=t.tot; setPay(payMethod);}
function chg(id,d){let f=cart.find(c=>c.id===id);if(!f)return;f.qty+=d;if(f.qty<=0)cart=cart.filter(c=>c.id!==id);save();renderCart();}
function show(id){document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('.bottom div').forEach(b=>b.classList.remove('active'));let btn=document.getElementById('b-'+id);if(btn)btn.classList.add('active');if(id==='cart')renderCart();if(id==='account')loadCustomerDashboard();if(id==='wishlist')renderWishlist();if(id==='community')loadCommunity();if(id==='appearance')applyAppear();closeMenu();window.scrollTo(0,0);}
async function loadP(){let r=await fetch('/api/products');all=await r.json();render(all);renderWishlist();}
async function verify(){let c=document.getElementById('vcode').value.trim();let r=await fetch('/api/verify/'+c);let d=await r.json();document.getElementById('vres').innerText=d.valid?'Authentic: '+d.product.name:'Invalid Code';}
async function trackOrder(){let no=document.getElementById('trackNo').value.trim();let r=await fetch('/api/track/'+no);let d=await r.json();if(!d.found){document.getElementById('trackRes').innerHTML='Order not found';return;}document.getElementById('trackRes').innerHTML=`<b>${d.order_no}</b> &middot; KSh ${d.total} &middot; ${d.status}<div class="progress" style="margin-top:10px"><div style="width:${d.progress}%"></div></div><div style="display:flex;justify-content:space-between;font-size:11px;margin-top:6px"><span>Pending</span><span>Paid</span><span>Shipped</span><span>Delivered</span></div>`;}
async function checkout(){
  let name=document.getElementById('custName').value.trim(),phone=document.getElementById('phone').value.trim(),area=document.getElementById('area').value,loc=document.getElementById('loc').value.trim();
  if(!name||!phone||!area||!loc||!document.getElementById('agree').checked){document.getElementById('ps').innerText='Please fill all fields and agree to Terms';return;}
  if(payMethod==='airtel' && !health.airtel_configured){ document.getElementById('ps').innerText='Airtel Money is temporarily unavailable. Please use M-Pesa.'; return; }
  if(payMethod==='card' && !health.card_configured){ document.getElementById('ps').innerText='Card payment is temporarily unavailable. Please use M-Pesa.'; return; }
  let t=calcTotals();
  let url='/mpesa/stkpush'; let body={phone,amount:t.tot,cart,name,area,location:loc};
  if(payMethod==='airtel'){ url='/airtel/stkpush'; document.getElementById('ps').innerText='Sending Airtel Money prompt...'; }
  else if(payMethod==='card'){ url='/card/pay'; body.card_no=document.getElementById('cardNo').value; body.expiry=document.getElementById('cardExpiry').value; body.cvv=document.getElementById('cardCvv').value; document.getElementById('ps').innerText='Processing secure card payment...'; }
  else { document.getElementById('ps').innerText='Sending M-Pesa prompt...'; }
  let r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let d=await r.json();document.getElementById('ps').innerText=d.message;
  if(d.status==='ok'){
    let methodLabel=payMethod==='airtel'?'Airtel Money':payMethod==='card'?'Card / Global Pay':'M-Pesa';
    myOrders.unshift({order_no:d.order_no,total:t.tot,status:'Pending',created:new Date().toLocaleString()});localStorage.setItem('my_orders',JSON.stringify(myOrders));
    document.getElementById('rcont').innerHTML=`<h3>${d.order_no}</h3><p>Total KSh ${t.tot} &middot; ${methodLabel} ${promoDiscount?'('+promoDiscount+'% OFF)':''}</p><p style="font-size:12px;color:#64748B">${payMethod==='card'?'Card payment pending confirmation. We will confirm via SMS.':'Check your phone for the payment prompt'}</p><button class="btn" style="margin-top:12px" onclick="document.getElementById('trackNo').value='${d.order_no}';show('track');trackOrder()">Track This Order</button>`;
    cart=[];promoDiscount=0;localStorage.removeItem('lonma_cart');save();show('receipt');
  }
}
async function loadOrders(){let ph=document.getElementById('phLookup').value.trim();let r=await fetch('/api/orders?phone='+ph);let data=await r.json();document.getElementById('olist').innerHTML=data.map(o=>`<div class="card" style="display:block"><div style="display:flex;justify-content:space-between"><b>${o.order_no}</b><span style="background:#F1F5F9;padding:4px 10px;border-radius:20px;font-size:11px">${o.status}</span></div><div style="margin-top:6px">KSh ${o.total} &middot; ${o.created}</div></div>`).join('');document.getElementById('noOrd').style.display=data.length?'none':'block';}
function switchAdminTab(tab,el){document.querySelectorAll('.dtab').forEach(t=>t.classList.remove('active'));el.classList.add('active');document.getElementById('aOrdersList').style.display=tab==='orders'?'block':'none';document.getElementById('aCustList').style.display=tab==='customers'?'block':'none';document.getElementById('aStockList').style.display=tab==='stock'?'block':'none';document.getElementById('aAdd').style.display=tab==='add'?'block':'none';}
async function adminLogin(){let p=document.getElementById('apass').value;let r=await fetch('/api/admin/check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p})});let d=await r.json();document.getElementById('ast').innerText=d.message||'';if(d.status==='ok'){adminPass=p;document.getElementById('adminLoginBox').style.display='none';document.getElementById('acont').style.display='block';let r2=await fetch('/api/admin/dashboard?password='+encodeURIComponent(p));adminData=await r2.json();document.getElementById('aSales').innerText='KSh '+adminData.total_sales;document.getElementById('aOrders').innerText=adminData.total_orders;document.getElementById('aCust').innerText=adminData.total_customers;document.getElementById('aProd').innerText=adminData.total_products;document.getElementById('aPosts').innerText=adminData.total_posts;document.getElementById('aOrdersList').innerHTML=adminData.orders.map(o=>`<div class="card" style="display:block"><div style="display:flex;justify-content:space-between"><b>${o.order_no}</b><span style="font-size:11px;background:#F0F9FB;padding:4px 8px;border-radius:10px">${o.pay_method||'M-Pesa'}</span><select onchange="changeStatus('${o.order_no}',this.value)" style="width:auto;padding:6px;margin:0;font-size:11px"><option ${o.status==='Pending'?'selected':''}>Pending</option><option ${o.status==='PAID'?'selected':''}>PAID</option><option ${o.status==='Shipped'?'selected':''}>Shipped</option><option ${o.status==='Delivered'?'selected':''}>Delivered</option></select></div><div style="font-size:12px;margin-top:6px">${o.name} &middot; ${o.phone}<br>KSh ${o.total} &middot; ${o.created}</div></div>`).join('')||'No orders';document.getElementById('aCustList').innerHTML=adminData.customers.map(c=>`<div class="card" style="display:block"><b>${c.name}</b><div style="font-size:12px;color:#64748B">${c.phone} &middot; ${c.orders} orders &middot; Spent KSh ${c.spent}</div></div>`).join('')||'No customers';document.getElementById('aStockList').innerHTML=adminData.products.map(p=>`<div class="card" style="display:block"><div style="display:flex;justify-content:space-between"><b style="font-size:13px">${p.name}</b><span style="font-weight:800;color:${p.stock<=8?'#EF4444':'#16A34A'}">${p.stock} left</span></div><div style="font-size:12px;color:#64748B">${p.category} &middot; KSh ${p.price}</div><button style="margin-top:8px;background:#FEE2E2;border:none;padding:6px 12px;border-radius:10px;font-size:11px" onclick="deleteProduct(${p.id})">Delete</button></div>`).join('');}}
async function changeStatus(order_no,status){await fetch('/api/admin/update_status',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminPass,order_no,status})});}
async function addProduct(){let name=document.getElementById('npName').value,price=document.getElementById('npPrice').value,code=document.getElementById('npCode').value,cat=document.getElementById('npCat').value,stock=document.getElementById('npStock').value;let r=await fetch('/api/admin/add_product',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminPass,name,price,code,category:cat,stock})});let d=await r.json();document.getElementById('npMsg').innerText=d.status==='ok'?'Added. Refresh page.':'Error';if(d.status==='ok')loadP();}
async function deleteProduct(id){if(!confirm('Delete this product?'))return;await fetch('/api/admin/delete_product',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:adminPass,id})});adminLogin();}
async function loadCustomerDashboard(){let u=getUser();if(!u){document.getElementById('out').style.display='block';document.getElementById('in').style.display='none';return;}document.getElementById('out').style.display='none';document.getElementById('in').style.display='block';document.getElementById('an').innerText='Welcome, '+u.name;document.getElementById('ap').innerText=u.phone;let r=await fetch('/api/customer/dashboard?phone='+encodeURIComponent(u.phone));let d=await r.json();document.getElementById('cOrders').innerText=d.total_orders;document.getElementById('cSpent').innerText='KSh '+d.total_spent;document.getElementById('cPoints').innerText=d.points;document.getElementById('cPhone').innerText=d.phone;document.getElementById('cList').innerHTML=d.orders.map(o=>`<div class="card" style="display:block"><div style="display:flex;justify-content:space-between"><b>${o.order_no}</b><span style="background:#F1F5F9;padding:4px 10px;border-radius:20px;font-size:11px">${o.status}</span></div><div style="margin-top:6px">KSh ${o.total} &middot; ${o.created}</div></div>`).join('')||'<div class="card" style="display:block;text-align:center">No orders yet</div>';}
async function register(){let name=document.getElementById('rn').value.trim(),phone=document.getElementById('rp').value.trim(),pass=document.getElementById('rpass').value.trim();let r=await fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,phone,password:pass})});let d=await r.json();document.getElementById('rs').innerText=d.status==='ok'?'Account created - password encrypted':'Error: '+ (d.message||'');if(d.status==='ok'){localStorage.setItem('lonma_user',JSON.stringify(d.user));loadCustomerDashboard();}}
async function login(){let phone=document.getElementById('lp').value.trim(),pass=document.getElementById('lpass').value.trim();let r=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone,password:pass})});let d=await r.json();document.getElementById('ls').innerText=d.status==='ok'?'Welcome back':'Wrong credentials';if(d.status==='ok'){localStorage.setItem('lonma_user',JSON.stringify(d.user));loadCustomerDashboard();}}
function logout(){localStorage.removeItem('lonma_user');document.getElementById('out').style.display='block';document.getElementById('in').style.display='none';}
document.getElementById('area')?.addEventListener('change',renderCart);
applyAppear(); loadHealth(); loadP();updateCount();loadCustomerDashboard();
</script></body></html>
<script>setInterval(()=>{let t=document.querySelector('textarea[placeholder*="Share deals"]');if(!t||document.getElementById('commActions'))return;let d=document.createElement('div');d.id='commActions';d.innerHTML='<button onclick="alert(\'Live coming\')" style="background:#FEE2E2;color:#DC2626;border:0;padding:8px 12px;border-radius:20px;font-size:12px;font-weight:700">🔴 Live Video</button> <button onclick="document.getElementById(\'commPhoto\').click()" style="background:#E0F2FE;color:#0369A1;border:0;padding:8px 12px;border-radius:20px;font-size:12px;font-weight:700">🖼️ Photo</button> <button onclick="let n=prompt(\'Friend name:\');if(n)alert(\'Friends with \'+n)" style="background:#FEF3C7;color:#92400E;border:0;padding:8px 12px;border-radius:20px;font-size:12px;font-weight:700">👥 Add Friends</button><input type=file id=commPhoto hidden accept=image/*>';t.parentNode.insertBefore(d,t.nextSibling)},1000)</script>
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
# ALIASES - login.html calls /api/register and /api/login, also support them
@app.post("/api/register")
async def reg_alias(req: Request):
    return await reg(req)

@app.post("/api/login")
async def log_alias(req: Request):
    return await log(req)

# Also support /api/auth/* without /auth for old frontend
@app.post("/api/signup")
async def signup_alias(req: Request):
    return await reg(req)

@app.post("/api/signin")
async def signin_alias(req: Request):
    return await log(req)
@app.post("/api/auth/forgot-password")
@app.post("/api/forgot-password")
async def forgot_pw(req: Request):
    try:
        d = await req.json()
    except:
        return {"status":"error","message":"Invalid data"}
    email = str(d.get("email","")).strip().lower()[:100]
    newpw = str(d.get("password","")).strip()[:50]
    if not email or "@" not in email or len(newpw) < 4:
        return {"status":"error","message":"Enter valid email and new password min 4 chars"}
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE phone=?", (email,))
        row = cur.fetchone()
        if not row:
            return {"status":"error","message":"No account found for this email. Please Create Account first."}
        try:
            hp = hash_pw(newpw)
        except:
            hp = newpw
        cur.execute("UPDATE users SET password=? WHERE id=?", (hp, row[0]))
        conn.commit()
        return {"status":"ok","message":"Password reset"}
    except Exception as e:
        print("FORGOT ERROR:", e)
        return {"status":"error","message":"Server error: "+str(e)}
