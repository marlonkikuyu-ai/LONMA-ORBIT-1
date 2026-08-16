from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from.schemas import PaymentCreate, PaymentOut, PayoutCreate, PayoutOut
from.service import create_payment, get_payment_by_reference, update_payment_status, create_payout, get_merchant_payouts
from core.security import get_current_user

router = APIRouter()

@router.post("/pay", response_model=PaymentOut)
def pay_order(payload: PaymentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_payment(db, user.id, payload)

@router.get("/{reference}", response_model=PaymentOut)
def get_payment(reference: str, db: Session = Depends(get_db)):
    return get_payment_by_reference(db, reference)

@router.patch("/{reference}/status")
def update_status(reference: str, status: str, db: Session = Depends(get_db)):
    return update_payment_status(db, reference, status)

@router.post("/payout", response_model=PayoutOut)
def request_payout(payload: PayoutCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_payout(db, payload)

@router.get("/payouts/merchant/{merchant_id}", response_model=list[PayoutOut])
def list_payouts(merchant_id: int, db: Session = Depends(get_db)):
    return get_merchant_payouts(db, merchant_id)
