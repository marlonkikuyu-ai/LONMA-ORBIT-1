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

print("APP STARTED SUCCESSFULLY")
