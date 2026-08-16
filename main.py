from fastapi import FastAPI
from database import Base, engine
from modules import auth, user, supermarket, product, order, payment, rider
import os

print("STARTING APP...")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

app = FastAPI(title="Lonma API")

# Create tables
Base.metadata.create_all(bind=engine)
print("TABLES CREATED")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(supermarket.router, prefix="/supermarkets", tags=["Supermarkets"])
app.include_router(product.router, prefix="/products", tags=["Products"])
app.include_router(order.router, prefix="/orders", tags=["Orders"])
app.include_router(payment.router, prefix="/payments", tags=["Payments"])
app.include_router(rider.router, prefix="/riders", tags=["Riders"])

@app.get("/")
def root():
    return {"message": "Lonma API is running"}

print("APP STARTED SUCCESSFULLY")
