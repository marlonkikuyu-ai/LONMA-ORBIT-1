from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This version WORKED before
try:
    import auth
    has_auth = True
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
except Exception as e:
    print(f"Auth load failed: {e}")
    has_auth = False

@app.get("/")
def root():
    return {"status": "ok", "auth_loaded": has_auth}

@app.get("/health")
def health():
    return {"status": "healthy"}
