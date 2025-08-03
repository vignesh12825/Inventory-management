from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    brand: Optional[str] = None
    model: Optional[str] = None
    price: float
    cost: Optional[float] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, Any]] = None
    specifications: Optional[Dict[str, Any]] = None
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    min_stock_level: Optional[int] = 0
    max_stock_level: Optional[int] = None
    reorder_point: Optional[int] = 0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, Any]] = None
    specifications: Optional[Dict[str, Any]] = None
    barcode: Optional[str] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    min_stock_level: Optional[int] = None
    max_stock_level: Optional[int] = None
    reorder_point: Optional[int] = None

class Product(ProductBase):
    id: int
    is_active: Optional[bool] = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProductList(BaseModel):
    products: List[Product]
    total: int
    page: int
    size: int 