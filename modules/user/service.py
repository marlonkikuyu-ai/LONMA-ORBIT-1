from sqlalchemy.orm import Session
from modules.user.models import Wallet

def create_wallet(db: Session, user_id: str):
    wallet = Wallet(user_id=user_id, balance=0.0)
    db.add(wallet)
    db.commit()
    return wallet

def top_up_wallet(db: Session, user_id: str, amount: float):
    wallet = db.query(Wallet).filter(Wallet.user_id==user_id).first()
    if wallet:
        wallet.balance += amount
        db.commit()
    return wallet
