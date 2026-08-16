from sqlalchemy.orm import Session
from.models import Product
from.schemas import ProductCreate, ProductUpdate
from fastapi import HTTPException

def create_product(db: Session, product_data: ProductCreate):
    product = Product(merchant_id=product_data.merchant_id, name=product_data.name, description=product_data.description, price=product_data.price, stock=product_data.stock, category=product_data.category, image_url=product_data.image_url)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def get_merchant_products(db: Session, merchant_id: int):
    return db.query(Product).filter(Product.merchant_id == merchant_id).all()

def update_product(db: Session, product_id: int, product_data: ProductUpdate):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product_data.dict(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"status": "deleted"}

def update_stock(db: Session, product_id: int, quantity: int):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.stock = product.stock + quantity
    if product.stock < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    db.commit()
    db.refresh(product)
    return product
