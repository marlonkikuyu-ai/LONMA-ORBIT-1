from sqlalchemy import Column, String, Float, ForeignKey, DateTime
import uuid
from datetime import datetime
from core.db import Base

class Order(Base):
    _tablename_ = "orders"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("users.id"), nullable=False)
    supermarket_id = Column(String, ForeignKey("supermarkets.id"), nullable=False)
    rider_id = Column(String, ForeignKey("riders.id"), nullable=True)
    status = Column(String, default="pending")
    total_amount = Column(Float, nullable=False)
    delivery_fee = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    supermarket_payout = Column(Float, nullable=False)
    payment_status = Column(String, default="unpaid")
    delivery_address = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    packed_at = Column(DateTime, nullable=True)
    picked_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

class OrderItem(Base):
    _tablename_ = "order_items"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
