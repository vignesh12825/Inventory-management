from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class InventoryBase(BaseModel):
    product_id: int
    location_id: int
    quantity: int
    reserved_quantity: int = 0
    unit_cost: Optional[float] = None
    notes: Optional[str] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    reserved_quantity: Optional[int] = None
    unit_cost: Optional[float] = None
    notes: Optional[str] = None

class Inventory(InventoryBase):
    id: int
    available_quantity: int
    last_restocked: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InventoryList(BaseModel):
    inventory_items: List[Inventory]
    total: int
    page: int
    size: int

class StockMovementBase(BaseModel):
    movement_type: str
    quantity: int
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    unit_cost: Optional[float] = None
    notes: Optional[str] = None

class StockMovementCreate(StockMovementBase):
    pass

class StockMovement(StockMovementBase):
    id: int
    inventory_item_id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class StockMovementList(BaseModel):
    movements: List[StockMovement]
    total: int
    page: int
    size: int

class StockAdjustmentRequest(BaseModel):
    quantity_change: int
    notes: Optional[str] = None 