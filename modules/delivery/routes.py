from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from.schemas import OrderCreate, OrderOut, OrderStatusUpdate
from.service import create_order, get_user_orders, get_order_by_id, update_order_status, get_merchant_orders
from core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=OrderOut)
def create_new_order(order: OrderCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_order(db, user.id, order)

@router.get("/me", response_model=list[OrderOut])
def read_user_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_user_orders(db, user.id)

@router.get("/{order_id}", response_model=OrderOut)
def read_order(order_id: int, db: Session = Depends(get_db)):
    return get_order_by_id(db, order_id)

@router.patch("/{order_id}/status", response_model=OrderOut)
def update_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    return update_order_status(db, order_id, payload.status)

@router.get("/merchant/{merchant_id}", response_model=list[OrderOut])
def read_merchant_orders(merchant_id: int, db: Session = Depends(get_db)):
    return get_merchant_orders(db, merchant_id)
