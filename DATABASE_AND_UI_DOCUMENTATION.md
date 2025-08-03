# Inventory Management System - Database & UI Documentation

## 📊 Database Schema & Relationships

### Core Tables Overview

The system consists of 8 main tables with complex relationships:

```
users
├── categories
│   └── products
│       ├── inventory (with locations)
│       ├── purchase_order_items
│       └── stock_alerts
├── suppliers
│   ├── products
│   └── purchase_orders
│       └── purchase_order_items
├── locations
│   ├── inventory
│   ├── stock_movements (from/to)
│   └── stock_alerts
└── stock_movements
    ├── inventory
    ├── locations (from/to)
    └── users
```

### 1. Users Table
**Purpose**: User authentication and authorization
```sql
users (
    id (PK),
    email (unique),
    username (unique),
    hashed_password,
    full_name,
    is_active,
    is_superuser,
    created_at,
    updated_at
)
```

**Relationships**:
- One-to-Many: `users` → `purchase_orders` (created_by, approved_by)
- One-to-Many: `users` → `stock_movements` (created_by)
- One-to-Many: `users` → `stock_alerts` (acknowledged_by, resolved_by)
- One-to-Many: `users` → `alert_rules` (created_by)

### 2. Categories Table
**Purpose**: Product categorization
```sql
categories (
    id (PK),
    name (unique),
    description,
    created_at,
    updated_at
)
```

**Relationships**:
- One-to-Many: `categories` → `products`
- One-to-Many: `categories` → `alert_rules`

### 3. Products Table
**Purpose**: Product master data
```sql
products (
    id (PK),
    name,
    description,
    sku (unique),
    brand,
    model,
    price,
    cost,
    weight,
    dimensions (JSON),
    specifications (JSON),
    barcode,
    is_active,
    category_id (FK),
    supplier_id (FK),
    min_stock_level,
    max_stock_level,
    reorder_point,
    created_at,
    updated_at
)
```

**Relationships**:
- Many-to-One: `products` → `categories`
- Many-to-One: `products` → `suppliers`
- One-to-Many: `products` → `inventory`
- One-to-Many: `products` → `purchase_order_items`
- One-to-Many: `products` → `stock_alerts`
- One-to-Many: `products` → `alert_rules`

### 4. Suppliers Table
**Purpose**: Supplier information
```sql
suppliers (
    id (PK),
    name,
    code (unique),
    contact_person,
    email,
    phone,
    address,
    tax_id,
    payment_terms,
    is_active,
    rating,
    notes,
    created_at,
    updated_at
)
```

**Relationships**:
- One-to-Many: `suppliers` → `products`
- One-to-Many: `suppliers` → `purchase_orders`

### 5. Locations Table
**Purpose**: Warehouse and storage locations
```sql
locations (
    id (PK),
    name,
    code (unique),
    address,
    warehouse_type,
    is_active,
    created_at,
    updated_at
)
```

**Relationships**:
- One-to-Many: `locations` → `inventory`
- One-to-Many: `locations` → `stock_movements` (from_location_id, to_location_id)
- One-to-Many: `locations` → `stock_alerts`
- One-to-Many: `locations` → `alert_rules`

### 6. Inventory Table
**Purpose**: Stock levels by product and location
```sql
inventory (
    id (PK),
    product_id (FK),
    location_id (FK),
    quantity,
    reserved_quantity,
    available_quantity,
    unit_cost,
    last_restocked,
    notes,
    created_at,
    updated_at
)
```

**Relationships**:
- Many-to-One: `inventory` → `products`
- Many-to-One: `inventory` → `locations`
- One-to-Many: `inventory` → `stock_movements`

### 7. Stock Movements Table
**Purpose**: Track all stock transactions
```sql
stock_movements (
    id (PK),
    inventory_item_id (FK),
    movement_type (ENUM: in, out, transfer, adjustment),
    quantity,
    from_location_id (FK),
    to_location_id (FK),
    reference_type,
    reference_id,
    unit_cost,
    notes,
    created_by (FK),
    created_at
)
```

**Relationships**:
- Many-to-One: `stock_movements` → `inventory`
- Many-to-One: `stock_movements` → `locations` (from_location)
- Many-to-One: `stock_movements` → `locations` (to_location)
- Many-to-One: `stock_movements` → `users`

### 8. Purchase Orders Table
**Purpose**: Purchase order management
```sql
purchase_orders (
    id (PK),
    po_number (unique),
    supplier_id (FK),
    status (ENUM: draft, pending_approval, approved, ordered, partially_received, received, cancelled),
    order_date,
    expected_delivery_date,
    delivery_date,
    subtotal,
    tax_amount,
    shipping_amount,
    total_amount,
    currency,
    payment_terms,
    shipping_address,
    billing_address,
    notes,
    created_by (FK),
    approved_by (FK),
    approved_at,
    created_at,
    updated_at
)
```

