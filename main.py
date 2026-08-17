from fastapi import FastAPI
from database import init_db
from modules.auth import router as auth_router

app = FastAPI(title="LONMA Orbit API")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
