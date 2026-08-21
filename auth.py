from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
def register(data: dict):
    return {"message": "register working", "email": data.get("email")}

@router.post("/login")
def login(data: dict):
    return {"message": "login working", "email": data.get("email")}
