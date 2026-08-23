import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Your existing routers and code here...
# e.g. app.include_router(auth.router) etc

# Add this at the very bottom of main.py
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    @app.get("/app-login")
    def serve_login():
        return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/")
def root():
    return {"status": "ok", "auth_loaded": True}
