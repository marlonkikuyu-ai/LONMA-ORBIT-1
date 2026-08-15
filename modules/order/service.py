from sqlalchemy.orm import Session
from datetime import datetime
from modules.order import models, schemas
from modules.product.models import Product
from modules.supermarket.models import Supermarket
from modules.rider.models import Rider
from modules.delivery.service import calculate_delivery_fee, find_nearest_rider

def create_order(db: Session, order: schemas.OrderCreate, customer_id: str):
    sm = db.query(Supermarket).filter(Supermarket.id==order.supermarket_id).first()
    if not sm:
        raise Exception("Supermarket not found")
    total = 0
    for item in order.items:
        p = db.query(Product).filter(Product.id==item.product_id).first()
        if not p or p.stock < item.quantity:
            raise Exception("Product out of stock")
        total += p.price * item.quantity
    delivery_fee = calculate_delivery_fee(db, order.supermarket_id, order.lat, order.lng)
    commission = total * sm.commission_rate
    payout = total - commission
    db_order = models.Order(customer_id=customer_id, supermarket_id=order.supermarket_id, total_amount=total, delivery_fee=delivery_fee, commission=commission, supermarket_payout=payout, delivery_address=order.delivery_address, lat=order.lat, lng=order.lng)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    for item in order.items:
        p = db.query(Product).filter(Product.id==item.product_id).first()
        p.stock -= item.quantity
        db_item = models.OrderItem(order_id=db_order.id, product_id=item.product_id, quantity=item.quantity, unit_price=p.price, total_price=p.price*item.quantity)
        db.add(db_item)
    db.commit()
    return db_order

def assign_rider(db: Session, order_id: str, rider_id: str = None):
    order = db.query(models.Order).filter(models.Order.id==order_id).first()
    if not order:
        raise Exception("Order not found")
    if rider_id:
        rider = db.query(Rider).filter(Rider.id==rider_id).first()
    else:
        sm = db.query(Supermarket).filter(Supermarket.id==order.supermarket_id).first()
        rider = find_nearest_rider(db, sm.lat, sm.lng)
    if not rider:
        raise Exception("No rider available")
    order.rider_id = rider.id
    order.status = "accepted"
    db.commit()
    return order

def update_status(db: Session, order_id: str, status: str):
    order = db.query(models.Order).filter(models.Order.id==order_id).first()
    if not order:
        raise Exception("Order not found")
    order.status = status
    if status == "packed":
        order.packed_at = datetime.utcnow()
    if status == "picked":
        order.picked_at = datetime.utcnow()
    if status == "delivered":
        order.delivered_at = datetime.utcnow()
        if order.rider_id:
            rider = db.query(Rider).filter(Rider.id==order.rider_id).first()
            rider.total_deliveries += 1
            rider.wallet_balance += 150
    db.commit()
    return order
