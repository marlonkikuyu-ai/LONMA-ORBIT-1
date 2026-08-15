from sqlalchemy import Column, String, Float, ForeignKey
import uuid
from core.db import Base

class DeliveryZone(Base):
    _tablename_ = "delivery_zones"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    supermarket_id = Column(String, ForeignKey("supermarkets.id"), nullable=False)
    name = Column(String, nullable=False)
    base_fee = Column(Float, nullable=False)
    per_km_fee = Column(Float, nullable=False)
