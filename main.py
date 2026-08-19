from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Create tables if you have database code - keep your existing DB code below
# For now this line fixes logo
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return FileResponse(os.path.join("static", "index.html"))

# --- KEEP YOUR OLD CODE BELOW THIS LINE ---
# If you have database, auth, etc - paste it here

