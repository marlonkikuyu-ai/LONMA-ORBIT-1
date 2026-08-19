from fastapi import FastAPI
from database import init_db
from modules.auth import router as auth_router

app = FastAPI(title="LONMA Orbit API")

@app.get("/")
def root():
    return {"message": "LONMA Orbit API is live - go to /docs"}

@app.get("/health")
def health():
    return {"status": "ok", "db": "connected"}

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
