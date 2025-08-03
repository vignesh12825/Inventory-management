from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime, date
import random
import string

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.purchase_order import PurchaseOrder as PurchaseOrderModel, PurchaseOrderItem as PurchaseOrderItemModel, PurchaseOrderStatus
from app.models.supplier import Supplier as SupplierModel
from app.models.product import Product as ProductModel
from app.models.inventory import Inventory, StockMovement, StockMovementType
from app.schemas.purchase_order import PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderUpdateWithItems, PurchaseOrderItem, PurchaseOrderItemCreate, PurchaseOrderItemUpdate
from app.schemas.common import PaginatedResponse

router = APIRouter()

def generate_po_number():
    """Generate a unique PO number"""
    prefix = "PO"
    year = datetime.now().year
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{year}{random_suffix}"

@router.get("/", response_model=PaginatedResponse[PurchaseOrder])
def get_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[PurchaseOrderStatus] = None,
    supplier_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get all purchase orders with optional filtering and pagination"""
    query = db.query(PurchaseOrderModel).options(
        joinedload(PurchaseOrderModel.supplier),
        joinedload(PurchaseOrderModel.items).joinedload(PurchaseOrderItemModel.product)
    )
    
    # Role-based filtering
    if not current_user.has_permission("view_all_po"):
        # Staff can only see POs they created
        query = query.filter(PurchaseOrderModel.created_by == current_user.id)
    
    if status:
        query = query.filter(PurchaseOrderModel.status == status)
    
    if supplier_id:
        query = query.filter(PurchaseOrderModel.supplier_id == supplier_id)
    
    if start_date:
        query = query.filter(PurchaseOrderModel.order_date >= start_date)
    
    if end_date:
        query = query.filter(PurchaseOrderModel.order_date <= end_date)
    
    total = query.count()
    purchase_orders = query.offset(skip).limit(limit).all()
    
    return PaginatedResponse(
        data=purchase_orders,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.post("/", response_model=PurchaseOrder)
def create_purchase_order(
    purchase_order: PurchaseOrderCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new purchase order"""
    if not current_user.has_permission("create_po"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create purchase orders"
        )
    
    # Validate supplier exists
    supplier = db.query(SupplierModel).filter(SupplierModel.id == purchase_order.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Validate products exist
    for item in purchase_order.items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")
    
    # Create purchase order
    po_data = purchase_order.dict(exclude={'items'})
    po_data['po_number'] = generate_po_number()
    po_data['created_by'] = current_user.id
    
    db_po = PurchaseOrderModel(**po_data)
    db.add(db_po)
    db.flush()  # Get the ID without committing
    
    # Calculate totals
    subtotal = 0
    
    # Create purchase order items
    for item_data in purchase_order.items:
        item_data_dict = item_data.dict()
        item_data_dict['purchase_order_id'] = db_po.id
        item_data_dict['total_price'] = item_data.quantity * item_data.unit_price
        subtotal += item_data_dict['total_price']
        
        db_item = PurchaseOrderItemModel(**item_data_dict)
        db.add(db_item)
    
    # Update totals
    db_po.subtotal = subtotal
    db_po.total_amount = subtotal + db_po.tax_amount + db_po.shipping_amount
    
    db.commit()
    db.refresh(db_po)
    return db_po

@router.get("/{po_id}", response_model=PurchaseOrder)
def get_purchase_order(
    po_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific purchase order"""
    db_po = db.query(PurchaseOrderModel).options(
        joinedload(PurchaseOrderModel.supplier),
        joinedload(PurchaseOrderModel.items).joinedload(PurchaseOrderItemModel.product)
    ).filter(PurchaseOrderModel.id == po_id).first()
    
    if not db_po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Check permissions
    if not current_user.has_permission("view_all_po") and db_po.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this purchase order"
        )
    
    return db_po

@router.put("/{po_id}", response_model=PurchaseOrder)
def update_purchase_order(
    po_id: int, 
    purchase_order: PurchaseOrderUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a purchase order"""
    db_po = db.query(PurchaseOrderModel).options(
        joinedload(PurchaseOrderModel.supplier),
        joinedload(PurchaseOrderModel.items).joinedload(PurchaseOrderItemModel.product)
    ).filter(PurchaseOrderModel.id == po_id).first()
    
    if not db_po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Check permissions
    if not current_user.has_permission("edit_po") and db_po.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this purchase order"
        )
    
    # Don't allow updates if already received
    if db_po.status in [PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Cannot update completed purchase order")
    
    update_data = purchase_order.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_po, field, value)
    
    # If status is being changed to approved, check permissions
    if purchase_order.status == PurchaseOrderStatus.APPROVED:
        if not current_user.can_approve_po():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to approve purchase orders"
            )
        db_po.approved_by = current_user.id
        db_po.approved_at = datetime.now()
    
    # Recalculate total if tax_amount or shipping_amount changed
    if 'tax_amount' in update_data or 'shipping_amount' in update_data:
        db_po.total_amount = db_po.subtotal + db_po.tax_amount + db_po.shipping_amount
    
    db.commit()
    db.refresh(db_po)
    return db_po

