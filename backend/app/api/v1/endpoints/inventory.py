from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.inventory import Inventory, StockMovement, StockMovementType
from app.models.product import Product
from app.models.user import User
from app.schemas.inventory import InventoryCreate, InventoryUpdate, Inventory as InventorySchema, StockMovementCreate, StockMovement as StockMovementSchema, StockAdjustmentRequest
from app.schemas.common import PaginatedResponse

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[InventorySchema])
def read_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    product_id: int = None,
    location_id: int = None,
) -> Any:
    """
    Retrieve inventory items with optional filtering.
    """
    query = db.query(Inventory)
    
    if product_id:
        query = query.filter(Inventory.product_id == product_id)
    if location_id:
        query = query.filter(Inventory.location_id == location_id)
    
    total = query.count()
    inventory_items = query.offset(skip).limit(limit).all()
    
    return PaginatedResponse(
        data=inventory_items,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.post("/", response_model=InventorySchema)
def create_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    inventory_in: InventoryCreate,
) -> Any:
    """
    Create new inventory item.
    """
    # Check if inventory item already exists for this product and location
    existing_item = db.query(Inventory).filter(
        Inventory.product_id == inventory_in.product_id,
        Inventory.location_id == inventory_in.location_id
    ).first()
    
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory item already exists for this product and location"
        )
    
    inventory_item = Inventory(**inventory_in.dict())
    db.add(inventory_item)
    db.commit()
    db.refresh(inventory_item)
    return inventory_item

@router.get("/{inventory_id}", response_model=InventorySchema)
def read_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    inventory_id: int,
) -> Any:
    """
    Get inventory item by ID.
    """
    inventory_item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    return inventory_item

@router.put("/{inventory_id}", response_model=InventorySchema)
async def update_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    inventory_id: int,
    inventory_in: InventoryUpdate,
) -> Any:
    """
    Update inventory item.
    """
    inventory_item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    update_data = inventory_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(inventory_item, field, value)
    
    # Update available quantity
    inventory_item.available_quantity = inventory_item.quantity - inventory_item.reserved_quantity
    
    db.add(inventory_item)
    db.commit()
    db.refresh(inventory_item)
    return inventory_item

@router.delete("/{inventory_id}")
def delete_inventory_item(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    inventory_id: int,
) -> Any:
    """
    Delete inventory item.
    """
    inventory_item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    try:
        # Check if there are any stock movements for this inventory item
        stock_movements = db.query(StockMovement).filter(
            StockMovement.inventory_item_id == inventory_id
        ).count()
        
        if stock_movements > 0:
            # Delete associated stock movements first
            db.query(StockMovement).filter(
                StockMovement.inventory_item_id == inventory_id
            ).delete()
            
        db.delete(inventory_item)
        db.commit()
        return {"message": "Inventory item deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete inventory item: {str(e)}"
        )

@router.post("/{inventory_id}/stock-movement", response_model=StockMovementSchema)
def create_stock_movement(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    inventory_id: int,
    movement_in: StockMovementCreate,
) -> Any:
    """
    Create stock movement for inventory item.
    """
    inventory_item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    # Create stock movement
    movement_data = movement_in.model_dump()
    movement_data["movement_type"] = StockMovementType(movement_data["movement_type"])
    stock_movement = StockMovement(
        inventory_item_id=inventory_id,
        created_by=current_user.id,
        **movement_data
    )
    db.add(stock_movement)
    
    # Update inventory quantities based on movement type
    if movement_in.movement_type == "in":
        inventory_item.quantity += movement_in.quantity
    elif movement_in.movement_type == "out":
        if inventory_item.quantity < movement_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock for this movement"
            )
        inventory_item.quantity -= movement_in.quantity
    elif movement_in.movement_type == "transfer":
        if inventory_item.quantity < movement_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock for this transfer"
            )
        inventory_item.quantity -= movement_in.quantity
    
    # Update available quantity
    inventory_item.available_quantity = inventory_item.quantity - inventory_item.reserved_quantity
    inventory_item.last_restocked = datetime.utcnow()
    
    db.add(inventory_item)
    db.commit()
    db.refresh(stock_movement)
    return stock_movement

@router.get("/{inventory_id}/stock-movements", response_model=List[StockMovementSchema])
def get_stock_movements(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    inventory_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get stock movements for an inventory item.
    """
    inventory_item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    movements = db.query(StockMovement).filter(
        StockMovement.inventory_item_id == inventory_id
    ).order_by(StockMovement.created_at.desc()).offset(skip).limit(limit).all()
    
    return movements

@router.post("/{inventory_id}/adjust-stock")
def adjust_stock(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    inventory_id: int,
    adjustment: StockAdjustmentRequest,
) -> Any:
    """
    Manually adjust stock quantity (add or reduce).
    """
    inventory_item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    # Create stock movement for adjustment
    movement_type = StockMovementType.IN if adjustment.quantity_change > 0 else StockMovementType.OUT
    stock_movement = StockMovement(
        inventory_item_id=inventory_id,
        created_by=current_user.id,
        movement_type=movement_type,
        quantity=abs(adjustment.quantity_change),
        reference_type="adjustment",
        notes=adjustment.notes or f"Manual stock adjustment: {adjustment.quantity_change:+d}"
    )
    db.add(stock_movement)
    
    # Update inventory quantity
    inventory_item.quantity += adjustment.quantity_change
    if inventory_item.quantity < 0:
        inventory_item.quantity = 0
    
    # Update available quantity
    inventory_item.available_quantity = inventory_item.quantity - inventory_item.reserved_quantity
    
    db.add(inventory_item)
    db.commit()
    
    return {
        "message": f"Stock adjusted by {adjustment.quantity_change:+d}",
        "new_quantity": inventory_item.quantity,
        "available_quantity": inventory_item.available_quantity
    }

@router.get("/low-stock", response_model=List[InventorySchema])
def get_low_stock_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get inventory items with low stock (below reorder point).
    """
    low_stock_items = db.query(Inventory).join(
        Product, Inventory.product_id == Product.id
    ).filter(
        Inventory.quantity <= Product.reorder_point
    ).offset(skip).limit(limit).all()
    
    return low_stock_items

@router.get("/out-of-stock", response_model=List[InventorySchema])
def get_out_of_stock_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get inventory items that are out of stock.
    """
    out_of_stock_items = db.query(Inventory).filter(
        Inventory.quantity == 0
    ).offset(skip).limit(limit).all()
    
    return out_of_stock_items 