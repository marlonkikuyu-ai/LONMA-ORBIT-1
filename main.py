@app.get("/", response_class=HTMLResponse)
async def home():
    cards="".join([f'<div class="card"><img src="{p["image"]}"><h3>{p["name"]}</h3><p>KSH {p["price"]}</p><button onclick="buy({p["id"]},{p["price"]},\'{p["name"]}\')">Buy Now</button></div>' for p in PRODUCTS])
    return f'''
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA ORBIT</title>
    <style>
    body{{margin:0;font-family:Arial;background:#f5f5f5}}
    header{{background:#0A8EA8;padding:12px;display:flex;justify-content:center;align-items:center;position:sticky;top:0;z-index:10}}
    header img{{height:75px;width:auto;object-fit:contain}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;padding:15px}}
    .card{{background:#fff;border-radius:12px;padding:12px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,0.1)}}
    .card img{{width:100%;border-radius:8px}} .card button{{width:100%;padding:12px;background:#0A8EA8;color:#fff;border:none;border-radius:8px;font-weight:bold}}
    .modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);justify-content:center;align-items:center;z-index:20}}
    .box{{background:#fff;padding:20px;border-radius:12px;width:90%;max-width:360px}}
    input{{width:100%;padding:12px;margin:10px 0;border-radius:8px;border:1px solid #ccc;box-sizing:border-box}}
    </style></head>
    <body>
    <header><img src="/logo.png" alt="LONMA ORBIT"></header>
    <div class="grid">{cards}</div>
    <div id="m" class="modal"><div class="box"><h3 id="pn"></h3><p id="pp"></p><input id="phone" value="254"><button onclick="pay()" style="width:100%;padding:13px;background:#0A8EA8;color:#fff;border:none;border-radius:8px;font-weight:bold">Lipa na M-Pesa</button><button onclick="document.getElementById('m').style.display='none'" style="width:100%;margin-top:8px;padding:10px;background:#eee;border:none;border-radius:8px">Cancel</button><p id="st" style="text-align:center;font-weight:bold"></p></div></div>
    <script>
    let pr;function buy(id,price,name){{pr=price;document.getElementById('pn').innerText=name;document.getElementById('pp').innerText='KSH '+price;document.getElementById('m').style.display='flex'}}
    async function pay(){{let ph=document.getElementById('phone').value;document.getElementById('st').innerText='Sending...';let r=await fetch('/mpesa/stkpush',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{phone:ph,amount:pr}})}});let d=await r.json();document.getElementById('st').innerText=d.error?d.error:(d.ResponseCode=='0'?'✅ Check phone!':'Error '+JSON.stringify(d))}}
    </script></body></html>
    '''
