from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db
from core.security import require_role
from modules.supermarket import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.SupermarketOut)
def create_supermarket(supermarket: schemas.SupermarketCreate, db: Session = Depends(get_db), user = Depends(require_role(["admin"]))):
    db_sm = models.Supermarket(owner_id=user.id, **supermarket.model_dump())
    db.add(db_sm)
    db.commit()
    db.refresh(db_sm)
    return db_sm

@router.get("/", response_model=list[schemas.SupermarketOut])
def list_supermarkets(db: Session = Depends(get_db)):
    return db.query(models.Supermarket).filter(models.Supermarket.is_active==True).all()

@router.get("/{supermarket_id}", response_model=schemas.SupermarketOut)
def get_supermarket(supermarket_id: str, db: Session = Depends(get_db)):
    sm = db.query(models.Supermarket).filter(models.Supermarket.id==supermarket_id).first()
    if not sm:
        raise HTTPException(status_code=404, detail="Supermarket not found")
    return sm

@router.put("/{supermarket_id}", response_model=schemas.SupermarketOut)
def update_supermarket(supermarket_id: str, data: schemas.SupermarketUpdate, db: Session = Depends(get_db), user = Depends(require_role(["admin"]))):
    sm = db.query(models.Supermarket).filter(models.Supermarket.id==supermarket_id).first()
    if not sm:
        raise HTTPException(status_code=404, detail="Supermarket not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(sm, k, v)
    db.commit()
    db.refresh(sm)
    return sm

@router.delete("/{supermarket_id}")
def delete_supermarket(supermarket_id: str, db: Session = Depends(get_db), user = Depends(require_role(["admin"]))):
    sm = db.query(models.Supermarket).filter(models.Supermarket.id==supermarket_id).first()
    if not sm:
        raise HTTPException(status_code=404, detail="Supermarket not found")
    sm.is_active = False
    db.commit()
    return {"detail": "Supermarket deactivated"}
