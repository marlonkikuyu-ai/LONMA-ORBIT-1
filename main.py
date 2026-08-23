from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import osfrom fastapi import FastAPI
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
# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/www")
    def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/dashboard")
    def serve_dashboard():
        return FileResponse(os.path.join(frontend_path, "dashboard.html"))
