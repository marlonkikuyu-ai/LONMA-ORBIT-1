from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from database import init_db
from modules.auth.routes import router as auth_router
from modules.user.routes import router as user_router

app = FastAPI(title="Lonma Orbit API")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
      <head><title>Lonma Orbit</title></head>
      <body style="font-family:sans-serif; text-align:center; padding-top:100px">
        <h1>🚀 Lonma Orbit is Live!</h1>
        <p>Backend API is running successfully.</p>
        <a href="/docs">View API Docs</a>
      </body>
    </html>
    """

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/user", tags=["User"])
