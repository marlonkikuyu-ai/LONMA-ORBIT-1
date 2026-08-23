import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/www")
def serve_www():
    path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "frontend/index.html not found"}
