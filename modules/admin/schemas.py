from pydantic import BaseModel
class AnalyticsOut(BaseModel):
    total_orders: int
    total_revenue: float
    total_customers: int
    total_supermarkets: int
