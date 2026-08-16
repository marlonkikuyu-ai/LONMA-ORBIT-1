from pydantic import BaseModel
from decimal import Decimal

class AnalyticsOut(BaseModel):
    total_users: int
    total_merchants: int
    total_transactions: int
    total_volume: Decimal
    frozen_wallets: int

class FreezeWalletRequest(BaseModel):
    user_id: int

class MerchantApprovalRequest(BaseModel):
    merchant_id: int
