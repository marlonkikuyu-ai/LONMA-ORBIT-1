from sqlalchemy import Column, String, Float, Boolean, DateTime
import uuid
from datetime import datetime
from core.db import Base

class Rider(Base):
    _tablename_ = "riders"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    bike_plate = Column(String, nullable=False)
    lat = Column(Float, default=0.0)
    lng = Column(Float, default=0.0)
    is_online = Column(Boolean, default=False)
    wallet_balance = Column(Float, default=0.0)
    total_deliveries = Column(Float, default=0.0)
    rating = Column(Float, default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)
