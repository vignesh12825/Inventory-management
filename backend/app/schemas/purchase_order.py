from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from enum import Enum
from app.schemas.supplier import Supplier
from app.schemas.product import Product

class PurchaseOrderStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ORDERED = "ordered"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class PurchaseOrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    supplier_sku: Optional[str] = None
    notes: Optional[str] = None

class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass

class PurchaseOrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    supplier_sku: Optional[str] = None
    notes: Optional[str] = None

class PurchaseOrderItem(PurchaseOrderItemBase):
    id: int
    purchase_order_id: int
    total_price: float
    received_quantity: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    product: Optional[Product] = None

    class Config:
        from_attributes = True

class PurchaseOrderBase(BaseModel):
    supplier_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    payment_terms: Optional[str] = None
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None
    notes: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate]
    tax_amount: Optional[float] = 0.0
    shipping_amount: Optional[float] = 0.0

class PurchaseOrderUpdate(BaseModel):
    supplier_id: Optional[int] = None
    status: Optional[PurchaseOrderStatus] = None
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    delivery_date: Optional[date] = None
    payment_terms: Optional[str] = None
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None
    notes: Optional[str] = None
    tax_amount: Optional[float] = None
    shipping_amount: Optional[float] = None

class PurchaseOrderUpdateWithItems(BaseModel):
    supplier_id: Optional[int] = None
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    payment_terms: Optional[str] = None
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None
    notes: Optional[str] = None
    tax_amount: Optional[float] = None
    shipping_amount: Optional[float] = None
    items: List[PurchaseOrderItemCreate]

class PurchaseOrder(PurchaseOrderBase):
    id: int
    po_number: str
    status: PurchaseOrderStatus
    subtotal: float
    tax_amount: float
    shipping_amount: float
    total_amount: float
    currency: str
    created_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[PurchaseOrderItem] = []
    supplier: Optional[Supplier] = None

    class Config:
        from_attributes = True

class PurchaseOrderList(BaseModel):
    purchase_orders: List[PurchaseOrder]
    total: int
    page: int
    size: int 