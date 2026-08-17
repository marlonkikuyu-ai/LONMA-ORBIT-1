from sqlalchemy.orm import Session
from modules.user import models
from core import security
from .schemas import UserCreate

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_data: UserCreate):
    hashed_password = security.get_password_hash(user_data.password)
    db_user = models.User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Auto create wallet
    wallet = models.Wallet(user_id=db_user.id)
    db.add(wallet)
    db.commit()
    
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict):
    return security.create_access_token(data)
