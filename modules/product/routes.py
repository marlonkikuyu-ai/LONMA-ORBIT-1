from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from.schemas import ProductCreate, ProductOut, ProductUpdate, StockUpdate
from.service import create_product, get_product, get_merchant_products, update_product, delete_product, update_stock
from core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=ProductOut)
def create_new_product(payload: ProductCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_product(db, payload)

@router.get("/{product_id}", response_model=ProductOut)
def read_product(product_id: int, db: Session = Depends(get_db)):
    return get_product(db, product_id)

@router.get("/merchant/{merchant_id}", response_model=list[ProductOut])
def read_merchant_products(merchant_id: int, db: Session = Depends(get_db)):
    return get_merchant_products(db, merchant_id)

@router.patch("/{product_id}", response_model=ProductOut)
def update_existing_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    return update_product(db, product_id, payload)

@router.delete("/{product_id}")
def delete_existing_product(product_id: int, db: Session = Depends(get_db)):
    return delete_product(db, product_id)

@router.patch("/{product_id}/stock", response_model=ProductOut)
def update_product_stock(product_id: int, payload: StockUpdate, db: Session = Depends(get_db)):
    return update_stock(db, product_id, payload.quantity)
