from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from .service import get_admin_analytics, freeze_user_wallet, unfreeze_user_wallet, approve_merchant
from .schemas import AnalyticsOut, FreezeWalletRequest, MerchantApprovalRequest
from core.security import get_current_admin_user

router = APIRouter()

@router.get("/analytics", response_model=AnalyticsOut)
def read_admin_analytics(db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    return get_admin_analytics(db)

@router.post("/wallet/freeze")
def freeze_wallet(payload: FreezeWalletRequest, db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    freeze_user_wallet(db, payload.user_id)
    return {"status": "frozen"}

@router.post("/wallet/unfreeze")
def unfreeze_wallet(payload: FreezeWalletRequest, db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    unfreeze_user_wallet(db, payload.user_id)
    return {"status": "unfrozen"}

@router.post("/merchant/approve")
def approve_merchant_account(payload: MerchantApprovalRequest, db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    approve_merchant(db, payload.merchant_id)
    return {"status": "approved"}
