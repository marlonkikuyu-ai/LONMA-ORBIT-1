from sqlalchemy.orm import Session
from.models import Rider
from.schemas import RiderCreate, RiderUpdate
from fastapi import HTTPException

def create_rider(db: Session, rider_data: RiderCreate):
    rider = Rider(user_id=rider_data.user_id, vehicle_type=rider_data.vehicle_type, vehicle_number=rider_data.vehicle_number, latitude=rider_data.latitude, longitude=rider_data.longitude)
    db.add(rider)
    db.commit()
    db.refresh(rider)
    return rider

def get_rider(db: Session, rider_id: int):
    return db.query(Rider).filter(Rider.id == rider_id).first()

def get_available_riders(db: Session):
    return db.query(Rider).filter(Rider.is_available == True).all()

def update_rider(db: Session, rider_id: int, rider_data: RiderUpdate):
    rider = get_rider(db, rider_id)
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    for key, value in rider_data.dict(exclude_unset=True).items():
        setattr(rider, key, value)
    db.commit()
    db.refresh(rider)
    return rider

def add_earning(db: Session, rider_id: int, amount: float):
    rider = get_rider(db, rider_id)
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    rider.earnings = rider.earnings + amount
    db.commit()
    db.refresh(rider)
    return rider

def update_rating(db: Session, rider_id: int, rating: float):
    rider = get_rider(db, rider_id)
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    total = rider.rating * rider.total_ratings
    rider.total_ratings = rider.total_ratings + 1
    rider.rating = (total + rating) / rider.total_ratings
    db.commit()
    db.refresh(rider)
    return rider
