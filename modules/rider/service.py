from sqlalchemy.orm import Session
from modules.rider.models import Rider

def add_earning(db: Session, rider_id: str, amount: float):
    rider = db.query(Rider).filter(Rider.id==rider_id).first()
    if rider:
        rider.wallet_balance += amount
        rider.total_deliveries += 1
        db.commit()
    return rider

def update_rating(db: Session, rider_id: str, rating: float):
    rider = db.query(Rider).filter(Rider.id==rider_id).first()
    if rider:
        rider.rating = (rider.rating + rating) / 2
        db.commit()
    return rider
