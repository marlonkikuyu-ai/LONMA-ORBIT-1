from sqlalchemy.orm import Session
from modules.user import models
from .schemas import AddressCreate

def create_address(db: Session, user_id: int, address: AddressCreate):
    db_address = models.Address(user_id=user_id, **address.model_dump())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def get_user_addresses(db: Session, user_id: int):
    return db.query(models.Address).filter(models.Address.user_id == user_id).all()

def get_wallet(db: Session, user_id: int):
    return db.query(models.Wallet).filter(models.Wallet.user_id == user_id).first()

def create_wallet(db: Session, user_id: int):
    wallet = models.Wallet(user_id=user_id)
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet

def top_up_wallet(db: Session, user_id: int, amount: float):
    wallet = get_wallet(db, user_id)
    if not wallet:
        wallet = create_wallet(db, user_id)
    wallet.balance += amount
    db.commit()
    db.refresh(wallet)
    return wallet
