from pydantic import BaseModel

class PayRequest(BaseModel):
    phone: str
    amount: int
    order_id: str

@app.post("/pay/mpesa")
def mpesa_pay(req: PayRequest):
    clean_phone = req.phone.replace("+", "").replace(" ", "")
    if clean_phone.startswith("0"):
        clean_phone = "254" + clean_phone[1:]
    return {
        "status": "sent",
        "message": f"STK Push sent to {req.phone}",
        "phone": clean_phone,
        "amount": req.amount,
        "order_id": req.order_id,
        "checkout_id": f"CHK-{req.order_id}"
    }

@app.get("/pay/status/{checkout_id}")
def pay_status(checkout_id: str):
    return {"checkout_id": checkout_id, "status": "Paid", "method": "M-Pesa"}
