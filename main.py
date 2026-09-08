from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lonmaorbit.co.ke", "https://themakers.co.ke", "https://app.lonmaorbit.co.ke"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FIX 1: Allow both GET and HEAD so Render health check passes
@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return {"status": "LONMA ORBIT API Live", "domain": "app.lonmaorbit.co.ke"}

@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}

@app.get("/www")
def www_page():
    return {"www": "ok"}

# your other routes...
