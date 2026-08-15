import os
import traceback

print("STARTING APP...")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("SECRET_KEY:", os.getenv("SECRET_KEY"))

try:
    from fastapi import FastAPI
    from database import engine, Base
    
    app = FastAPI(title="LONMA ORBIT API")
    
    @app.get("/")
    def root():
        return {"status": "LONMA ORBIT API is LIVE"}
    
    # TEMP: try create tables but don't crash if DB sleeps
    try:
        Base.metadata.create_all(bind=engine)
        print("TABLES CREATED")
    except Exception as db_err:
        print("DB TABLE CREATION FAILED, WILL RETRY ON FIRST REQUEST:", db_err)
    
    print("APP STARTED SUCCESSFULLY")
    
except Exception as e:
    print("CRASHED:")
    traceback.print_exc()
