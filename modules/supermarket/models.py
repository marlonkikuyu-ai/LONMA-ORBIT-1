from sqlalchemy import Column, String, Float, Boolean, DateTime
import uuid
from datetime import datetime
from core.db import Base

class Supermarket(Base):
    _tablename_ = "supermarkets"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    phone = Column(String, nullable=False)
    commission_rate = Column(Float, default=0.12)
    is_active = Column(Boolean, default=True)
    bank_account = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
