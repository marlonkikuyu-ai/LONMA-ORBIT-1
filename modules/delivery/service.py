from sqlalchemy.orm import Session
from sqlalchemy import func
import math
from.models import DeliveryZone, Rider, Delivery
from fastapi import HTTPException

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def create_delivery_zone(db: Session, zone_data):
    zone = DeliveryZone(name=zone_data.name, base_fee=zone_data.base_fee, per_km_fee=zone_data.per_km_fee)
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone

def get_delivery_zones(db: Session):
    return db.query(DeliveryZone).all()

def calculate_delivery_fee(db: Session, zone_id: int, distance_km: float):
    zone = db.query(DeliveryZone).filter(DeliveryZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    fee = zone.base_fee + (zone.per_km_fee * distance_km)
    return {"fee": fee, "distance_km": distance_km}

def find_nearest_rider(db: Session, lat: float, lng: float):
    riders = db.query(Rider).filter(Rider.is_available == 1).all()
    if not riders:
        return None
    nearest = min(riders, key=lambda r: haversine(lat, lng, r.latitude, r.longitude))
    return nearest

def assign_delivery(db: Session, req):
    distance = haversine(req.pickup_lat, req.pickup_lng, req.dropoff_lat, req.dropoff_lng)
    fee_data = calculate_delivery_fee(db, req.zone_id, distance)
    rider = find_nearest_rider(db, req.pickup_lat, req.pickup_lng)
    if not rider:
        raise HTTPException(status_code=404, detail="No available rider")
    delivery = Delivery(order_id=req.order_id, rider_id=rider.id, pickup_lat=req.pickup_lat, pickup_lng=req.pickup_lng, dropoff_lat=req.dropoff_lat, dropoff_lng=req.dropoff_lng, distance_km=distance, fee=fee_data["fee"])
    rider.is_available = 0
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery
