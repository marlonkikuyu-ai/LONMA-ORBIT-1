import os
print("ENV CHECK:", os.getenv("DATABASE_URL"), os.getenv("SECRET_KEY"))

from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "it works"}
