import os
import sys
import traceback
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

print("=== STARTING APP DEBUG ===")
print("DATABASE_URL set:", "YES" if os.getenv("DATABASE_URL") else "NO")
print("PORT:", os.getenv("PORT"))

try:
    from database import engine, Base, get_db
    print("Importing database.py: OK")
    Base.metadata.create_all(bind=engine)
    print("DB Tables created: OK")
except Exception:
    print("CRASH DURING STARTUP:")
    traceback.print_exc()
    sys.exit(1)

from core.config import settings

from modules.auth import routes as auth_routes
from modules.user import routes as user_routes
from modules.supermarket import routes as supermarket_routes
from modules.product import routes as product_routes
from modules.rider import routes as rider_routes
from modules.order import routes as order_routes
from modules.delivery import routes as delivery_routes
from modules.payment import routes as payment_routes
from modules.admin import routes as admin_routes

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_routes.router, prefix="/api/user", tags=["User"])
app.include_router(supermarket_routes.router, prefix="/api/supermarket", tags=["Supermarket"])
app.include_router(product_routes.router, prefix="/api/product", tags=["Product"])
app.include_router(rider_routes.router, prefix="/api/rider", tags=["Rider"])
app.include_router(order_routes.router, prefix="/api/order", tags=["Order"])
app.include_router(delivery_routes.router, prefix="/api/delivery", tags=["Delivery"])
app.include_router(payment_routes.router, prefix="/api/payment", tags=["Payment"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])

@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok", "db": "connected"}

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

print("=== STARTING APP DEBUG END ===")
