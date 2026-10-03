from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI(title="LONMA ORBIT")

@app.head("/")
async def head_root():
    return Response(status_code=200)

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LONMA ORBIT | Elite App Studio</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
<style>
:root{--gold:#FFD700;--gold2:#B8860B;--black:#050505;--dark:#0f0f0f;}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--black);color:#fff;font-family:'Inter',sans-serif;overflow-x:hidden}
h1,h2{font-family:'Cinzel',serif}
.gold{color:var(--gold);background:linear-gradient(90deg,var(--gold),var(--gold2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
nav{position:fixed;top:0;width:100%;padding:18px 5%;display:flex;justify-content:space-between;align-items:center;z-index:99;background:rgba(0,0,0,0.8);backdrop-filter:blur(10px);border-bottom:1px solid rgba(255,215,0,0.15)}
.logo{font-family:'Cinzel';letter-spacing:3px;font-weight:600}
.logo span{color:var(--gold)}
.btn{border:1px solid var(--gold);color:var(--gold);padding:10px 22px;text-decoration:none;letter-spacing:2px;font-size:12px;transition:0.3s}
.btn:hover{background:var(--gold);color:#000;box-shadow:0 0 20px rgba(255,215,0,0.5)}
.hero{min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:0 6%;background:radial-gradient(circle at 50% 30%,rgba(255,215,0,0.15),transparent 40%),#000}
.hero h1{font-size:clamp(32px,6vw,72px);line-height:1.1;margin-bottom:18px}
.hero p{color:#aaa;max-width:600px;font-size:18px;font-weight:300;margin-bottom:30px}
.badge{border:1px solid rgba(255,215,0,0.3);padding:6px 14px;font-size:10px;letter-spacing:3px;color:var(--gold);margin-bottom:25px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1px;background:rgba(255,215,0,0.15);margin:0 5%;border:1px solid rgba(255,215,0,0.15)}
.card{background:var(--dark);padding:40px 30px;transition:0.3s}
.card:hover{background:#151515}
.card h3{color:var(--gold);margin:15px 0 10px;letter-spacing:2px;font-size:14px}
.card p{color:#888;font-size:14px;line-height:1.6}
.section{padding:90px 5%}
.footer{text-align:center;padding:40px;color:#555;border-top:1px solid rgba(255,215,0,0.1);font-size:12px;letter-spacing:2px}
.status{margin-top:20px;font-size:11px;letter-spacing:3px;color:var(--gold);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
</style>
</head>
<body>
<nav>
<div class="logo">LONMA <span>ORBIT</span></div>
<a href="#contact" class="btn">INITIATE PROJECT</a>
</nav>

<div class="hero">
<div class="badge">EST. NAIROBI • 2026</div>
<h1><span class="gold">Elite Systems</span><br>For Ambitious Brands</h1>
<p>We architect luxury-grade applications, automation & digital platforms that scale like Rolex. Not templates. Pure engineering.</p>
<a href="#work" class="btn" style="background:var(--gold);color:#000;padding:14px 32px">EXPLORE STUDIO</a>
<div class="status">● SYSTEM LIVE • app.lonmaorbit.co.ke • RENDER OPERATIONAL</div>
</div>

<div class="section" id="work">
<h2 style="text-align:center;margin-bottom:50px;letter-spacing:4px">SERVICES — <span class="gold">ORBIT</span></h2>
<div class="grid">
<div class="card"><div style="font-size:30px">◈</div><h3>BESPOKE APPS</h3><p>FastAPI, React, Mobile. High-performance systems for real businesses, not MVPs.</p></div>
<div class="card"><div style="font-size:30px">⬢</div><h3>AUTOMATION</h3><p>M-Pesa, WhatsApp bots, CRMs, scrapers. We connect Kenya to the world automatically.</p></div>
<div class="card"><div style="font-size:30px">⬣</div><h3>LUXURY UI/UX</h3><p>Black & gold, glass morphism, Rolex-class design that converts elite clients.</p></div>
</div>
</div>

<div class="section" id="contact" style="text-align:center;background:var(--dark)">
<h2>READY TO <span class="gold">ORBIT?</span></h2>
<p style="color:#888;margin:15px auto;max-width:500px">Tell us your idea. We will architect the elite version.</p>
<br>
<a href="https://wa.me/254700000000" class="btn" style="background:var(--gold);color:#000">WHATSAPP MARLONE</a>
<p style="margin-top:25px;color:#444">marlone@lonmaorbit.co.ke | Nairobi, KE</p>
</div>

<div class="footer">LONMA ORBIT © 2026 — ELITE SYSTEMS BY MARLONE — ALL SYSTEMS OPERATIONAL</div>
</body>
</html>
    """

@app.get("/health")
async def health():
    return {"status": "live", "studio": "LONMA ORBIT", "region": "Nairobi", "uptime": "100%"}

@app.get("/api")
async def api_info():
    return {"message": "LONMA ORBIT API v1", "docs": "/docs", "owner": "Marlone"}
