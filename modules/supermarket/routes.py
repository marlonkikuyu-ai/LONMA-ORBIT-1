from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from.schemas import SupermarketCreate, SupermarketOut, SupermarketUpdate
from.service import create_supermarket, get_supermarket, get_all_supermarkets, update_supermarket, delete_supermarket
from core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=SupermarketOut)
def create_new_supermarket(payload: SupermarketCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_supermarket(db, payload)

@router.get("/{supermarket_id}", response_model=SupermarketOut)
def read_supermarket(supermarket_id: int, db: Session = Depends(get_db)):
    return get_supermarket(db, supermarket_id)

@router.get("/", response_model=list[SupermarketOut])
def read_all_supermarkets(db: Session = Depends(get_db)):
    return get_all_supermarkets(db)

@router.patch("/{supermarket_id}", response_model=SupermarketOut)
def update_existing_supermarket(supermarket_id: int, payload: SupermarketUpdate, db: Session = Depends(get_db)):
    return update_supermarket(db, supermarket_id, payload)

@router.delete("/{supermarket_id}")
def delete_existing_supermarket(supermarket_id: int, db: Session = Depends(get_db)):
    return delete_supermarket(db, supermarket_id)
