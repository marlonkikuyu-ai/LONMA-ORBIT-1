from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
@app.head("/")
def root():
    return FileResponse("static/index.html")

@app.get("/www")
def www():
    return FileResponse("static/index.html")

@app.get("/orders")
def orders():
    return {"orders":[
        {"id":"ORD-10284","customer":"Sarah Wanjiku","total":1850,"status":"Delivered"},
        {"id":"ORD-10283","customer":"James Omondi","total":4200,"status":"In Transit"}
    ]}

@app.get("/supermarket")
def supermarket():
    return {"products":[
        {"name":"Fresh Milk 500ml","price":120,"stock":50},
        {"name":"White Bread 400g","price":70,"stock":100}
    ]}

@app.get("/riders")
def riders():
    return {"riders":[{"name":"Peter Rider","status":"Online"}]}

@app.post("/pay/mpesa")
def pay_mpesa(data: dict):
    return {"status":"sent","phone":data.get("phone"),"amount":data.get("amount"),"order_id":data.get("order_id")}
