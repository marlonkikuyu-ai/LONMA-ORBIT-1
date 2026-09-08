from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import engine, Base
import models
from routes import orders

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LONMA ORBIT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/", methods=["GET","HEAD"], operation_id="root_final")
def root():
    return {"app":"LONMA ORBIT","status":"Live Thika"}

@app.api_route("/health", methods=["GET","HEAD"], operation_id="health_final")
def health():
    return {"ok": True}

@app.get("/favicon.ico", include_in_schema=False)
def fav(): return JSONResponse({}, status_code=204)

app.include_router(orders.router, prefix="/api", tags=["orders"])
