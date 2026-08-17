from fastapi import FastAPI
from database import init_db
from modules.auth import routes as auth_routes
# from modules.user import routes as user_routes # comment this until schemas ready

app = FastAPI(title="LONMA Orbit API")

@app.on_event("startup")
def on_startup():
    init_db() # run after server starts

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
# app.include_router(user_routes.router, prefix="/user", tags=["User"])

@app.get("/health")
def health(): return {"status": "ok"}
