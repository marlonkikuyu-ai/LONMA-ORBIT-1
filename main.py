from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="LONMA ORBIT")

# mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/www")
def www():
    return FileResponse("static/index.html")

@app.get("/orders")
def get_orders():
    return {"orders": [
        {"id":"ORD-10284","customer":"Sarah Wanjiku","total":1850,"status":"Delivered"},
        {"id":"ORD-10283","customer":"James Omondi","total":4200,"status":"In Transit"},
        {"id":"ORD-10282","customer":"Brian 0727828838","total":3100,"status":"Pending"}
    ]}

@app.get("/riders")
def get_riders():
    return {"riders": [
        {"name":"Peter Rider - 0727828838","status":"Online"},
        {"name":"John Rider - 07463876981","status":"Online"}
    ]}

@app.post("/pay/mpesa")
def pay_mpesa(data: dict):
    return {"status":"sent","phone": data.get("phone","0727828838"), "amount": data.get("amount", 0)}
