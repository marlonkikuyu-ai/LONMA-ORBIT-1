from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import engine, Base
from routes import orders, riders, shops, mpesa

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LONMA ORBIT API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lonmaorbit.co.ke","https://www.lonmaorbit.co.ke","https://themakers.co.ke","https://app.lonmaorbit.co.ke","*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

@app.api_route("/", methods=["GET","HEAD"], operation_id="root_live")
def root(): return {"app":"LONMA ORBIT","status":"Live","region":"Thika"}

@app.api_route("/health", methods=["GET","HEAD"], operation_id="health_live")
def health(): return {"ok":True}

@app.get("/favicon.ico", include_in_schema=False)
def fav(): return JSONResponse({}, 204)

app.include_router(orders.router, prefix="/api")
app.include_router(riders.router, prefix="/api")
app.include_router(shops.router, prefix="/api")
app.include_router(mpesa.router, prefix="/api")
