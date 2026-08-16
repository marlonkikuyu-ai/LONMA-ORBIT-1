from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Merchant, Transaction, Wallet
from decimal import Decimal

def get_admin_analytics(db: Session):
    total_users = db.query(func.count(User.id)).scalar()
    total_merchants = db.query(func.count(Merchant.id)).scalar()
    total_transactions = db.query(func.count(Transaction.id)).scalar()
    total_volume = db.query(func.sum(Transaction.amount)).scalar() or Decimal(0)
    frozen_wallets = db.query(func.count(Wallet.id)).filter(Wallet.is_frozen == True).scalar()
    return {
        "total_users": total_users,
        "total_merchants": total_merchants,
        "total_transactions": total_transactions,
        "total_volume": total_volume,
        "frozen_wallets": frozen_wallets
    }

def freeze_user_wallet(db: Session, user_id: int):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    wallet.is_frozen = True
    db.commit()

def unfreeze_user_wallet(db: Session, user_id: int):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    wallet.is_frozen = False
    db.commit()

def approve_merchant(db: Session, merchant_id: int):
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    merchant.is_approved = True
    db.commit()
