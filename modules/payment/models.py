from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from database import Base

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String, nullable=False)
    reference = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Payout(Base):
    __tablename__ = "payouts"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String, nullable=False)
    reference = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
