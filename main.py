from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# PASTE HERE, right after app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lonmaorbit.co.ke", "https://themakers.co.ke", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... your other routes below
@app.get("/")
def home():
    ...
