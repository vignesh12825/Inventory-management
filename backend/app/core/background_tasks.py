import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional

from app.core.database import get_db
from app.models.stock_alert import StockAlert, AlertRule, AlertType, AlertStatus
from app.models.inventory import Inventory
from app.models.product import Product
from app.core.websocket import manager

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    def __init__(self):
        self.is_running = False
        self.check_interval = 60  # Check every 1 minute (60 seconds) for faster notifications
        self.task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the background task manager"""
        if not self.is_running:
            self.is_running = True
            self.task = asyncio.create_task(self._run_periodic_checks())
            logger.info("Background task manager started")
    
    async def stop(self):
        """Stop the background task manager"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Background task manager stopped")
    
    async def _run_periodic_checks(self):
        """Run periodic stock alert checks"""
        while self.is_running:
            try:
                await self._check_stock_alerts()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic stock alert check: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _check_stock_alerts(self):
        """Check for stock alerts and send notifications"""
        try:
            # Get database session
            db = next(get_db())
            
            # Get all active alert rules
            rules = db.query(AlertRule).filter(AlertRule.is_active == True).all()
            
            alerts_created = 0
            alerts_updated = 0
            alerts_resolved = 0
            
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
                                message = f"Overstock alert: {item.product.name} has {item.available_quantity} units (threshold: {max_threshold})"
                    
                    if should_alert:
                        # Check if alert already exists
                        existing_alert = db.query(StockAlert).filter(
                            and_(
                                StockAlert.product_id == item.product_id,
                                StockAlert.location_id == item.location_id,
                                StockAlert.alert_type == alert_type
                            )
                        ).order_by(StockAlert.created_at.desc()).first()
                        
                        if not existing_alert:
                            # Create new alert
                            new_alert = StockAlert(
                                product_id=item.product_id,
                                location_id=item.location_id,
                                alert_type=alert_type,
                                current_quantity=item.available_quantity,
                                threshold_quantity=rule.threshold_quantity,
                                message=message,
                                status=AlertStatus.ACTIVE
                            )
                            db.add(new_alert)
                            alerts_created += 1
                            
                            # Send WebSocket notification
                            await manager.broadcast_alert(new_alert)
                        
                        elif existing_alert.status == AlertStatus.RESOLVED:
                            # Reactivate resolved alert
                            existing_alert.status = AlertStatus.ACTIVE
                            existing_alert.current_quantity = item.available_quantity
                            existing_alert.message = message
                            existing_alert.updated_at = datetime.utcnow()
                            alerts_updated += 1
                            
                            # Send WebSocket notification
                            await manager.broadcast_alert(existing_alert)
                    
                    else:
                        # Check if alert should be resolved
                        existing_alert = db.query(StockAlert).filter(
                            and_(
                                StockAlert.product_id == item.product_id,
                                StockAlert.location_id == item.location_id,
                                StockAlert.alert_type == alert_type,
                                StockAlert.status == AlertStatus.ACTIVE
                            )
                        ).first()
                        
                        if existing_alert:
                            # Resolve alert
                            existing_alert.status = AlertStatus.RESOLVED
                            existing_alert.resolved_at = datetime.utcnow()
                            existing_alert.updated_at = datetime.utcnow()
                            alerts_resolved += 1
            
            # Commit changes
            db.commit()
            
            if alerts_created > 0 or alerts_updated > 0 or alerts_resolved > 0:
                logger.info(f"Stock alerts processed: {alerts_created} created, {alerts_updated} updated, {alerts_resolved} resolved")
                
        except Exception as e:
            logger.error(f"Error checking stock alerts: {e}")
            if 'db' in locals():
                db.rollback()

# Global instance
background_task_manager = BackgroundTaskManager() 