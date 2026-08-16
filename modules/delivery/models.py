from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from database import Base

class DeliveryZone(Base):
    __tablename__ = "delivery_zones"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    base_fee = Column(Float, nullable=False)
    per_km_fee = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Rider(Base):
    __tablename__ = "riders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_available = Column(Integer, default=1)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    rider_id = Column(Integer, ForeignKey("riders.id"))
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)
    dropoff_lat = Column(Float, nullable=False)
    dropoff_lng = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
