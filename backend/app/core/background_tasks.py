import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional

from app.core.database import get_db
from app.models.stock_alert import StockAlert as StockAlertModel, AlertRule as AlertRuleModel, AlertType, AlertStatus
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
            rules = db.query(AlertRuleModel).filter(AlertRuleModel.is_active == True).all()
            
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
                                message = f"Overstock alert: {item.product.name} has {item.available_quantity} units (over {rule.threshold_percentage}% of max)"
                    
                    # Check existing alerts for this product/location/type
                    existing_alert = db.query(StockAlertModel).filter(
                        and_(
                            StockAlertModel.product_id == item.product_id,
                            StockAlertModel.location_id == item.location_id,
                            StockAlertModel.alert_type == alert_type
                        )
                    ).order_by(StockAlertModel.created_at.desc()).first()
                    
                    if should_alert:
                        if not existing_alert:
                            # Create new alert only if no alert has ever existed for this combination
                            new_alert = StockAlertModel(
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
                                logger.info(f"Sent WebSocket notification for new alert: {new_alert.id}")
                            except Exception as e:
                                logger.error(f"Failed to send WebSocket notification: {e}")
                        
                        elif existing_alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
                            # Update existing active/acknowledged alert to reflect current quantity
                            existing_alert.current_quantity = item.available_quantity
                            existing_alert.message = message
                            existing_alert.updated_at = datetime.now()
                            alerts_updated += 1
                        
                        elif existing_alert.status in [AlertStatus.RESOLVED, AlertStatus.DISMISSED]:
                            # Only reactivate if the alert was previously resolved/dismissed AND conditions are still bad
                            # This prevents re-triggering of manually resolved alerts
                            # Only reactivate if the current quantity is worse than when it was resolved
                            if item.available_quantity < existing_alert.current_quantity:
                                existing_alert.status = AlertStatus.ACTIVE
                                existing_alert.current_quantity = item.available_quantity
                                existing_alert.message = message
                                existing_alert.acknowledged_at = None
                                existing_alert.resolved_at = None
                                existing_alert.updated_at = datetime.now()
                                alerts_updated += 1
                                
                                # Send WebSocket notification for reactivated alert
                                try:
                                    alert_data = {
                                        "id": existing_alert.id,
                                        "product_id": existing_alert.product_id,
                                        "location_id": existing_alert.location_id,
                                        "alert_type": existing_alert.alert_type.value,
                                        "message": existing_alert.message,
                                        "current_quantity": existing_alert.current_quantity,
                                        "threshold_quantity": existing_alert.threshold_quantity,
                                        "status": existing_alert.status.value
                                    }
                                    await manager.send_alert(alert_data)
                                    logger.info(f"Sent WebSocket notification for reactivated alert: {existing_alert.id}")
                                except Exception as e:
                                    logger.error(f"Failed to send WebSocket notification: {e}")
                    
                    else:
                        # Check if we need to resolve existing alerts (conditions no longer apply)
                        if existing_alert and existing_alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
                            # Conditions no longer apply, resolve the alert
                            existing_alert.status = AlertStatus.RESOLVED
                            existing_alert.resolved_at = datetime.now()
                            existing_alert.updated_at = datetime.now()
                            alerts_resolved += 1
                            
                            # Send WebSocket notification for resolved alert
                            try:
                                alert_data = {
                                    "id": existing_alert.id,
                                    "product_id": existing_alert.product_id,
                                    "location_id": existing_alert.location_id,
                                    "alert_type": existing_alert.alert_type.value,
                                    "message": f"Alert resolved: {item.product.name} stock level improved",
                                    "current_quantity": item.available_quantity,
                                    "threshold_quantity": existing_alert.threshold_quantity,
                                    "status": existing_alert.status.value
                                }
                                await manager.send_alert(alert_data)
                                logger.info(f"Sent WebSocket notification for resolved alert: {existing_alert.id}")
                            except Exception as e:
                                logger.error(f"Failed to send WebSocket notification: {e}")
            
            db.commit()
            
            if alerts_created > 0 or alerts_updated > 0 or alerts_resolved > 0:
                logger.info(f"Stock alert check completed. {alerts_created} new alerts created, {alerts_updated} alerts updated, {alerts_resolved} alerts resolved.")
            
        except Exception as e:
            logger.error(f"Error checking stock alerts: {e}")
            if 'db' in locals():
                db.rollback()

# Global background task manager instance
background_task_manager = BackgroundTaskManager() 