# Database Entity Relationship Diagram (ERD)

## Visual Database Schema

```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string username UK
        string hashed_password
        string full_name
        boolean is_active
        boolean is_superuser
        datetime created_at
        datetime updated_at
    }

    CATEGORIES {
        int id PK
        string name UK
        text description
        datetime created_at
        datetime updated_at
    }

    SUPPLIERS {
        int id PK
        string name
        string code UK
        string contact_person
        string email
        string phone
        text address
        string tax_id
        string payment_terms
        boolean is_active
        int rating
        text notes
        datetime created_at
        datetime updated_at
    }

    LOCATIONS {
        int id PK
        string name
        string code UK
        text address
        string warehouse_type
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    PRODUCTS {
        int id PK
        string name
        text description
        string sku UK
        string brand
        string model
        float price
        float cost
        float weight
        json dimensions
        json specifications
        string barcode
        boolean is_active
        int category_id FK
        int supplier_id FK
        int min_stock_level
        int max_stock_level
        int reorder_point
        datetime created_at
        datetime updated_at
    }

    INVENTORY {
        int id PK
        int product_id FK
        int location_id FK
        int quantity
        int reserved_quantity
        int available_quantity
        float unit_cost
        datetime last_restocked
        text notes
        datetime created_at
        datetime updated_at
    }

    STOCK_MOVEMENTS {
        int id PK
        int inventory_item_id FK
        enum movement_type
        int quantity
        int from_location_id FK
        int to_location_id FK
        string reference_type
        int reference_id
        float unit_cost
        text notes
        int created_by FK
        datetime created_at
    }

    PURCHASE_ORDERS {
        int id PK
        string po_number UK
        int supplier_id FK
        enum status
        date order_date
        date expected_delivery_date
        date delivery_date
        float subtotal
        float tax_amount
        float shipping_amount
        float total_amount
        string currency
        string payment_terms
        text shipping_address
        text billing_address
        text notes
        int created_by FK
        int approved_by FK
        datetime approved_at
        datetime created_at
        datetime updated_at
    }

    PURCHASE_ORDER_ITEMS {
        int id PK
        int purchase_order_id FK
        int product_id FK
        int quantity
        float unit_price
        float total_price
        int received_quantity
        string supplier_sku
        text notes
        datetime created_at
        datetime updated_at
    }

    STOCK_ALERTS {
        int id PK
        int product_id FK
        int location_id FK
        enum alert_type
        enum status
        int current_quantity
        int threshold_quantity
        text message
        boolean is_email_sent
        boolean is_sms_sent
        int acknowledged_by FK
        datetime acknowledged_at
        int resolved_by FK
        datetime resolved_at
        datetime created_at
        datetime updated_at
    }

    ALERT_RULES {
        int id PK
        string name
        enum alert_type
        int product_id FK
        int category_id FK
        int location_id FK
        int threshold_quantity
        float threshold_percentage
        boolean is_active
        boolean notify_email
        boolean notify_sms
        boolean notify_dashboard
        int created_by FK
        datetime created_at
        datetime updated_at
    }

    %% Relationships
    USERS ||--o{ PURCHASE_ORDERS : "created_by"
    USERS ||--o{ PURCHASE_ORDERS : "approved_by"
    USERS ||--o{ STOCK_MOVEMENTS : "created_by"
    USERS ||--o{ STOCK_ALERTS : "acknowledged_by"
    USERS ||--o{ STOCK_ALERTS : "resolved_by"
    USERS ||--o{ ALERT_RULES : "created_by"

    CATEGORIES ||--o{ PRODUCTS : "category_id"
    CATEGORIES ||--o{ ALERT_RULES : "category_id"

    SUPPLIERS ||--o{ PRODUCTS : "supplier_id"
    SUPPLIERS ||--o{ PURCHASE_ORDERS : "supplier_id"

    LOCATIONS ||--o{ INVENTORY : "location_id"
    LOCATIONS ||--o{ STOCK_MOVEMENTS : "from_location_id"
    LOCATIONS ||--o{ STOCK_MOVEMENTS : "to_location_id"
    LOCATIONS ||--o{ STOCK_ALERTS : "location_id"
    LOCATIONS ||--o{ ALERT_RULES : "location_id"

    PRODUCTS ||--o{ INVENTORY : "product_id"
    PRODUCTS ||--o{ PURCHASE_ORDER_ITEMS : "product_id"
    PRODUCTS ||--o{ STOCK_ALERTS : "product_id"
    PRODUCTS ||--o{ ALERT_RULES : "product_id"

    INVENTORY ||--o{ STOCK_MOVEMENTS : "inventory_item_id"

    PURCHASE_ORDERS ||--o{ PURCHASE_ORDER_ITEMS : "purchase_order_id"
```

## Key Relationship Types

### One-to-Many (1:N) Relationships
- **Users → Purchase Orders**: One user can create/approve many purchase orders
- **Categories → Products**: One category can have many products
- **Suppliers → Products**: One supplier can supply many products
- **Suppliers → Purchase Orders**: One supplier can have many purchase orders
- **Locations → Inventory**: One location can have many inventory items
- **Products → Inventory**: One product can be in many locations
- **Products → Purchase Order Items**: One product can be in many purchase orders
- **Products → Stock Alerts**: One product can have many alerts
- **Inventory → Stock Movements**: One inventory item can have many movements

### Many-to-One (N:1) Relationships
- **Products → Categories**: Many products can belong to one category
- **Products → Suppliers**: Many products can be supplied by one supplier
- **Inventory → Products**: Many inventory items can reference one product
- **Inventory → Locations**: Many inventory items can be in one location
- **Purchase Orders → Suppliers**: Many purchase orders can be with one supplier
- **Purchase Order Items → Products**: Many items can reference one product

### Self-Referencing Relationships
- **Users → Users**: Users can approve purchase orders created by other users
- **Locations → Locations**: Stock movements can transfer between locations

## Database Constraints

### Primary Keys
- All tables have auto-incrementing integer primary keys
- Composite keys are used where needed (e.g., inventory: product_id + location_id)

### Foreign Keys
- All relationships are properly enforced with foreign key constraints
- Cascade delete is used where appropriate (e.g., purchase order items)

### Unique Constraints
- Email and username in users table
- SKU in products table
- PO number in purchase orders table
- Category name
- Supplier code
- Location code

### Check Constraints
- Stock quantities cannot be negative
- Prices and costs must be positive
- Alert thresholds must be reasonable values

## Indexes for Performance

### Primary Indexes
- All primary keys are automatically indexed

### Foreign Key Indexes
- All foreign key columns are indexed for join performance

### Unique Indexes
- Email, username, SKU, PO number, etc.

### Composite Indexes
- Inventory: (product_id, location_id)
- Stock movements: (inventory_item_id, created_at)
- Purchase order items: (purchase_order_id, product_id)

### Performance Indexes
- Created_at columns for date range queries
- Status columns for filtering
- Name columns for search functionality 