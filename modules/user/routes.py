from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.db import get_db
from core.security import get_current_user
from modules.user import models, schemas

router = APIRouter()

@router.post("/address", response_model=schemas.AddressOut)
def add_address(addr: schemas.AddressCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    db_a = models.Address(user_id=user.id, **addr.model_dump())
    db.add(db_a)
    db.commit()
    db.refresh(db_a)
    return db_a

@router.get("/addresses", response_model=list[schemas.AddressOut])
def list_addresses(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return db.query(models.Address).filter(models.Address.user_id==user.id).all()

@router.get("/wallet", response_model=schemas.WalletOut)
def get_wallet(db: Session = Depends(get_db), user = Depends(get_current_user)):
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id==user.id).first()
    return wallet
