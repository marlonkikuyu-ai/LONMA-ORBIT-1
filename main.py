from fastapi.staticfiles import StaticFiles
import os

# After app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Make sure you have this too for root
from fastapi.responses import FileResponse

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return FileResponse("static/index.html")

