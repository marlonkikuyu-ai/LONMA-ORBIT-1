from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.db import get_db
from core.security import require_role
from modules.delivery import models, schemas
router = APIRouter()
@router.post("/zone", response_model=schemas.DeliveryZoneOut)
def create_zone(zone: schemas.DeliveryZoneCreate, db: Session = Depends(get_db), user = Depends(require_role(["admin"]))):
    db_z = models.DeliveryZone(**zone.model_dump())
    db.add(db_z)
    db.commit()
    db.refresh(db_z)
    return db_z
@router.get("/zone/{supermarket_id}", response_model=list[schemas.DeliveryZoneOut])
def list_zones(supermarket_id: str, db: Session = Depends(get_db)):
    return db.query(models.DeliveryZone).filter(models.DeliveryZone.supermarket_id==supermarket_id).all()
