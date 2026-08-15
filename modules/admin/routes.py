from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.db import get_db
from core.security import require_role
from modules.order.models import Order
from modules.auth.models import User
from modules.supermarket.models import Supermarket
from modules.admin.schemas import AnalyticsOut
router = APIRouter()
@router.get("/analytics", response_model=AnalyticsOut)
def analytics(db: Session = Depends(get_db), user = Depends(require_role(["admin"]))):
    total_orders = db.query(func.count(Order.id)).scalar()
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
    total_customers = db.query(func.count(User.id)).filter(User.role=="customer").scalar()
    total_supermarkets = db.query(func.count(Supermarket.id)).scalar()
    return {"total_orders": total_orders, "total_revenue": total_revenue, "total_customers": total_customers, "total_supermarkets": total_supermarkets}