@router.post("/{po_id}/status", response_model=PurchaseOrder)
def change_purchase_order_status(
    po_id: int, 
    status_data: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    new_status = status_data.get("new_status")
    if not new_status:
        raise HTTPException(status_code=422, detail="new_status is required")
    
    try:
        new_status = PurchaseOrderStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid status: {new_status}")
    """Change purchase order status"""
    db_po = db.query(PurchaseOrderModel).filter(PurchaseOrderModel.id == po_id).first()
    if not db_po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Check permissions based on status change
    if new_status == PurchaseOrderStatus.APPROVED:
        if not current_user.can_approve_po():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to approve purchase orders"
            )
    elif new_status == PurchaseOrderStatus.CANCELLED:
        if not current_user.can_cancel_po():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to cancel purchase orders"
            )
    
    # Validate status transitions
    valid_transitions = {
        PurchaseOrderStatus.DRAFT: [PurchaseOrderStatus.PENDING_APPROVAL, PurchaseOrderStatus.CANCELLED],
        PurchaseOrderStatus.PENDING_APPROVAL: [PurchaseOrderStatus.APPROVED, PurchaseOrderStatus.CANCELLED],
        PurchaseOrderStatus.APPROVED: [PurchaseOrderStatus.ORDERED, PurchaseOrderStatus.CANCELLED],
        PurchaseOrderStatus.ORDERED: [PurchaseOrderStatus.PARTIALLY_RECEIVED, PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.CANCELLED],
        PurchaseOrderStatus.PARTIALLY_RECEIVED: [PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.CANCELLED],
        PurchaseOrderStatus.RECEIVED: [],  # Final state
        PurchaseOrderStatus.CANCELLED: []  # Final state
    }
    
    if new_status not in valid_transitions.get(db_po.status, []):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status transition from {db_po.status} to {new_status}"
        )
    
    # Handle specific status changes
    if new_status == PurchaseOrderStatus.APPROVED:
        db_po.approved_by = current_user.id
        db_po.approved_at = datetime.now()
    elif new_status == PurchaseOrderStatus.ORDERED:
        db_po.order_date = datetime.now().date()
    
    db_po.status = new_status
    db.commit()
    db.refresh(db_po)
    return db_po

@router.put("/{po_id}/with-items", response_model=PurchaseOrder)
def update_purchase_order_with_items(
    po_id: int, 
    purchase_order: PurchaseOrderUpdateWithItems, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a purchase order including items"""
    db_po = db.query(PurchaseOrderModel).options(
        joinedload(PurchaseOrderModel.supplier),
        joinedload(PurchaseOrderModel.items).joinedload(PurchaseOrderItemModel.product)
    ).filter(PurchaseOrderModel.id == po_id).first()
    
    if not db_po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Check permissions
    if not current_user.has_permission("edit_po") and db_po.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this purchase order"
        )
    
    # Don't allow updates if already received
    if db_po.status in [PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Cannot update completed purchase order")
    
    # Validate supplier exists
    if purchase_order.supplier_id:
        supplier = db.query(SupplierModel).filter(SupplierModel.id == purchase_order.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Validate products exist
    for item in purchase_order.items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")
    
    # Update basic fields
    update_data = purchase_order.dict(exclude={'items'}, exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_po, field, value)
    
    # Clear existing items and recalculate totals
    db.query(PurchaseOrderItemModel).filter(PurchaseOrderItemModel.purchase_order_id == po_id).delete()
    
    # Calculate new totals
    subtotal = 0
    
    # Create new items
    for item_data in purchase_order.items:
        item_data_dict = item_data.dict()
        item_data_dict['purchase_order_id'] = po_id
        item_data_dict['total_price'] = item_data.quantity * item_data.unit_price
        subtotal += item_data_dict['total_price']
        
        db_item = PurchaseOrderItemModel(**item_data_dict)
        db.add(db_item)
    
    # Update totals
    db_po.subtotal = subtotal
    db_po.total_amount = subtotal + db_po.tax_amount + db_po.shipping_amount
    
    db.commit()
    db.refresh(db_po)
    return db_po

@router.post("/{po_id}/receive", response_model=PurchaseOrder)
def receive_purchase_order(
    po_id: int, 
    received_items: List[dict],  # List of {item_id: int, received_quantity: int}
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Receive items from a purchase order"""
    if not current_user.can_receive_po():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to receive purchase orders"
        )
    
    db_po = db.query(PurchaseOrderModel).options(
        joinedload(PurchaseOrderModel.supplier),
        joinedload(PurchaseOrderModel.items).joinedload(PurchaseOrderItemModel.product)
    ).filter(PurchaseOrderModel.id == po_id).first()
    
    if not db_po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    if db_po.status in [PurchaseOrderStatus.DRAFT, PurchaseOrderStatus.PENDING_APPROVAL, PurchaseOrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Cannot receive items from this purchase order status")
    
    all_received = True
    
    for received_item in received_items:
        item_id = received_item.get('item_id')
        received_quantity = received_item.get('received_quantity', 0)
        
        if received_quantity <= 0:
            continue
            
        # Find the purchase order item
        po_item = db.query(PurchaseOrderItemModel).filter(
            and_(PurchaseOrderItemModel.id == item_id, PurchaseOrderItemModel.purchase_order_id == po_id)
        ).first()
        
        if not po_item:
            raise HTTPException(status_code=404, detail=f"Purchase order item {item_id} not found")
        
        # Check if we're not exceeding the ordered quantity
        total_received = po_item.received_quantity + received_quantity
        if total_received > po_item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot receive more than ordered quantity for item {item_id}"
            )
        
        # Update received quantity
        po_item.received_quantity = total_received
        
        # Update inventory
        inventory_item = db.query(Inventory).filter(
            and_(Inventory.product_id == po_item.product_id, Inventory.location_id == location_id)
        ).first()
        
        if not inventory_item:
            # Create new inventory item
            inventory_item = Inventory(
                product_id=po_item.product_id,
                location_id=location_id,
                quantity=received_quantity,
                unit_cost=po_item.unit_price
            )
            db.add(inventory_item)
        else:
            # Update existing inventory
            inventory_item.quantity += received_quantity
            inventory_item.available_quantity = inventory_item.quantity - inventory_item.reserved_quantity
            inventory_item.last_restocked = datetime.now()
        
        # Create stock movement record
        stock_movement = StockMovement(
            inventory_item_id=inventory_item.id,
            movement_type=StockMovementType.IN,
            quantity=received_quantity,
            reference_type="purchase_order",
            reference_id=po_id,
            unit_cost=po_item.unit_price,
            notes=f"Received from PO {db_po.po_number} by {current_user.username}"
        )
        db.add(stock_movement)
        
        # Check if all items are received
        if po_item.received_quantity < po_item.quantity:
            all_received = False
    
    # Update purchase order status
    if all_received:
        db_po.status = PurchaseOrderStatus.RECEIVED
        db_po.delivery_date = datetime.now().date()
    else:
        db_po.status = PurchaseOrderStatus.PARTIALLY_RECEIVED
    
    db.commit()
    db.refresh(db_po)
    return db_po

