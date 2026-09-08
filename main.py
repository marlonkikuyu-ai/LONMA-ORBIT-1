from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="LONMA ORBIT API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Allow your Olitt shops to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lonmaorbit.co.ke",
        "https://www.lonmaorbit.co.ke",
        "https://themakers.co.ke",
        "https://app.lonmaorbit.co.ke",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/", methods=["GET", "HEAD"], operation_id="root_check")
def root():
    return {"status": "LONMA ORBIT API Live", "domain": "app.lonmaorbit.co.ke"}

@app.api_route("/health", methods=["GET", "HEAD"], operation_id="health_check_unique")
def health():
    return {"status": "ok", "service": "lonma-orbit"}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return JSONResponse(content={}, status_code=204)

@app.get("/appsettings.json", include_in_schema=False)
def appsettings():
    return JSONResponse(content={}, status_code=204)

# YOUR REAL ROUTES START HERE - make sure each def name is UNIQUE
@app.get("/api/test", operation_id="test_api")
def test_api():
    return {"message": "API working for Thika supermarkets"}

# Example: Add your orders, riders, mpesa routes below
# @app.get("/api/orders", operation_id="list_orders")
# def list_orders(): ...
