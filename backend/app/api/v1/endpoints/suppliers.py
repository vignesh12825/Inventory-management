from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.supplier import Supplier, SupplierCreate, SupplierUpdate
from app.schemas.common import PaginatedResponse
from app.models.supplier import Supplier as SupplierModel
from sqlalchemy import and_

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[Supplier])
def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> Any:
    """Get all suppliers with optional filtering and pagination"""
    query = db.query(SupplierModel)
    
    if search:
        query = query.filter(
            and_(
                SupplierModel.name.ilike(f"%{search}%") |
                SupplierModel.code.ilike(f"%{search}%") |
                SupplierModel.contact_person.ilike(f"%{search}%")
            )
        )
    
    if is_active is not None:
        query = query.filter(SupplierModel.is_active == is_active)
    
    total = query.count()
    suppliers = query.offset(skip).limit(limit).all()
    
    return PaginatedResponse(
        data=suppliers,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.post("/", response_model=Supplier)
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    """Create a new supplier"""
    # Check if supplier code already exists
    existing_supplier = db.query(SupplierModel).filter(SupplierModel.code == supplier.code).first()
    if existing_supplier:
        raise HTTPException(status_code=400, detail="Supplier code already exists")
    
    db_supplier = SupplierModel(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.get("/{supplier_id}", response_model=Supplier)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Get a specific supplier by ID"""
    supplier = db.query(SupplierModel).filter(SupplierModel.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.put("/{supplier_id}", response_model=Supplier)
def update_supplier(supplier_id: int, supplier: SupplierUpdate, db: Session = Depends(get_db)):
    """Update a supplier"""
    db_supplier = db.query(SupplierModel).filter(SupplierModel.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Check if new code conflicts with existing supplier
    if supplier.code and supplier.code != db_supplier.code:
        existing_supplier = db.query(SupplierModel).filter(
            and_(SupplierModel.code == supplier.code, SupplierModel.id != supplier_id)
        ).first()
        if existing_supplier:
            raise HTTPException(status_code=400, detail="Supplier code already exists")
    
    update_data = supplier.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_supplier, field, value)
    
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Delete a supplier (soft delete by setting is_active to False)"""
    supplier = db.query(SupplierModel).filter(SupplierModel.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    supplier.is_active = False
    db.commit()
    return {"message": "Supplier deactivated successfully"} 