@app.get("/mpesa/callback")
@app.post("/mpesa/callback")
async def mpesa_callback(request: Request):
    try:
        data = await request.json() if request.method == "POST" else {"check": "ok"}
        print("M-Pesa Callback:", data)
        # Here you can save to DB or confirm order
        return {"ResultCode": 0, "ResultDesc": "Accepted"}
    except:
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

@app.get("/favicon.ico")
async def favicon():
    return {"status": "ok"}
