from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.stock_alert import (
    StockAlert, StockAlertCreate, StockAlertUpdate,
    AlertRule, AlertRuleCreate, AlertRuleUpdate,
    AlertType, AlertStatus
)
from app.schemas.common import PaginatedResponse
from app.models.stock_alert import (
    StockAlert as StockAlertModel, 
    AlertRule as AlertRuleModel
)
from app.models.product import Product as ProductModel
from app.models.inventory import Inventory as InventoryModel
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from datetime import datetime

router = APIRouter()

@router.get("/alerts", response_model=PaginatedResponse[StockAlert])
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
    query = db.query(StockAlertModel).options(
        joinedload(StockAlertModel.product),
        joinedload(StockAlertModel.location)
    )
    
    if status:
        query = query.filter(StockAlertModel.status == status)
    
    if alert_type:
        query = query.filter(StockAlertModel.alert_type == alert_type)
    
    if product_id:
        query = query.filter(StockAlertModel.product_id == product_id)
    
    if location_id:
        query = query.filter(StockAlertModel.location_id == location_id)
    
    total = query.count()
    alerts = query.order_by(StockAlertModel.created_at.desc()).offset(skip).limit(limit).all()
    
    return PaginatedResponse(
        data=alerts,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/alerts/active", response_model=List[StockAlert])
def get_active_alerts(db: Session = Depends(get_db)):
    """Get all active stock alerts"""
    alerts = db.query(StockAlertModel).options(
        joinedload(StockAlertModel.product),
        joinedload(StockAlertModel.location)
    ).filter(
        StockAlertModel.status == AlertStatus.ACTIVE
    ).order_by(StockAlertModel.created_at.desc()).all()
    return alerts

@router.post("/alerts", response_model=StockAlert)
async def create_stock_alert(alert: StockAlertCreate, db: Session = Depends(get_db)):
    """Create a new stock alert"""
    # Validate product exists
    product = db.query(ProductModel).filter(ProductModel.id == alert.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if similar alert already exists
    existing_alert = db.query(StockAlertModel).filter(
        and_(
            StockAlertModel.product_id == alert.product_id,
            StockAlertModel.location_id == alert.location_id,
            StockAlertModel.alert_type == alert.alert_type,
            StockAlertModel.status == AlertStatus.ACTIVE
        )
    ).first()
    
    if existing_alert:
        # Update the existing alert instead of creating a new one
        existing_alert.current_quantity = alert.current_quantity
        existing_alert.threshold_quantity = alert.threshold_quantity
        existing_alert.message = alert.message
        existing_alert.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_alert)
        return existing_alert
    
    db_alert = StockAlertModel(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    # Send WebSocket notification
    try:
        from app.core.websocket import manager
        alert_data = {
            "id": db_alert.id,
            "product_id": db_alert.product_id,
            "location_id": db_alert.location_id,
            "alert_type": db_alert.alert_type.value,
            "message": db_alert.message,
            "current_quantity": db_alert.current_quantity,
            "threshold_quantity": db_alert.threshold_quantity,
            "status": db_alert.status.value
        }
        await manager.send_alert(alert_data)
    except Exception as e:
        # Log error but don't fail the alert creation
        print(f"Failed to send WebSocket notification: {e}")
    
    # Reload with relationships
    db_alert = db.query(StockAlertModel).options(
        joinedload(StockAlertModel.product),
        joinedload(StockAlertModel.location)
    ).filter(StockAlertModel.id == db_alert.id).first()
    
    return db_alert

@router.put("/alerts/{alert_id}", response_model=StockAlert)
def update_stock_alert(alert_id: int, alert: StockAlertUpdate, db: Session = Depends(get_db)):
    """Update a stock alert"""
    db_alert = db.query(StockAlertModel).options(
        joinedload(StockAlertModel.product),
        joinedload(StockAlertModel.location)
    ).filter(StockAlertModel.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Stock alert not found")
    
    update_data = alert.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_alert, field, value)
    
    # Set timestamps for status changes
    if alert.status == AlertStatus.ACKNOWLEDGED and not db_alert.acknowledged_at:
        db_alert.acknowledged_at = datetime.now()
    elif alert.status == AlertStatus.RESOLVED and not db_alert.resolved_at:
        db_alert.resolved_at = datetime.now()
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/rules", response_model=PaginatedResponse[AlertRule])
def get_alert_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    alert_type: Optional[AlertType] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> Any:
    """Get all alert rules with optional filtering and pagination"""
    query = db.query(AlertRuleModel)
    
    if alert_type:
        query = query.filter(AlertRuleModel.alert_type == alert_type)
    
    if is_active is not None:
        query = query.filter(AlertRuleModel.is_active == is_active)
    
    total = query.count()
    rules = query.offset(skip).limit(limit).all()
    
    return PaginatedResponse(
        data=rules,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.post("/rules", response_model=AlertRule)
def create_alert_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    """Create a new alert rule"""
    # Validate product exists if specified
    if rule.product_id:
        product = db.query(ProductModel).filter(ProductModel.id == rule.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    rule_data = rule.dict()
    rule_data['created_by'] = 1  # TODO: Get from current user
    
    db_rule = AlertRuleModel(**rule_data)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.put("/rules/{rule_id}", response_model=AlertRule)
def update_alert_rule(rule_id: int, rule: AlertRuleUpdate, db: Session = Depends(get_db)):
    """Update an alert rule"""
    db_rule = db.query(AlertRuleModel).filter(AlertRuleModel.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    update_data = rule.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rule, field, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.delete("/rules/{rule_id}")
def delete_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete an alert rule (soft delete by setting is_active to False)"""
    rule = db.query(AlertRuleModel).filter(AlertRuleModel.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    rule.is_active = False
    db.commit()
    return {"message": "Alert rule deactivated successfully"}

@router.post("/check-alerts")
async def check_stock_alerts(db: Session = Depends(get_db)):
    """Manually trigger stock alert checking"""
    # Get all active alert rules
    rules = db.query(AlertRule).filter(AlertRule.is_active == True).all()
    
    alerts_created = 0
    alerts_updated = 0
    
    for rule in rules:
        # Build query based on rule criteria
        query = db.query(Inventory).join(Product)
        
        if rule.product_id:
            query = query.filter(Inventory.product_id == rule.product_id)
        
        if rule.location_id:
            query = query.filter(Inventory.location_id == rule.location_id)
        
        inventory_items = query.all()
        
        for item in inventory_items:
            # Check if alert should be triggered
            should_alert = False
            alert_type = None
            message = ""
            
            if rule.alert_type == AlertType.LOW_STOCK:
                if item.available_quantity <= rule.threshold_quantity:
                    should_alert = True
                    alert_type = AlertType.LOW_STOCK
                    message = f"Low stock alert: {item.product.name} has {item.available_quantity} units available (threshold: {rule.threshold_quantity})"
            
            elif rule.alert_type == AlertType.OUT_OF_STOCK:
                if item.available_quantity == 0:
                    should_alert = True
                    alert_type = AlertType.OUT_OF_STOCK
                    message = f"Out of stock alert: {item.product.name} is out of stock"
            
            elif rule.alert_type == AlertType.OVERSTOCK:
                if rule.threshold_percentage and item.product.max_stock_level:
                    max_threshold = item.product.max_stock_level * (rule.threshold_percentage / 100)
                    if item.available_quantity > max_threshold:
                        should_alert = True
                        alert_type = AlertType.OVERSTOCK
                        message = f"Overstock alert: {item.product.name} has {item.available_quantity} units (over {rule.threshold_percentage}% of max)"
            
            if should_alert:
                # Check if alert already exists for this product/location/type (any status)
                existing_alert = db.query(StockAlert).filter(
                    and_(
                        StockAlert.product_id == item.product_id,
                        StockAlert.location_id == item.location_id,
                        StockAlert.alert_type == alert_type
                    )
                ).order_by(StockAlert.created_at.desc()).first()
                
                if not existing_alert:
                    # Create new alert only if no alert has ever existed for this combination
                    new_alert = StockAlert(
                        product_id=item.product_id,
                        location_id=item.location_id,
                        alert_type=alert_type,
                        current_quantity=item.available_quantity,
                        threshold_quantity=rule.threshold_quantity,
                        message=message
                    )
                    db.add(new_alert)
                    alerts_created += 1
                    
                    # Send WebSocket notification for new alert
                    try:
                        from app.core.websocket import manager
                        alert_data = {
                            "id": new_alert.id,
                            "product_id": new_alert.product_id,
                            "location_id": new_alert.location_id,
                            "alert_type": new_alert.alert_type.value,
                            "message": new_alert.message,
                            "current_quantity": new_alert.current_quantity,
                            "threshold_quantity": new_alert.threshold_quantity,
                            "status": new_alert.status.value
                        }
                        await manager.send_alert(alert_data)
                    except Exception as e:
                        print(f"Failed to send WebSocket notification: {e}")
                        
                elif existing_alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
                    # Update existing active/acknowledged alert to reflect current quantity
                    existing_alert.current_quantity = item.available_quantity
                    existing_alert.message = message
                    existing_alert.updated_at = datetime.now()
                    alerts_updated += 1
                elif existing_alert.status in [AlertStatus.RESOLVED, AlertStatus.DISMISSED]:
                    # Reactivate resolved/dismissed alert if conditions still apply
                    existing_alert.status = AlertStatus.ACTIVE
                    existing_alert.current_quantity = item.available_quantity
                    existing_alert.message = message
                    existing_alert.acknowledged_at = None
                    existing_alert.resolved_at = None
                    existing_alert.updated_at = datetime.now()
                    alerts_updated += 1
    
    db.commit()
    return {"message": f"Stock alert check completed. {alerts_created} new alerts created, {alerts_updated} alerts updated."}

@router.get("/background-task/status")
def get_background_task_status():
    """Get the status of the background task manager"""
    from app.core.background_tasks import background_task_manager
    
    return {
        "is_running": background_task_manager.is_running,
        "check_interval_seconds": background_task_manager.check_interval,
        "check_interval_minutes": background_task_manager.check_interval / 60,
        "status": "running" if background_task_manager.is_running else "stopped"
    }

@router.post("/background-task/trigger")
async def trigger_immediate_check():
    """Trigger an immediate stock alert check"""
    from app.core.background_tasks import background_task_manager
    
    if not background_task_manager.is_running:
        raise HTTPException(status_code=400, detail="Background task manager is not running")
    
    # Trigger immediate check
    await background_task_manager._check_stock_alerts()
    return {"message": "Immediate stock alert check triggered successfully"}

@router.post("/cleanup-duplicates")
def cleanup_duplicate_alerts(db: Session = Depends(get_db)):
    """Clean up duplicate alerts by keeping only the most recent one for each product/location/type combination"""
    from sqlalchemy import func
    
    # Find duplicate alerts
    duplicates = db.query(
        StockAlertModel.product_id,
        StockAlertModel.location_id,
        StockAlertModel.alert_type,
        func.count(StockAlertModel.id).label('count')
    ).group_by(
        StockAlertModel.product_id,
        StockAlertModel.location_id,
        StockAlertModel.alert_type
    ).having(func.count(StockAlertModel.id) > 1).all()
    
    deleted_count = 0
    
    for duplicate in duplicates:
        # Get all alerts for this combination, ordered by creation date (newest first)
        alerts = db.query(StockAlertModel).filter(
            and_(
                StockAlertModel.product_id == duplicate.product_id,
                StockAlertModel.location_id == duplicate.location_id,
                StockAlertModel.alert_type == duplicate.alert_type
            )
        ).order_by(StockAlertModel.created_at.desc()).all()
        
        # Keep the most recent alert, delete the rest
        if len(alerts) > 1:
            for alert in alerts[1:]:  # Skip the first (most recent) one
                db.delete(alert)
                deleted_count += 1
    
    db.commit()
    return {"message": f"Cleanup completed. {deleted_count} duplicate alerts removed."} 