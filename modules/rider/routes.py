from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db
from core.security import require_role
from modules.rider import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.RiderOut)
def create_rider(rider: schemas.RiderCreate, db: Session = Depends(get_db), user = Depends(require_role(["admin"]))):
    db_r = models.Rider(user_id=user.id, **rider.model_dump())
    db.add(db_r)
    db.commit()
    db.refresh(db_r)
    return db_r

@router.post("/location")
def update_location(data: schemas.RiderLocationUpdate, db: Session = Depends(get_db), user = Depends(require_role(["rider"]))):
    rider = db.query(models.Rider).filter(models.Rider.user_id==user.id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    rider.lat = data.lat
    rider.lng = data.lng
    db.commit()
    return {"status": "location updated"}

@router.post("/status")
def update_status(data: schemas.RiderStatusUpdate, db: Session = Depends(get_db), user = Depends(require_role(["rider"]))):
    rider = db.query(models.Rider).filter(models.Rider.user_id==user.id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    rider.is_online = data.is_online
    db.commit()
    return {"status": "status updated"}

@router.get("/available", response_model=list[schemas.RiderOut])
def list_available_riders(db: Session = Depends(get_db)):
    return db.query(models.Rider).filter(models.Rider.is_online==True).all()