**Relationships**:
- Many-to-One: `purchase_orders` → `suppliers`
- Many-to-One: `purchase_orders` → `users` (created_by)
- Many-to-One: `purchase_orders` → `users` (approved_by)
- One-to-Many: `purchase_orders` → `purchase_order_items`

### 9. Purchase Order Items Table
**Purpose**: Individual items in purchase orders
```sql
purchase_order_items (
    id (PK),
    purchase_order_id (FK),
    product_id (FK),
    quantity,
    unit_price,
    total_price,
    received_quantity,
    supplier_sku,
    notes,
    created_at,
    updated_at
)
```

**Relationships**:
- Many-to-One: `purchase_order_items` → `purchase_orders`
- Many-to-One: `purchase_order_items` → `products`

### 10. Stock Alerts Table
**Purpose**: Automated stock level alerts
```sql
stock_alerts (
    id (PK),
    product_id (FK),
    location_id (FK),
    alert_type (ENUM: low_stock, out_of_stock, overstock, expiry_warning),
    status (ENUM: active, acknowledged, resolved, dismissed),
    current_quantity,
    threshold_quantity,
    message,
    is_email_sent,
    is_sms_sent,
    acknowledged_by (FK),
    acknowledged_at,
    resolved_by (FK),
    resolved_at,
    created_at,
    updated_at
)
```

**Relationships**:
- Many-to-One: `stock_alerts` → `products`
- Many-to-One: `stock_alerts` → `locations`
- Many-to-One: `stock_alerts` → `users` (acknowledged_by)
- Many-to-One: `stock_alerts` → `users` (resolved_by)

### 11. Alert Rules Table
**Purpose**: Configurable alert rules
```sql
alert_rules (
    id (PK),
    name,
    alert_type (ENUM),
    product_id (FK),
    category_id (FK),
    location_id (FK),
    threshold_quantity,
    threshold_percentage,
    is_active,
    notify_email,
    notify_sms,
    notify_dashboard,
    created_by (FK),
    created_at,
    updated_at
)
```

**Relationships**:
- Many-to-One: `alert_rules` → `products`
- Many-to-One: `alert_rules` → `categories`
- Many-to-One: `alert_rules` → `locations`
- Many-to-One: `alert_rules` → `users`

---

## 🖥️ UI Functionality - Page by Page

### 1. Authentication Pages

#### Login Page (`/login`)
**Purpose**: User authentication
**Features**:
- Email/username and password login
- Form validation
- Error handling
- Redirect to dashboard on success
- Link to registration page

#### Register Page (`/register`)
**Purpose**: New user registration
**Features**:
- User registration form
- Password confirmation
- Form validation
- Success/error notifications
- Link to login page

### 2. Dashboard Page (`/`)
**Purpose**: System overview and key metrics
**Features**:
- **Summary Cards**:
  - Total products
  - Total inventory value
  - Active alerts
  - Pending purchase orders
- **Charts & Graphs**:
  - Stock levels by category
  - Recent stock movements
  - Alert trends
- **Quick Actions**:
  - Create new product
  - Create purchase order
  - View alerts
- **Recent Activity**:
  - Latest stock movements
  - Recent alerts
  - Recent purchase orders

### 3. Products Page (`/products`)
**Purpose**: Product master data management
**Features**:
- **Product List**:
  - Search and filter products
  - Sort by name, SKU, category, supplier
  - Pagination
- **Product Details**:
  - View product information
  - Current stock levels across locations
  - Related purchase orders
- **Product Management**:
  - Add new product
  - Edit existing product
  - Deactivate/reactivate product
  - Set stock levels (min, max, reorder point)
- **Bulk Operations**:
  - Import products
  - Export product data
  - Bulk update categories/suppliers

### 4. Categories Page (`/categories`)
**Purpose**: Product categorization
**Features**:
- **Category List**:
  - View all categories
  - Search categories
  - Sort by name
- **Category Management**:
  - Add new category
  - Edit category details
  - Delete category (with product count check)
- **Category Analytics**:
  - Products per category
  - Stock value by category
  - Category performance metrics

### 5. Inventory Page (`/inventory`)
**Purpose**: Stock level management and tracking
**Features**:
- **Inventory Overview**:
  - Stock levels by location
  - Available vs reserved quantities
  - Low stock indicators
- **Stock Movements**:
  - Record stock in/out
  - Transfer between locations
  - Stock adjustments
  - Movement history
- **Inventory Management**:
  - Update stock levels
  - Reserve stock for orders
  - Release reserved stock
  - Stock count reconciliation
