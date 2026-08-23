from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LONMA ORBIT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.head("/")
def root():
    return {"status": "ok", "auth_loaded": True}

@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}

try:
    from auth import router as auth_router
    app.include_router(auth_router, prefix="/auth")
except:
    pass
