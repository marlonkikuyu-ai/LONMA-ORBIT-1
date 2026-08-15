from sqlalchemy.orm import Session
from modules.product.models import Product

def reduce_stock(db: Session, product_id: str, quantity: float):
    p = db.query(Product).filter(Product.id==product_id).first()
    if p:
        p.stock -= quantity
        db.commit()
    return p

def restock(db: Session, product_id: str, quantity: float):
    p = db.query(Product).filter(Product.id==product_id).first()
    if p:
        p.stock += quantity
        db.commit()
    return p