- **Reports**:
  - Stock aging report
  - Movement history
  - Stock valuation
  - ABC analysis

### 6. Suppliers Page (`/suppliers`)
**Purpose**: Supplier relationship management
**Features**:
- **Supplier List**:
  - Search and filter suppliers
  - Sort by name, rating, performance
  - Active/inactive status
- **Supplier Details**:
  - Contact information
  - Performance metrics
  - Associated products
  - Purchase history
- **Supplier Management**:
  - Add new supplier
  - Edit supplier information
  - Deactivate supplier
  - Rate supplier performance
- **Supplier Analytics**:
  - Purchase volume by supplier
  - Delivery performance
  - Cost analysis

### 7. Locations Page (`/locations`)
**Purpose**: Warehouse and storage location management
**Features**:
- **Location List**:
  - View all locations
  - Location types (main, secondary, retail)
  - Active/inactive status
- **Location Details**:
  - Address and contact info
  - Current inventory
  - Storage capacity
  - Location performance
- **Location Management**:
  - Add new location
  - Edit location details
  - Deactivate location
  - Set location capacity
- **Location Analytics**:
  - Stock distribution
  - Space utilization
  - Movement patterns

### 8. Purchase Orders Page (`/purchase-orders`)
**Purpose**: Purchase order lifecycle management
**Features**:
- **Purchase Order List**:
  - Filter by status, supplier, date range
  - Sort by creation date, total amount
  - Status indicators
- **Purchase Order Details**:
  - Order items and quantities
  - Pricing and totals
  - Delivery information
  - Approval workflow
- **Purchase Order Management**:
  - Create new purchase order
  - Add/remove items
  - Update quantities and prices
  - Submit for approval
  - Receive items
  - Close/cancel orders
- **Workflow Management**:
  - Draft → Pending Approval → Approved → Ordered → Received
  - Approval notifications
  - Delivery tracking
- **Reports**:
  - Purchase order history
  - Supplier performance
  - Cost analysis

### 9. Stock Alerts Page (`/stock-alerts`)
**Purpose**: Automated alert management
**Features**:
- **Alert Dashboard**:
  - Active alerts by type
  - Alert severity levels
  - Location-based alerts
- **Alert Management**:
  - View alert details
  - Acknowledge alerts
  - Resolve alerts
  - Dismiss alerts
- **Alert Rules**:
  - Configure alert thresholds
  - Set notification preferences
  - Create product/category/location specific rules
- **Alert History**:
  - Historical alerts
  - Resolution tracking
  - Performance metrics
- **Notifications**:
  - Email notifications
  - SMS notifications
  - Dashboard notifications

---

## 🔄 Key Business Workflows

### 1. Product Lifecycle
1. **Product Creation**: Add product with category, supplier, and stock levels
2. **Initial Stock**: Record initial inventory across locations
3. **Stock Monitoring**: System tracks stock levels and generates alerts
4. **Reorder Process**: Create purchase orders when stock reaches reorder point
5. **Stock Receipt**: Receive items and update inventory

### 2. Purchase Order Workflow
1. **Draft Creation**: Create PO with supplier and items
2. **Approval Process**: Submit for approval, approve/reject
3. **Order Placement**: Send to supplier
4. **Delivery Tracking**: Monitor delivery status
5. **Receipt Processing**: Receive items and update inventory
6. **Order Closure**: Complete or cancel order

### 3. Stock Movement Process
1. **Movement Initiation**: Record stock in/out/transfer
2. **Validation**: Check available stock
3. **Execution**: Update inventory levels
4. **Documentation**: Record movement details
5. **Alert Check**: Trigger alerts if needed

### 4. Alert Management
1. **Rule Configuration**: Set up alert rules
2. **Monitoring**: System continuously monitors stock levels
3. **Alert Generation**: Create alerts when thresholds are breached
4. **Notification**: Send notifications via email/SMS
5. **Resolution**: Acknowledge and resolve alerts

---

## 📈 Data Flow Architecture

```
Frontend (React) ↔ API (FastAPI) ↔ Database (PostgreSQL)
     ↓                    ↓              ↓
  User Interface    Business Logic    Data Storage
  - Forms          - Validation       - Tables
  - Tables         - Calculations     - Relationships
  - Charts         - Workflows        - Constraints
  - Notifications  - Notifications    - Indexes
```

This architecture ensures:
- **Separation of Concerns**: UI, business logic, and data are separate
- **Scalability**: Each layer can be scaled independently
- **Maintainability**: Changes in one layer don't affect others
- **Security**: API layer provides authentication and authorization
- **Performance**: Database indexes and caching optimize queries 