from sqlalchemy.orm import Session
from datetime import datetime
from modules.payment.models import Payout
from modules.rider.models import Rider
from modules.supermarket.models import Supermarket
def create_payout(db: Session, recipient_id: str, recipient_type: str, amount: float):
    p = Payout(recipient_id=recipient_id, recipient_type=recipient_type, amount=amount, status="pending")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p
def process_weekly_payouts(db: Session):
    riders = db.query(Rider).all()
    for r in riders:
        if r.wallet_balance > 0:
            create_payout(db, r.id, "rider", r.wallet_balance)
            r.wallet_balance = 0
    supermarkets = db.query(Supermarket).all()
    db.commit()
    return {"status": "payouts created"}
