from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)  # in kg
    dimensions = Column(JSON, nullable=True)  # {"length": 10, "width": 5, "height": 2}
    specifications = Column(JSON, nullable=True)  # {"color": "red", "material": "plastic"}
    barcode = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    min_stock_level = Column(Integer, default=0)
    max_stock_level = Column(Integer, nullable=True)
    reorder_point = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    inventory_items = relationship("Inventory", back_populates="product")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="product", cascade="all, delete-orphan")
    stock_alerts = relationship("StockAlert", cascade="all, delete-orphan") 