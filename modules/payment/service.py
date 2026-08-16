from sqlalchemy.orm import Session
import uuid
from.models import Payment, Payout
from fastapi import HTTPException

def generate_reference(prefix):
    return f"{prefix}_{uuid.uuid4().hex}"

def create_payment(db: Session, user_id: int, payment_data):
    reference = generate_reference("PAY")
    payment = Payment(user_id=user_id, order_id=payment_data.order_id, amount=payment_data.amount, method=payment_data.method, reference=reference)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def get_payment_by_reference(db: Session, reference: str):
    return db.query(Payment).filter(Payment.reference == reference).first()

def update_payment_status(db: Session, reference: str, status: str):
    payment = get_payment_by_reference(db, reference)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = status
    db.commit()
    db.refresh(payment)
    return payment

def create_payout(db: Session, payout_data):
    reference = generate_reference("PAYOUT")
    payout = Payout(merchant_id=payout_data.merchant_id, amount=payout_data.amount, method=payout_data.method, reference=reference)
    db.add(payout)
    db.commit()
    db.refresh(payout)
    return payout

def get_merchant_payouts(db: Session, merchant_id: int):
    return db.query(Payout).filter(Payout.merchant_id == merchant_id).all()
