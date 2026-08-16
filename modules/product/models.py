from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
