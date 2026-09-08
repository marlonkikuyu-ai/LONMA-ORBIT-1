from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
router = APIRouter()
@router.get("/orders")
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).order_by(models.Order.id.desc()).all()
@router.post("/orders")
def create_order(data: dict, db: Session = Depends(get_db)):
    o = models.Order(**data)
    db.add(o); db.commit(); db.refresh(o)
    return o
