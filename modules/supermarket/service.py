from sqlalchemy.orm import Session
from.models import Supermarket
from.schemas import SupermarketCreate, SupermarketUpdate
from fastapi import HTTPException

def create_supermarket(db: Session, supermarket_data: SupermarketCreate):
    supermarket = Supermarket(owner_id=supermarket_data.owner_id, name=supermarket_data.name, address=supermarket_data.address, latitude=supermarket_data.latitude, longitude=supermarket_data.longitude, phone=supermarket_data.phone)
    db.add(supermarket)
    db.commit()
    db.refresh(supermarket)
    return supermarket

def get_supermarket(db: Session, supermarket_id: int):
    return db.query(Supermarket).filter(Supermarket.id == supermarket_id).first()

def get_all_supermarkets(db: Session):
    return db.query(Supermarket).filter(Supermarket.is_active == True).all()

def update_supermarket(db: Session, supermarket_id: int, supermarket_data: SupermarketUpdate):
    supermarket = get_supermarket(db, supermarket_id)
    if not supermarket:
        raise HTTPException(status_code=404, detail="Supermarket not found")
    for key, value in supermarket_data.dict(exclude_unset=True).items():
        setattr(supermarket, key, value)
    db.commit()
    db.refresh(supermarket)
    return supermarket

def delete_supermarket(db: Session, supermarket_id: int):
    supermarket = get_supermarket(db, supermarket_id)
    if not supermarket:
        raise HTTPException(status_code=404, detail="Supermarket not found")
    supermarket.is_active = False
    db.commit()
    return {"status": "deleted"}
