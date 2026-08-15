from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime
import uuid
from datetime import datetime
from core.db import Base

class Product(Base):
    _tablename_ = "products"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    supermarket_id = Column(String, ForeignKey("supermarkets.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Float, default=0.0)
    unit = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
