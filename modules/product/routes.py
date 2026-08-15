from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db
from core.security import require_role
from modules.product import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), user = Depends(require_role(["supermarket", "admin"]))):
    db_p = models.Product(**product.model_dump())
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p

@router.get("/supermarket/{supermarket_id}", response_model=list[schemas.ProductOut])
def list_products(supermarket_id: str, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.supermarket_id==supermarket_id, models.Product.is_active==True).all()

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id==product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: str, data: schemas.ProductUpdate, db: Session = Depends(get_db), user = Depends(require_role(["supermarket", "admin"]))):
    p = db.query(models.Product).filter(models.Product.id==product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db), user = Depends(require_role(["supermarket", "admin"]))):
    p = db.query(models.Product).filter(models.Product.id==product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    p.is_active = False
    db.commit()
    return {"detail": "Product deactivated"}
