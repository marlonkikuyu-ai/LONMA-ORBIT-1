from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, Base, engine
import os

app = FastAPI(title="Lonma Orbit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

# Import all routers
from modules.auth.router import router as auth_router
from modules.user.router import router as user_router
from modules.admin.router import router as admin_router
from modules.product.router import router as product_router
from modules.order.router import router as order_router
from modules.payment.router import router as payment_router
from modules.delivery.router import router as delivery_router
from modules.rider.router import router as rider_router
from modules.supermarket.router import router as supermarket_router

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(product_router, prefix="/products", tags=["products"])
app.include_router(order_router, prefix="/orders", tags=["orders"])
app.include_router(payment_router, prefix="/payments", tags=["payments"])
app.include_router(delivery_router, prefix="/delivery", tags=["delivery"])
app.include_router(rider_router, prefix="/riders", tags=["riders"])
app.include_router(supermarket_router, prefix="/supermarkets", tags=["supermarkets"])

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}
