from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StockAlertBase(BaseModel):
    product_id: int
    threshold: int
    alert_type: str  # 'low_stock', 'out_of_stock', 'overstock'
    is_active: bool = True

class StockAlertCreate(StockAlertBase):
    pass

class StockAlertUpdate(BaseModel):
    threshold: Optional[int] = None
    alert_type: Optional[str] = None
    is_active: Optional[bool] = None

class StockAlertResponse(StockAlertBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 