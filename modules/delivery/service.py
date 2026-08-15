from sqlalchemy.orm import Session
from geopy.distance import geodesic
from modules.supermarket.models import Supermarket
from modules.rider.models import Rider
def calculate_delivery_fee(db: Session, supermarket_id: str, customer_lat: float, customer_lng: float):
    sm = db.query(Supermarket).filter(Supermarket.id==supermarket_id).first()
    if not sm:
        return 150
    dist = geodesic((sm.lat, sm.lng), (customer_lat, customer_lng)).km
    if dist <= 3:
        return 100
    if dist <= 10:
        return 100 + (dist - 3) * 20
    return 240 + (dist - 10) * 30
def find_nearest_rider(db: Session, supermarket_lat: float, supermarket_lng: float):
    riders = db.query(Rider).filter(Rider.is_online==True).all()
    if not riders:
        return None
    nearest = min(riders, key=lambda r: geodesic((supermarket_lat, supermarket_lng), (r.lat, r.lng)).km)
    return nearest
