from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from.schemas import RiderCreate, RiderOut, RiderUpdate, EarningUpdate, RatingUpdate
from.service import create_rider, get_rider, get_available_riders, update_rider, add_earning, update_rating
from core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=RiderOut)
def register_rider(payload: RiderCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_rider(db, payload)

@router.get("/{rider_id}", response_model=RiderOut)
def read_rider(rider_id: int, db: Session = Depends(get_db)):
    return get_rider(db, rider_id)

@router.get("/available", response_model=list[RiderOut])
def list_available_riders(db: Session = Depends(get_db)):
    return get_available_riders(db)

@router.patch("/{rider_id}", response_model=RiderOut)
def update_rider_info(rider_id: int, payload: RiderUpdate, db: Session = Depends(get_db)):
    return update_rider(db, rider_id, payload)

@router.post("/{rider_id}/earning", response_model=RiderOut)
def rider_add_earning(rider_id: int, payload: EarningUpdate, db: Session = Depends(get_db)):
    return add_earning(db, rider_id, payload.amount)

@router.post("/{rider_id}/rating", response_model=RiderOut)
def rider_update_rating(rider_id: int, payload: RatingUpdate, db: Session = Depends(get_db)):
    return update_rating(db, rider_id, payload.rating)
