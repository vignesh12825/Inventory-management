from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    address = Column(Text, nullable=True)
    description = Column(String, nullable=True)
    warehouse_type = Column(String, nullable=True)  # main, secondary, retail, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    inventory_items = relationship("Inventory", back_populates="location")
    stock_movements_from = relationship("StockMovement", foreign_keys="StockMovement.from_location_id", back_populates="from_location")
    stock_movements_to = relationship("StockMovement", foreign_keys="StockMovement.to_location_id", back_populates="to_location") 