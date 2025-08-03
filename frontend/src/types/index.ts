// User types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: UserRole;
  department?: string;
  phone?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserWithPermissions extends User {
  can_approve_po: boolean;
  can_cancel_po: boolean;
  can_receive_po: boolean;
  can_edit_po: boolean;
  can_manage_users: boolean;
  can_view_reports: boolean;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  role: UserRole;
  department?: string;
  phone?: string;
  is_active?: boolean;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  password?: string;
  full_name?: string;
  role?: UserRole;
  department?: string;
  phone?: string;
  is_active?: boolean;
}

export enum UserRole {
  ADMIN = "admin",
  MANAGER = "manager",
  STAFF = "staff",
  VIEWER = "viewer"
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  role?: UserRole;
  department?: string;
  phone?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Product types
export interface Product {
  id: number;
  name: string;
  description?: string;
  sku: string;
  brand?: string;
  model?: string;
  price: number;
  cost?: number;
  weight?: number;
  dimensions?: Record<string, any>;
  specifications?: Record<string, any>;
  barcode?: string;
  is_active: boolean;
  category_id?: number;
  supplier_id?: number;
  min_stock_level: number;
  max_stock_level?: number;
  reorder_point: number;
  created_at: string;
  updated_at?: string;
  category?: Category;
  supplier?: Supplier;
}

export interface ProductCreate {
  name: string;
  description?: string;
  sku: string;
  brand?: string;
  model?: string;
  price: number;
  cost?: number;
  weight?: number;
  dimensions?: Record<string, any>;
  specifications?: Record<string, any>;
  barcode?: string;
  category_id?: number;
  supplier_id?: number;
  min_stock_level?: number;
  max_stock_level?: number;
  reorder_point?: number;
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  sku?: string;
  brand?: string;
  model?: string;
  price?: number;
  cost?: number;
  weight?: number;
  dimensions?: Record<string, any>;
  specifications?: Record<string, any>;
  barcode?: string;
  is_active?: boolean;
  category_id?: number;
  supplier_id?: number;
  min_stock_level?: number;
  max_stock_level?: number;
  reorder_point?: number;
}

// Category types
export interface Category {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CategoryCreate {
  name: string;
  description?: string;
  is_active?: boolean;
}

export interface CategoryUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
}

// Inventory types
export interface Inventory {
  id: number;
  product_id: number;
  location_id: number;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  unit_cost?: number;
  last_restocked?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
  product?: Product;
  location?: Location;
}

export interface InventoryCreate {
  product_id: number;
  location_id: number;
  quantity: number;
  reserved_quantity?: number;
  unit_cost?: number;
  notes?: string;
}

export interface InventoryUpdate {
  quantity?: number;
  reserved_quantity?: number;
  unit_cost?: number;
  notes?: string;
}

// Location types
export interface Location {
  id: number;
  name: string;
  code: string;
  address?: string;
  warehouse_type?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface LocationCreate {
  name: string;
  code: string;
  address?: string;
  warehouse_type?: string;
}

export interface LocationUpdate {
  name?: string;
  code?: string;
  address?: string;
  warehouse_type?: string;
  is_active?: boolean;
}

// Supplier types
export interface Supplier {
  id: number;
  name: string;
  code: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  tax_id?: string;
  payment_terms?: string;
  rating?: number;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SupplierCreate {
  name: string;
  code: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  tax_id?: string;
  payment_terms?: string;
  rating?: number;
  notes?: string;
}

export interface SupplierUpdate {
  name?: string;
  code?: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  tax_id?: string;
  payment_terms?: string;
  rating?: number;
  notes?: string;
  is_active?: boolean;
}

// Purchase Order types
export enum PurchaseOrderStatus {
  DRAFT = "draft",
  PENDING_APPROVAL = "pending_approval",
  APPROVED = "approved",
  ORDERED = "ordered",
  PARTIALLY_RECEIVED = "partially_received",
  RECEIVED = "received",
  CANCELLED = "cancelled"
}

export interface PurchaseOrderItem {
  id: number;
  purchase_order_id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  total_price: number;
  received_quantity: number;
  supplier_sku?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
  product?: Product;
}

export interface PurchaseOrderItemCreate {
  product_id: number;
  quantity: number;
  unit_price: number;
  supplier_sku?: string;
  notes?: string;
}

export interface PurchaseOrderItemUpdate {
  quantity?: number;
  unit_price?: number;
  supplier_sku?: string;
  notes?: string;
}

export interface PurchaseOrder {
  id: number;
  po_number: string;
  supplier_id: number;
  status: PurchaseOrderStatus;
  order_date: string;
  expected_delivery_date?: string;
  delivery_date?: string;
  subtotal: number;
  tax_amount: number;
  shipping_amount: number;
  total_amount: number;
  currency: string;
  payment_terms?: string;
  shipping_address?: string;
  billing_address?: string;
  notes?: string;
  created_by: number;
  approved_by?: number;
  approved_at?: string;
  created_at: string;
  updated_at?: string;
  supplier?: Supplier;
  items: PurchaseOrderItem[];
}

export interface PurchaseOrderCreate {
  supplier_id: number;
  order_date: string;
  expected_delivery_date?: string;
  payment_terms?: string;
  shipping_address?: string;
  billing_address?: string;
  notes?: string;
  items: PurchaseOrderItemCreate[];
  tax_amount?: number;
  shipping_amount?: number;
}

export interface PurchaseOrderUpdate {
  supplier_id?: number;
  status?: PurchaseOrderStatus;
  order_date?: string;
  expected_delivery_date?: string;
  delivery_date?: string;
  payment_terms?: string;
  shipping_address?: string;
  billing_address?: string;
  notes?: string;
  tax_amount?: number;
  shipping_amount?: number;
}

// Stock Alert types
export enum AlertType {
  LOW_STOCK = "low_stock",
  OUT_OF_STOCK = "out_of_stock",
  OVERSTOCK = "overstock",
  EXPIRY_WARNING = "expiry_warning"
}

export enum AlertStatus {
  ACTIVE = "active",
  ACKNOWLEDGED = "acknowledged",
  RESOLVED = "resolved",
  DISMISSED = "dismissed"
}

export interface StockAlert {
  id: number;
  product_id: number;
  location_id?: number;
  alert_type: AlertType;
  status: AlertStatus;
  current_quantity: number;
  threshold_quantity: number;
  message: string;
  is_email_sent: boolean;
  is_sms_sent: boolean;
  acknowledged_by?: number;
  acknowledged_at?: string;
  resolved_by?: number;
  resolved_at?: string;
  created_at: string;
  updated_at?: string;
  product?: Product;
  location?: Location;
}

export interface StockAlertCreate {
  product_id: number;
  location_id?: number;
  alert_type: AlertType;
  current_quantity: number;
  threshold_quantity: number;
  message: string;
}

export interface StockAlertUpdate {
  status?: AlertStatus;
  acknowledged_by?: number;
  resolved_by?: number;
}

export interface AlertRule {
  id: number;
  name: string;
  alert_type: AlertType;
  product_id?: number;
  category_id?: number;
  location_id?: number;
  threshold_quantity: number;
  threshold_percentage?: number;
  is_active: boolean;
  notify_email: boolean;
  notify_sms: boolean;
  notify_dashboard: boolean;
  created_by: number;
  created_at: string;
  updated_at?: string;
}

export interface AlertRuleCreate {
  name: string;
  alert_type: AlertType;
  product_id?: number;
  category_id?: number;
  location_id?: number;
  threshold_quantity: number;
  threshold_percentage?: number;
  notify_email?: boolean;
  notify_sms?: boolean;
  notify_dashboard?: boolean;
}

export interface AlertRuleUpdate {
  name?: string;
  alert_type?: AlertType;
  product_id?: number;
  category_id?: number;
  location_id?: number;
  threshold_quantity?: number;
  threshold_percentage?: number;
  is_active?: boolean;
  notify_email?: boolean;
  notify_sms?: boolean;
  notify_dashboard?: boolean;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
} 