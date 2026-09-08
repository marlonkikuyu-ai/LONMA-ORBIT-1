from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LONMA ORBIT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now, we restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"message": "LONMA ORBIT API is Live", "url": "https://app.lonmaorbit.co.ke"}

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "ok"}

# Add your real routes below, make sure each function name is UNIQUE
@app.get("/api/test")
def test_api():
    return {"test": "working"}
