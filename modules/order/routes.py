from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db
from core.security import get_current_user, require_role
from modules.order import schemas
from modules.order.service import create_order, assign_rider, update_status
from modules.order.models import Order

router = APIRouter()

@router.post("/", response_model=schemas.OrderOut)
def place_order(order: schemas.OrderCreate, db: Session = Depends(get_db), user = Depends(require_role(["customer"]))):
    try:
        return create_order(db, order, user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/assign")
def assign(order_id: str, rider_id: str | None = None, db: Session = Depends(get_db), user = Depends(require_role(["admin"]))):
    try:
        return assign_rider(db, order_id, rider_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/status/{status}")
def status(order_id: str, status: str, db: Session = Depends(get_db)):
    try:
        return update_status(db, order_id, status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: str, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id==order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    return o