@router.post("/{po_id}/items", response_model=PurchaseOrderItem)
def add_purchase_order_item(
    po_id: int, 
    item: PurchaseOrderItemCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add an item to a purchase order"""
    purchase_order = db.query(PurchaseOrderModel).filter(PurchaseOrderModel.id == po_id).first()
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Check permissions
    if not current_user.has_permission("edit_po") and purchase_order.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this purchase order"
        )
    
    # Validate product exists
    product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    item_data = item.dict()
    item_data['purchase_order_id'] = po_id
    item_data['total_price'] = item.quantity * item.unit_price
    
    db_item = PurchaseOrderItemModel(**item_data)
    db.add(db_item)
    
    # Update purchase order totals
    purchase_order.subtotal += item_data['total_price']
    purchase_order.total_amount = purchase_order.subtotal + purchase_order.tax_amount + purchase_order.shipping_amount
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{po_id}/items/{item_id}", response_model=PurchaseOrderItem)
def update_purchase_order_item(
    po_id: int, 
    item_id: int, 
    item: PurchaseOrderItemUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a purchase order item"""
    db_item = db.query(PurchaseOrderItemModel).filter(
        and_(PurchaseOrderItemModel.id == item_id, PurchaseOrderItemModel.purchase_order_id == po_id)
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Purchase order item not found")
    
    # Check permissions
    purchase_order = db.query(PurchaseOrderModel).filter(PurchaseOrderModel.id == po_id).first()
    if not current_user.has_permission("edit_po") and purchase_order.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this purchase order"
        )
    
    # Calculate old total for adjustment
    old_total = db_item.total_price
    
    update_data = item.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    # Recalculate total price
    if 'quantity' in update_data or 'unit_price' in update_data:
        db_item.total_price = db_item.quantity * db_item.unit_price
    
    # Update purchase order totals
    purchase_order.subtotal = purchase_order.subtotal - old_total + db_item.total_price
    purchase_order.total_amount = purchase_order.subtotal + purchase_order.tax_amount + purchase_order.shipping_amount
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.post("/{po_id}/cancel")
def cancel_purchase_order(
    po_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a purchase order"""
    if not current_user.can_cancel_po():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to cancel purchase orders"
        )
    
    purchase_order = db.query(PurchaseOrderModel).filter(PurchaseOrderModel.id == po_id).first()
    if not purchase_order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    if purchase_order.status in [PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Purchase order cannot be cancelled")
    
    purchase_order.status = PurchaseOrderStatus.CANCELLED
    db.commit()
    return {"message": "Purchase order cancelled successfully"} 