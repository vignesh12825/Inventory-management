#!/usr/bin/env python3
"""
Check product and purchase order relationships
"""
from app.core.database import SessionLocal
from app.models.product import Product
from app.models.purchase_order import PurchaseOrderItem, PurchaseOrder, PurchaseOrderStatus

def check_relationships():
    db = SessionLocal()
    try:
        print("📋 Products:")
        products = db.query(Product).all()
        for p in products:
            print(f"  {p.id}: {p.name}")
        
        print("\n🔗 PO Items by Product:")
        for p in products:
            items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.product_id == p.id).all()
            if items:
                print(f"  Product {p.id} ({p.name}): {len(items)} PO items")
                for item in items:
                    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == item.purchase_order_id).first()
                    if po:
                        print(f"    - PO {po.po_number}: {po.status.value}")
            else:
                print(f"  Product {p.id} ({p.name}): No PO items")
        
        print("\n📊 PO Status Summary:")
        pos = db.query(PurchaseOrder).all()
        status_counts = {}
        for po in pos:
            status = po.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"  {status}: {count} POs")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_relationships() 