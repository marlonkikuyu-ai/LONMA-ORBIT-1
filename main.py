from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from database import init_db
from modules.auth.routes import router as auth_router
from modules.user.routes import router as user_router

app = FastAPI(title="Lonma Orbit API")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/user", tags=["User"])

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Lonma Orbit API is live", "docs": "/docs"}

