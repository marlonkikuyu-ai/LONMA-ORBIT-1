from sqlalchemy.orm import Session
from.models import Order, OrderItem
from.schemas import OrderCreate
from fastapi import HTTPException

def create_order(db: Session, user_id: int, order_data: OrderCreate):
    total = sum(item.price * item.quantity for item in order_data.items)
    db_order = Order(user_id=user_id, merchant_id=order_data.merchant_id, total_amount=total)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    for item in order_data.items:
        db_item = OrderItem(order_id=db_order.id, product_id=item.product_id, product_name=item.product_name, quantity=item.quantity, price=item.price)
        db.add(db_item)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()

def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def update_order_status(db: Session, order_id: int, status: str):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    db.refresh(order)
    return order

def get_merchant_orders(db: Session, merchant_id: int):
    return db.query(Order).filter(Order.merchant_id == merchant_id).all()
