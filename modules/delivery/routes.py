from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from.schemas import DeliveryZoneCreate, DeliveryZoneOut, DeliveryFeeRequest, DeliveryFeeOut, AssignRiderRequest
from.service import create_delivery_zone, get_delivery_zones, calculate_delivery_fee, assign_delivery
from core.security import get_current_user

router = APIRouter()

@router.post("/zones", response_model=DeliveryZoneOut)
def create_zone(zone: DeliveryZoneCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_delivery_zone(db, zone)

@router.get("/zones", response_model=list[DeliveryZoneOut])
def list_zones(db: Session = Depends(get_db)):
    return get_delivery_zones(db)

@router.post("/fee", response_model=DeliveryFeeOut)
def get_fee(req: DeliveryFeeRequest, db: Session = Depends(get_db)):
    return calculate_delivery_fee(db, req.zone_id, req.distance_km)

@router.post("/assign")
def assign(req: AssignRiderRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return assign_delivery(db, req)
