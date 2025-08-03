from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.websocket import manager
from app.models.stock_alert import StockAlert, AlertType, AlertStatus
from datetime import datetime

router = APIRouter()

@router.post("/test-notification")
async def test_websocket_notification(db: Session = Depends(get_db)):
    """Test endpoint to send a WebSocket notification"""
    
    # Create a test alert data
    test_alert_data = {
        "id": 999,
        "product_id": 1,
        "location_id": 1,
        "alert_type": "low_stock",
        "message": "TEST: Low stock alert for testing WebSocket notifications",
        "current_quantity": 5,
        "threshold_quantity": 10,
        "status": "active"
    }
    
    try:
        # Send the test notification
        await manager.send_alert(test_alert_data)
        return {
            "message": "Test notification sent successfully",
            "alert_data": test_alert_data
        }
    except Exception as e:
        return {
            "message": f"Failed to send test notification: {str(e)}",
            "alert_data": test_alert_data
        }

@router.post("/test-notification-user/{user_id}")
async def test_websocket_notification_user(user_id: int, db: Session = Depends(get_db)):
    """Test endpoint to send a WebSocket notification to a specific user"""
    
    # Create a test alert data
    test_alert_data = {
        "id": 999,
        "product_id": 1,
        "location_id": 1,
        "alert_type": "low_stock",
        "message": f"TEST: Low stock alert for user {user_id}",
        "current_quantity": 5,
        "threshold_quantity": 10,
        "status": "active"
    }
    
    try:
        # Send the test notification to specific user
        await manager.send_alert(test_alert_data, user_id)
        return {
            "message": f"Test notification sent successfully to user {user_id}",
            "alert_data": test_alert_data
        }
    except Exception as e:
        return {
            "message": f"Failed to send test notification: {str(e)}",
            "alert_data": test_alert_data
        } 