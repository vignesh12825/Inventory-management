from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, products, categories, inventory, suppliers, locations, purchase_orders, stock_alerts, websocket, test_websocket

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["purchase-orders"])
api_router.include_router(stock_alerts.router, prefix="/stock-alerts", tags=["stock-alerts"])
api_router.include_router(websocket.router, tags=["websocket"])
api_router.include_router(test_websocket.router, prefix="/test", tags=["test"]) 