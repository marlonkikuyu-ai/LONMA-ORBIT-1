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

# Try both paths
try:
    from modules.auth.router import router as auth_router
    print("Loaded from modules.auth")
except ModuleNotFoundError:
    import auth.router as auth_module
    auth_router = auth_module.router
    print("Loaded from auth")

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
def root():
    return {"status": "ok", "auth_loaded": True}

@app.get("/health")
def health():
    return {"status": "healthy"}
