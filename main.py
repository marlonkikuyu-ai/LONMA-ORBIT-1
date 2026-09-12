from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LONMA ORBIT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "LONMA ORBIT is Live", "services": ["PA Systems", "UI/UX", "Photography", "Podcast", "Activation", "Websites", "Excel & PowerPoint"]}

@app.get("/services")
def get_services():
    return [
        {"id": 1, "name": "Public Address Systems"},
        {"id": 2, "name": "UI/UX Design"},
        {"id": 3, "name": "Tour Guide Services"},
        {"id": 4, "name": "Photography Services"},
        {"id": 5, "name": "Instore/Market Activation"},
        {"id": 6, "name": "Podcast sessions"},
        {"id": 7, "name": "Social Media & Website design"},
        {"id": 8, "name": "Excel & PowerPoint"}
    ]
