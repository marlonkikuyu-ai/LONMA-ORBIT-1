from sqlalchemy.orm import Session
from.models import Address, Wallet
from.schemas import AddressCreate, WalletCreate
from fastapi import HTTPException

def create_address(db: Session, user_id: int, address_data: AddressCreate):
    address = Address(user_id=user_id, label=address_data.label, address_line=address_data.address_line, latitude=address_data.latitude, longitude=address_data.longitude)
    db.add(address)
    db.commit()
    db.refresh(address)
    return address

def get_user_addresses(db: Session, user_id: int):
    return db.query(Address).filter(Address.user_id == user_id).all()

def create_wallet(db: Session, user_id: int):
    existing = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if existing:
        return existing
    wallet = Wallet(user_id=user_id)
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet

def get_wallet(db: Session, user_id: int):
    return db.query(Wallet).filter(Wallet.user_id == user_id).first()

def top_up_wallet(db: Session, user_id: int, amount: float):
    wallet = get_wallet(db, user_id)
    if not wallet:
        wallet = create_wallet(db, user_id)
    wallet.balance = wallet.balance + amount
    db.commit()
    db.refresh(wallet)
    return wallet

def deduct_wallet(db: Session, user_id: int, amount: float):
    wallet = get_wallet(db, user_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    wallet.balance = wallet.balance - amount
    db.commit()
    db.refresh(wallet)
    return wallet
