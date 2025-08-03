from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class LocationBase(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    warehouse_type: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    warehouse_type: Optional[str] = None
    is_active: Optional[bool] = None

class Location(LocationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LocationList(BaseModel):
    locations: List[Location]
    total: int
    page: int
    size: int 