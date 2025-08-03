from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.location import Location, LocationCreate, LocationUpdate
from app.schemas.common import PaginatedResponse
from app.models.inventory import Location as LocationModel
from sqlalchemy import and_

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[Location])
def get_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    warehouse_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> Any:
    """Get all locations with optional filtering and pagination"""
    query = db.query(LocationModel)
    
    if search:
        query = query.filter(
            and_(
                LocationModel.name.ilike(f"%{search}%") |
                LocationModel.code.ilike(f"%{search}%") |
                LocationModel.address.ilike(f"%{search}%")
            )
        )
    
    if warehouse_type:
        query = query.filter(LocationModel.warehouse_type == warehouse_type)
    
    if is_active is not None:
        query = query.filter(LocationModel.is_active == is_active)
    
    total = query.count()
    locations = query.offset(skip).limit(limit).all()
    
    return PaginatedResponse(
        data=locations,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.post("/", response_model=Location)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    """Create a new location"""
    # Check if location code already exists
    existing_location = db.query(LocationModel).filter(LocationModel.code == location.code).first()
    if existing_location:
        raise HTTPException(status_code=400, detail="Location code already exists")
    
    db_location = LocationModel(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@router.get("/{location_id}", response_model=Location)
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get a specific location by ID"""
    location = db.query(LocationModel).filter(LocationModel.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.put("/{location_id}", response_model=Location)
def update_location(location_id: int, location: LocationUpdate, db: Session = Depends(get_db)):
    """Update a location"""
    db_location = db.query(LocationModel).filter(LocationModel.id == location_id).first()
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Check if new code conflicts with existing location
    if location.code and location.code != db_location.code:
        existing_location = db.query(LocationModel).filter(
            and_(LocationModel.code == location.code, LocationModel.id != location_id)
        ).first()
        if existing_location:
            raise HTTPException(status_code=400, detail="Location code already exists")
    
    update_data = location.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_location, field, value)
    
    db.commit()
    db.refresh(db_location)
    return db_location

@router.delete("/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db)):
    """Delete a location (soft delete by setting is_active to False)"""
    location = db.query(LocationModel).filter(LocationModel.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    location.is_active = False
    db.commit()
    return {"message": "Location deactivated successfully"} 