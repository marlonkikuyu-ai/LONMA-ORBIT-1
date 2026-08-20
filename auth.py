from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core import security
from modules.user import models
from .schemas import UserCreate, UserLogin

router = APIRouter()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=security.get_password_hash(user_data.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.add(models.Wallet(user_id=db_user.id))
    db.commit()
    token = security.create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": db_user.id}

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, user_data.email)
    if not user or not security.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = security.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}
