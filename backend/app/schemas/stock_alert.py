from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.models.stock_alert import AlertType, AlertStatus

# Import product and location schemas
from app.schemas.product import Product
from app.schemas.location import Location

class StockAlertBase(BaseModel):
    product_id: int
    location_id: Optional[int] = None
    alert_type: AlertType
    current_quantity: int
    threshold_quantity: int
    message: str

class StockAlertCreate(StockAlertBase):
    pass

class StockAlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[int] = None
    resolved_by: Optional[int] = None

class StockAlert(StockAlertBase):
    id: int
    status: AlertStatus
    is_email_sent: bool
    is_sms_sent: bool
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    product: Optional[Product] = None
    location: Optional[Location] = None

    class Config:
        from_attributes = True

class AlertRuleBase(BaseModel):
    name: str
    alert_type: AlertType
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    threshold_quantity: int
    threshold_percentage: Optional[float] = None
    notify_email: bool = True
    notify_sms: bool = False
    notify_dashboard: bool = True

class AlertRuleCreate(AlertRuleBase):
    pass

class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    alert_type: Optional[AlertType] = None
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    threshold_quantity: Optional[int] = None
    threshold_percentage: Optional[float] = None
    is_active: Optional[bool] = None
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
    notify_dashboard: Optional[bool] = None

class AlertRule(AlertRuleBase):
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StockAlertList(BaseModel):
    alerts: List[StockAlert]
    total: int
    page: int
    size: int

class AlertRuleList(BaseModel):
    rules: List[AlertRule]
    total: int
    page: int
    size: int 