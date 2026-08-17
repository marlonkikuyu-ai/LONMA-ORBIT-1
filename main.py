from fastapi import FastAPI
from database import Base, engine
from modules.auth import routes as auth_routes

Base.metadata.create_all(bind=engine) # creates tables on first boot

app = FastAPI(title="LONMA Orbit API")

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"msg": "LONMA Orbit API Running"}
