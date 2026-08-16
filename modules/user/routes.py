from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from.schemas import AddressCreate, AddressOut, WalletOut, TopUpRequest
from.service import create_address, get_user_addresses, create_wallet, get_wallet, top_up_wallet
from core.security import get_current_user

router = APIRouter()

@router.post("/address", response_model=AddressOut)
def add_address(payload: AddressCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_address(db, user.id, payload)

@router.get("/addresses", response_model=list[AddressOut])
def read_addresses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_user_addresses(db, user.id)

@router.post("/wallet", response_model=WalletOut)
def init_wallet(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_wallet(db, user.id)

@router.get("/wallet", response_model=WalletOut)
def read_wallet(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_wallet(db, user.id)

@router.post("/wallet/top-up", response_model=WalletOut)
def top_up(payload: TopUpRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return top_up_wallet(db, user.id, payload.amount)
