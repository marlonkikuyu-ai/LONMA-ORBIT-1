<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lonma Orbit - Delivery Platform</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<style>
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;background:#f8f8fa;color:#111}
header{max-width:1200px;margin:0 auto;padding:18px 20px;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:900;letter-spacing:-0.5px;font-size:20px}
nav a{color:#111;text-decoration:none;margin-left:16px;font-size:14px;font-weight:600}
.wrap{max-width:1200px;margin:0 auto;padding:20px;display:grid;grid-template-columns:1.1fr 0.9fr;gap:30px;align-items:center}
@media(max-width:800px){.wrap{grid-template-columns:1fr}}
.h1{font-size:52px;line-height:0.95;font-weight:900;letter-spacing:-2px;margin:0}
.sub{color:#666;margin-top:18px;font-size:17px;line-height:1.5}
.card{background:#fff;border-radius:22px;padding:28px;box-shadow:0 20px 60px rgba(0,0,0,0.08);border:1px solid #eee}
.tabs{display:flex;background:#f1f1f3;padding:4px;border-radius:12px;margin-bottom:18px}
.tabs button{flex:1;padding:10px;border:none;background:transparent;border-radius:10px;font-weight:700;cursor:pointer}
.tabs button.active{background:#111;color:#fff}
label{font-size:12px;font-weight:700;color:#666;margin-top:10px;display:block}
input{width:100%;padding:14px 14px;border:1.5px solid #e6e6e6;border-radius:12px;margin-top:6px;font-size:15px;outline:none}
input:focus{border-color:#111}
.primary{width:100%;margin-top:18px;padding:14px;background:#111;color:#fff;border:none;border-radius:12px;font-weight:700;font-size:15px;cursor:pointer}
.primary:disabled{opacity:0.5}
.muted{margin-top:14px;font-size:13px;color:#666;text-align:center}
.msg{margin-top:14px;padding:12px;border-radius:10px;font-size:13px;display:none}
.msg.ok{display:block;background:#e8f7ee;color:#0a5c26;border:1px solid #c3e8ce}
.msg.err{display:block;background:#fde8e8;color:#8a1a1a;border:1px solid #f5c2c2}
.dash{display:none}
.kpi{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}
.kpi div{background:#f6f6f7;padding:14px;border-radius:12px}
.kpi b{display:block;font-size:20px}
</style>
</head>
<body>
<header>
<div class="logo">LONMA ORBIT</div>
<nav><a href="/docs">API</a><a href="#" onclick="logout()">Logout</a></nav>
</header>

<div class="wrap" id="authView">
<div>
<h1 class="h1">Fast Delivery,<br>Smart Orbit.</h1>
<p class="sub">Kenya's next-gen logistics. Track, send, receive. Your API is live and connected to this client in real-time. No mock data.</p>
<div class="kpi">
<div><b id="apiStatus">● Checking</b><span style="font-size:12px;color:#666">Backend Status</span></div>
<div><b>100%</b><span style="font-size:12px;color:#666">Uptime Ready</span></div>
</div>
</div>

<div class="card">
<div class="tabs">
<button id="tabLogin" class="active" onclick="setMode('login')">Login</button>
<button id="tabReg" onclick="setMode('register')">Register</button>
</div>

<label>Email Address</label>
<input id="email" type="email" autocomplete="email" placeholder="you@lonmaorbit.co.ke">

<label>Password</label>
<input id="password" type="password" autocomplete="current-password" placeholder="••••••••">

<button id="submitBtn" class="primary" onclick="handleAuth()">Continue</button>

<div id="message" class="msg"></div>
<div class="muted">Secured by Lonma Orbit API • app.lonmaorbit.co.ke</div>
</div>
</div>

<div class="wrap dash" id="dashView">
<div>
<h1 class="h1" id="welcomeText">Welcome.</h1>
<p class="sub" id="userEmailText"></p>
<button class="primary" style="max-width:200px" onclick="loadProfile()">Refresh Profile</button>
</div>
<div class="card">
<h3 style="margin:0">Session Active</h3>
<p style="font-size:13px;color:#666">You are authenticated with real JWT from backend.</p>
<pre id="tokenBox" style="background:#f6f6f7;padding:12px;border-radius:10px;font-size:11px;overflow:auto;white-space:pre-wrap;word-break:break-all"></pre>
<button class="primary" onclick="logout()">Logout</button>
</div>
</div>

<script>
let mode = 'login';
const API_BASE = '';

function setMode(m){
 mode = m;
 document.getElementById('tabLogin').className = m==='login'?'active':'';
 document.getElementById('tabReg').className = m==='register'?'active':'';
 document.getElementById('submitBtn').innerText = m==='login'?'Login to Orbit':'Create Account';
}

function showMsg(text, type){
 const el = document.getElementById('message');
 el.innerText = text;
 el.className = 'msg ' + (type==='ok'?'ok':'err');
}

async function checkBackend(){
 try{
  const r = await fetch(API_BASE + '/');
  if(r.ok){ document.getElementById('apiStatus').innerText='● ONLINE'; document.getElementById('apiStatus').style.color='#0a5c26'; }
  else throw new Error();
 } catch { document.getElementById('apiStatus').innerText='● OFFLINE'; document.getElementById('apiStatus').style.color='#8a1a1a'; }
}

function getToken(){ return localStorage.getItem('lonma_token'); }

function isLoggedIn(){
 const token = getToken();
 if(!token) return false;
 document.getElementById('authView').style.display='none';
 document.getElementById('dashView').style.display='grid';
 document.getElementById('tokenBox').innerText = token;
 return true;
}

async function handleAuth(){
 const email = document.getElementById('email').value.trim();
 const password = document.getElementById('password').value;
 const btn = document.getElementById('submitBtn');
 if(!email || !password){ showMsg('Email and password required','err'); return; }
 btn.disabled=true; btn.innerText='Processing...';
 try{
  const endpoint = mode==='login'?'/auth/login':'/auth/register';
  const res = await fetch(API_BASE + endpoint, {
   method:'POST',
   headers:{'Content-Type':'application/json'},
   body: JSON.stringify({email,password})
  });
  const data = await res.json();
  if(!res.ok){ throw new Error(data.detail || data.message || JSON.stringify(data)); }
  const token = data.access_token || data.token || data.jwt;
  if(mode==='login'){
   if(!token) throw new Error('No token returned from backend - check auth route returns access_token');
   localStorage.setItem('lonma_token', token);
   localStorage.setItem('lonma_user', JSON.stringify(data.user || {email}));
   showMsg('Authenticated successfully','ok');
   setTimeout(()=>{ location.reload(); }, 600);
  } else {
   showMsg('Account created! Please login now.','ok');
   setMode('login');
  }
 } catch(e){ showMsg(e.message,'err'); }
 finally{ btn.disabled=false; btn.innerText = mode==='login'?'Login to Orbit':'Create Account'; }
}

async function loadProfile(){
 const token = getToken();
 if(!token) return;
 try{
  const r = await fetch(API_BASE + '/user/me', { headers:{'Authorization':'Bearer '+token} });
  const d = await r.json();
  if(r.ok){
   document.getElementById('welcomeText').innerText = 'Welcome, ' + (d.email || d.name || 'Rider') + '.';
   document.getElementById('userEmailText').innerText = d.email || '';
  }
 } catch {}
}

function logout(){
 localStorage.removeItem('lonma_token');
 localStorage.removeItem('lonma_user');
 location.reload();
}

checkBackend();
if(!isLoggedIn()){ setMode('login'); } else { loadProfile(); }
</script>
</body>
</html>
