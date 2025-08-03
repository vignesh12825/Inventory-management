from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Any, Optional
from datetime import datetime, timedelta
import json
import logging

from app.core.database import get_db
from app.schemas.stock_alert import (
    StockAlertSchema, 
    StockAlertCreate, 
    StockAlertUpdate,
    StockAlertList,
    AlertRuleSchema,
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleList
)
from app.models.stock_alert import StockAlert, AlertRule
from app.models.product import Product
from app.models.inventory import Inventory
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/alerts", response_model=StockAlertList)
def get_stock_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AlertStatus] = None,
    alert_type: Optional[AlertType] = None,
    product_id: Optional[int] = None,
    location_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Any:
    """Get all stock alerts with optional filtering and pagination"""
    query = db.query(StockAlert).options(
        joinedload(StockAlert.product),
        joinedload(StockAlert.location)
    )
    
    if status:
        query = query.filter(StockAlert.status == status)
    
    if alert_type:
        query = query.filter(StockAlert.alert_type == alert_type)
    
    if product_id:
        query = query.filter(StockAlert.product_id == product_id)
    
    if location_id:
        query = query.filter(StockAlert.location_id == location_id)
    
    total = query.count()
    alerts = query.order_by(StockAlert.created_at.desc()).offset(skip).limit(limit).all()
    
    return StockAlertList(
        alerts=alerts,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/alerts/active", response_model=List[StockAlertSchema])
def get_active_alerts(db: Session = Depends(get_db)):
    """Get all active stock alerts"""
    alerts = db.query(StockAlert).options(
        joinedload(StockAlert.product),
        joinedload(StockAlert.location)
    ).filter(
        StockAlert.status == AlertStatus.ACTIVE
    ).order_by(StockAlert.created_at.desc()).all()
    return alerts

@router.post("/alerts", response_model=StockAlertSchema)
async def create_stock_alert(alert: StockAlertCreate, db: Session = Depends(get_db)):
    """Create a new stock alert"""
    # Validate product exists
    product = db.query(Product).filter(Product.id == alert.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if similar alert already exists
    existing_alert = db.query(StockAlert).filter(
        and_(
            StockAlert.product_id == alert.product_id,
            StockAlert.location_id == alert.location_id,
            StockAlert.alert_type == alert.alert_type,
            StockAlert.status == AlertStatus.ACTIVE
        )
    ).first()
    
    if existing_alert:
        return existing_alert
    
    db_alert = StockAlert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    # Reload with relationships
    db_alert = db.query(StockAlert).options(
        joinedload(StockAlert.product),
        joinedload(StockAlert.location)
    ).filter(StockAlert.id == db_alert.id).first()
    
    return db_alert

@router.put("/alerts/{alert_id}", response_model=StockAlertSchema)
def update_stock_alert(alert_id: int, alert: StockAlertUpdate, db: Session = Depends(get_db)):
    """Update a stock alert"""
    db_alert = db.query(StockAlert).options(
        joinedload(StockAlert.product),
        joinedload(StockAlert.location)
    ).filter(StockAlert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Stock alert not found")
    
    for field, value in alert.dict(exclude_unset=True).items():
        setattr(db_alert, field, value)
    
    db_alert.updated_at = datetime.now()
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@router.delete("/alerts/{alert_id}")
def delete_stock_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete a stock alert"""
    db_alert = db.query(StockAlert).filter(StockAlert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Stock alert not found")
    
    db.delete(db_alert)
    db.commit()
    
    return {"message": "Stock alert deleted successfully"}

@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Acknowledge a stock alert"""
    db_alert = db.query(StockAlert).filter(StockAlert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Stock alert not found")
    
    db_alert.acknowledged_by = current_user.id
    db_alert.acknowledged_at = datetime.now()
    db_alert.updated_at = datetime.now()
    db.commit()
    db.refresh(db_alert)
    
    return {"message": "Alert acknowledged successfully"}

@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Resolve a stock alert"""
    db_alert = db.query(StockAlert).filter(StockAlert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Stock alert not found")
    
    db_alert.status = AlertStatus.RESOLVED
    db_alert.resolved_by = current_user.id
    db_alert.resolved_at = datetime.now()
    db_alert.updated_at = datetime.now()
    db.commit()
    db.refresh(db_alert)
    
    return {"message": "Alert resolved successfully"}

# Alert Rules endpoints
@router.get("/rules", response_model=AlertRuleList)
def get_alert_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    alert_type: Optional[AlertType] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> Any:
    """Get all alert rules with optional filtering and pagination"""
    query = db.query(AlertRule)
    
    if alert_type:
        query = query.filter(AlertRule.alert_type == alert_type)
    
    if is_active is not None:
        query = query.filter(AlertRule.is_active == is_active)
    
    total = query.count()
    rules = query.order_by(AlertRule.created_at.desc()).offset(skip).limit(limit).all()
    
    return AlertRuleList(
        rules=rules,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.post("/rules", response_model=AlertRuleSchema)
def create_alert_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    """Create a new alert rule"""
    db_rule = AlertRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    return db_rule

@router.put("/rules/{rule_id}", response_model=AlertRuleSchema)
def update_alert_rule(rule_id: int, rule: AlertRuleUpdate, db: Session = Depends(get_db)):
    """Update an alert rule"""
    db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    for field, value in rule.dict(exclude_unset=True).items():
        setattr(db_rule, field, value)
    
    db_rule.updated_at = datetime.now()
    db.commit()
    db.refresh(db_rule)
    
    return db_rule

@router.delete("/rules/{rule_id}")
def delete_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete an alert rule"""
    db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    db.delete(db_rule)
    db.commit()
    
    return {"message": "Alert rule deleted successfully"}

# Manual trigger endpoints
@router.post("/check-alerts")
async def check_stock_alerts(db: Session = Depends(get_db)):
    """Manually trigger stock alert check"""
    try:
        from app.core.background_tasks import background_task_manager
        await background_task_manager._check_stock_alerts()
        return {"message": "Stock alert check completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking stock alerts: {str(e)}")

# WebSocket endpoint for real-time alerts
@router.websocket("/ws/alerts/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    try:
        from app.core.websocket import manager
        await manager.connect(websocket, user_id)
        
        while True:
            # Keep connection alive
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        try:
            from app.core.websocket import manager
            manager.disconnect(user_id)
        except:
            pass
    except Exception as e:
        logging.error(f"WebSocket error: {e}")

# Background task management
@router.get("/background-task/status")
def get_background_task_status():
    """Get background task status"""
    try:
        from app.core.background_tasks import background_task_manager
        return {
            "is_running": background_task_manager.is_running,
            "check_interval": background_task_manager.check_interval
        }
    except Exception as e:
        return {"error": f"Could not get background task status: {str(e)}"}

@router.post("/background-task/trigger")
async def trigger_immediate_check():
    """Trigger immediate background task check"""
    try:
        from app.core.background_tasks import background_task_manager
        await background_task_manager._check_stock_alerts()
        return {"message": "Immediate check triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering check: {str(e)}")

# Utility endpoints
@router.post("/cleanup-duplicates")
def cleanup_duplicate_alerts(db: Session = Depends(get_db)):
    """Clean up duplicate stock alerts"""
    try:
        # Find and remove duplicate alerts
        duplicates = db.query(StockAlert).filter(
            and_(
                StockAlert.status == AlertStatus.ACTIVE,
                StockAlert.created_at < datetime.now() - timedelta(hours=1)
            )
        ).all()
        
        # Group by product, location, and alert type
        seen = set()
        to_delete = []
        
        for alert in duplicates:
            key = (alert.product_id, alert.location_id, alert.alert_type)
            if key in seen:
                to_delete.append(alert)
            else:
                seen.add(key)
        
        # Delete duplicates
        for alert in to_delete:
            db.delete(alert)
        
        db.commit()
        
        return {
            "message": f"Cleaned up {len(to_delete)} duplicate alerts",
            "deleted_count": len(to_delete)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up duplicates: {str(e)}")

@router.get("/stats")
def get_alert_stats(db: Session = Depends(get_db)):
    """Get stock alert statistics"""
    try:
        total_alerts = db.query(StockAlert).count()
        active_alerts = db.query(StockAlert).filter(StockAlert.status == AlertStatus.ACTIVE).count()
        resolved_alerts = db.query(StockAlert).filter(StockAlert.status == AlertStatus.RESOLVED).count()
        
        # Alerts by type
        low_stock_alerts = db.query(StockAlert).filter(
            and_(
                StockAlert.alert_type == AlertType.LOW_STOCK,
                StockAlert.status == AlertStatus.ACTIVE
            )
        ).count()
        
        out_of_stock_alerts = db.query(StockAlert).filter(
            and_(
                StockAlert.alert_type == AlertType.OUT_OF_STOCK,
                StockAlert.status == AlertStatus.ACTIVE
            )
        ).count()
        
        overstock_alerts = db.query(StockAlert).filter(
            and_(
                StockAlert.alert_type == AlertType.OVERSTOCK,
                StockAlert.status == AlertStatus.ACTIVE
            )
        ).count()
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "by_type": {
                "low_stock": low_stock_alerts,
                "out_of_stock": out_of_stock_alerts,
                "overstock": overstock_alerts
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}") 