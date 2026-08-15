from geopy.distance import geodesic
import httpx
from core.config import settings

def calculate_distance(lat1, lng1, lat2, lng2):
    return geodesic((lat1, lng1), (lat2, lng2)).km

async def send_sms(phone: str, message: str):
    return {"status": "sent", "phone": phone, "message": message}
