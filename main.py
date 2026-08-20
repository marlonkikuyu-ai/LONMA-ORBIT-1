from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    import auth
    has_auth = True
except ImportError:
    has_auth = False

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if has_auth:
    app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def root():
    return {"status": "ok", "auth_loaded": has_auth}

@app.get("/health")
def health():
    return {"status": "healthy"}
