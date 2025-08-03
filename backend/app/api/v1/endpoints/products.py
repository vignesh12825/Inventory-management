from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.product import Product as ProductModel
from app.schemas.product import ProductCreate, ProductUpdate, Product
from app.schemas.common import PaginatedResponse
from app.models.purchase_order import PurchaseOrderStatus, PurchaseOrderItem, PurchaseOrder

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[Product])
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search in name, description, sku, brand, model"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    supplier_id: Optional[int] = Query(None, description="Filter by supplier ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
) -> Any:
    """
    Retrieve products with optional filtering.
    """
    try:
        query = db.query(ProductModel)
        
        # Apply search filter
        if search:
            search_filter = or_(
                ProductModel.name.ilike(f"%{search}%"),
                ProductModel.description.ilike(f"%{search}%"),
                ProductModel.sku.ilike(f"%{search}%"),
                ProductModel.brand.ilike(f"%{search}%"),
                ProductModel.model.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Apply category filter
        if category_id is not None:
            query = query.filter(ProductModel.category_id == category_id)
        
        # Apply supplier filter
        if supplier_id is not None:
            query = query.filter(ProductModel.supplier_id == supplier_id)
        
        # Apply active status filter
        if is_active is not None:
            query = query.filter(ProductModel.is_active == is_active)
        
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        
        return PaginatedResponse(
            data=products,
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    except Exception as e:
        print(f"Error in read_products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
) -> Any:
    """
    Create new product.
    """
    product = db.query(ProductModel).filter(ProductModel.sku == product_in.sku).first()
    if product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A product with this SKU already exists."
        )
    
    product = ProductModel(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/{product_id}", response_model=Product)
def read_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Get product by ID.
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.put("/{product_id}", response_model=Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
) -> Any:
    """
    Update product.
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    update_data = product_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Delete product.
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if product has related inventory items
    if product.inventory_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete product with existing inventory items. Please remove all inventory items first."
        )
    
    # Check if product has related purchase order items in ACTIVE POs only
    # Active POs are: draft, pending_approval, approved, ordered, partially_received
    # We allow deletion if POs are received or cancelled
    
    active_po_statuses = [
        PurchaseOrderStatus.DRAFT,
        PurchaseOrderStatus.PENDING_APPROVAL,
        PurchaseOrderStatus.APPROVED,
        PurchaseOrderStatus.ORDERED,
        PurchaseOrderStatus.PARTIALLY_RECEIVED
    ]
    
    # Check if any PO items are in active POs
    active_po_items = db.query(PurchaseOrderItem).join(PurchaseOrder).filter(
        PurchaseOrderItem.product_id == product_id,
        PurchaseOrder.status.in_(active_po_statuses)
    ).first()
    
    if active_po_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete product with items in active purchase orders. Please complete or cancel all active purchase orders first."
        )
    
    try:
        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error deleting product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product. Please try again."
        ) 