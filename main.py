import os
import traceback
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

print("STARTING APP...")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

from database import engine, Base, get_db

app = FastAPI(title="LONMA ORBIT API")

@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        print("TABLES CREATED")
    except Exception as e:
        print("DB NOT READY YET, WILL CREATE ON FIRST REQUEST:", e)

@app.get("/")
def root():
    return {"status": "LONMA ORBIT API is LIVE"}

from modules import auth, user, supermarket, product, order, payment, rider

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(supermarket.router, prefix="/supermarkets", tags=["Supermarkets"])
app.include_router(product.router, prefix="/products", tags=["Products"])
app.include_router(order.router, prefix="/orders", tags=["Orders"])
app.include_router(payment.router, prefix="/payments", tags=["Payments"])
app.include_router(rider.router, prefix="/riders", tags=["Riders"])

print("APP STARTED SUCCESSFULLY")
