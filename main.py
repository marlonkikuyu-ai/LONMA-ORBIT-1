import os
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

# --- YOUR EXISTING ROUTERS ---
# from core.auth import router as auth_router
# app.include_router(auth_router, prefix="/auth")
# ... keep your other routers ...

@app.get("/")
def root():
    return {"status": "ok", "auth_loaded": True}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Serve frontend files ---
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

@app.get("/www")
def serve_frontend():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "frontend/index.html not found"}
