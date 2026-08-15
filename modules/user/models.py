from sqlalchemy import Column, String, Float, ForeignKey, DateTime
import uuid
from datetime import datetime
from core.db import Base

class Address(Base):
    _tablename_ = "addresses"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    label = Column(String, nullable=False)
    address = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Wallet(Base):
    _tablename_ = "wallets"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    balance = Column(Float, default=0.0)
