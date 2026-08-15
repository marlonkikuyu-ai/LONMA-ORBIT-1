from sqlalchemy.orm import Session
from modules.supermarket.models import Supermarket

def get_supermarket(db: Session, supermarket_id: str):
    return db.query(Supermarket).filter(Supermarket.id==supermarket_id).first()

def update_commission(db: Session, supermarket_id: str, rate: float):
    sm = db.query(Supermarket).filter(Supermarket.id==supermarket_id).first()
    if sm:
        sm.commission_rate = rate
        db.commit()
    return sm
