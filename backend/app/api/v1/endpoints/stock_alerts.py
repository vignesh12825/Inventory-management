from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.stock_alert import StockAlert
from app.schemas.stock_alert import (
    StockAlertCreate,
    StockAlertUpdate,
    StockAlertResponse
)
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=StockAlertResponse)
async def create_stock_alert(
    alert: StockAlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new stock alert"""
    db_alert = StockAlert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/", response_model=List[StockAlertResponse])
async def get_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all stock alerts"""
    alerts = db.query(StockAlert).all()
    return alerts

@router.get("/{alert_id}", response_model=StockAlertResponse)
async def get_stock_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific stock alert"""
    alert = db.query(StockAlert).filter(StockAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock alert not found"
        )
    return alert

@router.put("/{alert_id}", response_model=StockAlertResponse)
async def update_stock_alert(
    alert_id: int,
    alert_update: StockAlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a stock alert"""
    db_alert = db.query(StockAlert).filter(StockAlert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock alert not found"
        )
    
    update_data = alert_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_alert, field, value)
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.delete("/{alert_id}")
async def delete_stock_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a stock alert"""
    db_alert = db.query(StockAlert).filter(StockAlert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock alert not found"
        )
    
    db.delete(db_alert)
    db.commit()
    return {"message": "Stock alert deleted successfully"} 