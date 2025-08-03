import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional

# Try to import database and models, but don't fail if they don't work
try:
    from app.core.database import get_db
    from app.models.stock_alert import StockAlert, AlertRule, AlertType, AlertStatus
    from app.models.inventory import Inventory
    from app.models.product import Product
    from app.core.websocket import manager
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import some modules in background_tasks: {e}")
    IMPORTS_SUCCESSFUL = False
    # Create dummy classes to prevent import errors
    class StockAlert:
        pass
    class AlertRule:
        pass
    class AlertType:
        LOW_STOCK = "LOW_STOCK"
        OUT_OF_STOCK = "OUT_OF_STOCK"
        OVERSTOCK = "OVERSTOCK"
    class AlertStatus:
        ACTIVE = "ACTIVE"
        RESOLVED = "RESOLVED"
    class Inventory:
        pass
    class Product:
        pass
    manager = None

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    def __init__(self):
        self.is_running = False
        self.check_interval = 60  # Check every 1 minute (60 seconds) for faster notifications
        self.task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the background task manager"""
        if not self.is_running and IMPORTS_SUCCESSFUL:
            self.is_running = True
            self.task = asyncio.create_task(self._run_periodic_checks())
            logger.info("Background task manager started")
        else:
            logger.warning("Background task manager not started - imports failed")
    
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
        if not IMPORTS_SUCCESSFUL:
            logger.warning("Skipping stock alert check - imports failed")
            return
            
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
                                StockAlert.alert_type == alert_type,
                                StockAlert.status == AlertStatus.ACTIVE
                            )
                        ).first()
                        
                        if existing_alert:
                            # Update existing alert
                            existing_alert.current_quantity = item.available_quantity
                            existing_alert.message = message
                            existing_alert.updated_at = datetime.now()
                            alerts_updated += 1
                        else:
                            # Create new alert
                            new_alert = StockAlert(
                                product_id=item.product_id,
                                location_id=item.location_id,
                                alert_type=alert_type,
                                status=AlertStatus.ACTIVE,
                                current_quantity=item.available_quantity,
                                threshold_quantity=rule.threshold_quantity,
                                message=message,
                                created_at=datetime.now(),
                                updated_at=datetime.now()
                            )
                            db.add(new_alert)
                            alerts_created += 1
                    
                    # Check for resolved alerts
                    active_alerts = db.query(StockAlert).filter(
                        and_(
                            StockAlert.product_id == item.product_id,
                            StockAlert.location_id == item.location_id,
                            StockAlert.status == AlertStatus.ACTIVE
                        )
                    ).all()
                    
                    for alert in active_alerts:
                        resolved = False
                        
                        if alert.alert_type == AlertType.LOW_STOCK:
                            if item.available_quantity > rule.threshold_quantity:
                                resolved = True
                        elif alert.alert_type == AlertType.OUT_OF_STOCK:
                            if item.available_quantity > 0:
                                resolved = True
                        elif alert.alert_type == AlertType.OVERSTOCK:
                            if rule.threshold_percentage and item.product.max_stock_level:
                                max_threshold = item.product.max_stock_level * (rule.threshold_percentage / 100)
                                if item.available_quantity <= max_threshold:
                                    resolved = True
                        
                        if resolved:
                            alert.status = AlertStatus.RESOLVED
                            alert.resolved_at = datetime.now()
                            alert.updated_at = datetime.now()
                            alerts_resolved += 1
            
            db.commit()
            
            if alerts_created > 0 or alerts_updated > 0 or alerts_resolved > 0:
                logger.info(f"Stock alerts processed: {alerts_created} created, {alerts_updated} updated, {alerts_resolved} resolved")
                
                # Send WebSocket notifications if manager is available
                if manager:
                    await manager.broadcast({
                        "type": "stock_alerts_updated",
                        "data": {
                            "alerts_created": alerts_created,
                            "alerts_updated": alerts_updated,
                            "alerts_resolved": alerts_resolved
                        }
                    })
                    
        except Exception as e:
            logger.error(f"Error checking stock alerts: {e}")
            # Don't re-raise the exception to prevent the background task from stopping

# Create a global instance
background_task_manager = BackgroundTaskManager() 