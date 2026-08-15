import os
import traceback

print("STARTING APP...")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("SECRET_KEY:", os.getenv("SECRET_KEY"))

try:
    from fastapi import FastAPI
    from database import engine, Base, get_db
    # TEMP: comment all modules until we fix them
    # from modules import users, wallets, transactions, merchants, disputes, admin, referrals, analytics
    
    app = FastAPI(title="LONMA ORBIT API")
    
    # TEMP: comment all routers
    # app.include_router(users.router, prefix="/users", tags=["Users"])
    # app.include_router(wallets.router, prefix="/wallets", tags=["Wallets"])
    # app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
    # app.include_router(merchants.router, prefix="/merchants", tags=["Merchants"])
    # app.include_router(disputes.router, prefix="/disputes", tags=["Disputes"])
    # app.include_router(admin.router, prefix="/admin", tags=["Admin"])
    # app.include_router(referrals.router, prefix="/referrals", tags=["Referrals"])
    # app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
    
    @app.get("/")
    def root():
        return {"status": "LONMA ORBIT API is LIVE"}
    
    Base.metadata.create_all(bind=engine)
    print("APP STARTED SUCCESSFULLY")
    
except Exception as e:
    print("CRASHED:")
    traceback.print_exc()
