import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  LoginCredentials, RegisterData, AuthResponse,
  Product, ProductCreate, ProductUpdate,
  Category, CategoryCreate, CategoryUpdate,
  Inventory, InventoryCreate, InventoryUpdate,
  Location, LocationCreate, LocationUpdate,
  Supplier, SupplierCreate, SupplierUpdate,
  PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderItem, PurchaseOrderItemCreate, PurchaseOrderStatus,
  StockAlert, StockAlertCreate, StockAlertUpdate,
  AlertRule, AlertRuleCreate, AlertRuleUpdate,
  PaginatedResponse, UserWithPermissions, UserCreate, UserUpdate
} from '../types';

const API_BASE_URL = (window as any).__ENV__?.REACT_APP_API_URL || 'http://localhost:8000';
const API_VERSION = (window as any).__ENV__?.REACT_APP_API_VERSION || '/api/v1';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}${API_VERSION}`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
          console.log('Adding auth token to request:', config.url);
        } else {
          console.log('No auth token found for request:', config.url);
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          console.log('401 error detected, clearing auth data');
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          // Only redirect if not already on login page
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth API
  auth = {
    login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
      // Convert email to username for backend compatibility
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);
      
      const response: AxiosResponse<AuthResponse> = await this.api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response.data;
    },

    register: async (userData: RegisterData): Promise<AuthResponse> => {
      const response: AxiosResponse<AuthResponse> = await this.api.post('/auth/register', userData);
      return response.data;
    },

    // getCurrentUser is now in users.getCurrentUser

    forgotPassword: async (email: string): Promise<any> => {
      const response: AxiosResponse<any> = await this.api.post('/auth/forgot-password', { email });
      return response.data;
    },

    resetPassword: async (data: { token: string; new_password: string }): Promise<any> => {
      const response: AxiosResponse<any> = await this.api.post('/auth/reset-password', {
        email: '', // This will be extracted from token on backend
        token: data.token,
        new_password: data.new_password,
      });
      return response.data;
    },

    logout: () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    },
  };

  // Users API
  users = {
    getCurrentUser: async (): Promise<UserWithPermissions> => {
      const response: AxiosResponse<UserWithPermissions> = await this.api.get('/users/me');
      return response.data;
    },

    getUsers: async (params?: {
      skip?: number;
      limit?: number;
    }): Promise<UserWithPermissions[]> => {
      const response: AxiosResponse<UserWithPermissions[]> = await this.api.get('/users/', { params });
      return response.data;
    },

    getUser: async (id: number): Promise<UserWithPermissions> => {
      const response: AxiosResponse<UserWithPermissions> = await this.api.get(`/users/${id}`);
      return response.data;
    },

    createUser: async (userData: UserCreate): Promise<UserWithPermissions> => {
      const response: AxiosResponse<UserWithPermissions> = await this.api.post('/users/', userData);
      return response.data;
    },

    updateUser: async (id: number, userData: UserUpdate): Promise<UserWithPermissions> => {
      const response: AxiosResponse<UserWithPermissions> = await this.api.put(`/users/${id}`, userData);
      return response.data;
    },

    deleteUser: async (id: number): Promise<void> => {
      await this.api.delete(`/users/${id}`);
    },

    getAvailableRoles: async (): Promise<string[]> => {
      const response: AxiosResponse<string[]> = await this.api.get('/users/roles/available');
      return response.data;
    },

    changePassword: async (data: { current_password: string; new_password: string }): Promise<void> => {
      await this.api.post('/users/change-password', data);
    },
  };

  // Products API
  products = {
    getProducts: async (params?: {
      skip?: number;
      limit?: number;
      search?: string;
      category_id?: number;
      supplier_id?: number;
      is_active?: boolean;
    }): Promise<PaginatedResponse<Product>> => {
      const response: AxiosResponse<PaginatedResponse<Product>> = await this.api.get('/products/', { params });
      return response.data;
    },

    getProduct: async (id: number): Promise<Product> => {
      const response: AxiosResponse<Product> = await this.api.get(`/products/${id}`);
      return response.data;
    },

    createProduct: async (productData: ProductCreate): Promise<Product> => {
      const response: AxiosResponse<Product> = await this.api.post('/products/', productData);
      return response.data;
    },

    updateProduct: async (id: number, productData: ProductUpdate): Promise<Product> => {
      const response: AxiosResponse<Product> = await this.api.put(`/products/${id}`, productData);
      return response.data;
    },

    deleteProduct: async (id: number): Promise<void> => {
      await this.api.delete(`/products/${id}`);
    },
  };

  // Categories API
  categories = {
    getCategories: async (params?: {
      skip?: number;
      limit?: number;
      search?: string;
      is_active?: boolean;
    }): Promise<PaginatedResponse<Category>> => {
      const response: AxiosResponse<PaginatedResponse<Category>> = await this.api.get('/categories/', { params });
      return response.data;
    },

    getCategory: async (id: number): Promise<Category> => {
      const response: AxiosResponse<Category> = await this.api.get(`/categories/${id}`);
      return response.data;
    },

    createCategory: async (categoryData: CategoryCreate): Promise<Category> => {
      const response: AxiosResponse<Category> = await this.api.post('/categories/', categoryData);
      return response.data;
    },

    updateCategory: async (id: number, categoryData: CategoryUpdate): Promise<Category> => {
      const response: AxiosResponse<Category> = await this.api.put(`/categories/${id}`, categoryData);
      return response.data;
    },

    deleteCategory: async (id: number): Promise<void> => {
      await this.api.delete(`/categories/${id}`);
    },
  };

  // Inventory API
  inventory = {
    getInventory: async (params?: {
      skip?: number;
      limit?: number;
      product_id?: number;
      location_id?: number;
    }): Promise<PaginatedResponse<Inventory>> => {
      const response: AxiosResponse<PaginatedResponse<Inventory>> = await this.api.get('/inventory/', { params });
      return response.data;
    },

    getInventoryItem: async (id: number): Promise<Inventory> => {
      const response: AxiosResponse<Inventory> = await this.api.get(`/inventory/${id}`);
      return response.data;
    },

    createInventoryItem: async (inventoryData: InventoryCreate): Promise<Inventory> => {
      const response: AxiosResponse<Inventory> = await this.api.post('/inventory/', inventoryData);
      return response.data;
    },

    updateInventoryItem: async (id: number, inventoryData: InventoryUpdate): Promise<Inventory> => {
      const response: AxiosResponse<Inventory> = await this.api.put(`/inventory/${id}`, inventoryData);
      return response.data;
    },

    deleteInventoryItem: async (id: number): Promise<void> => {
      await this.api.delete(`/inventory/${id}`);
    },

    adjustStock: async (inventoryId: number, quantityChange: number, notes?: string): Promise<any> => {
      const response: AxiosResponse<any> = await this.api.post(`/inventory/${inventoryId}/adjust-stock`, {
        quantity_change: quantityChange,
        notes: notes
      });
      return response.data;
    },

    createStockMovement: async (inventoryId: number, movementData: any): Promise<any> => {
      const response: AxiosResponse<any> = await this.api.post(`/inventory/${inventoryId}/stock-movement`, movementData);
      return response.data;
    },

    getStockMovements: async (inventoryId: number, params?: {
      skip?: number;
      limit?: number;
    }): Promise<any> => {
      const response: AxiosResponse<any> = await this.api.get(`/inventory/${inventoryId}/stock-movements`, { params });
      return response.data;
    },

    getLowStockItems: async (params?: {
      skip?: number;
      limit?: number;
    }): Promise<PaginatedResponse<Inventory>> => {
      const response: AxiosResponse<PaginatedResponse<Inventory>> = await this.api.get('/inventory/low-stock', { params });
      return response.data;
    },

    getOutOfStockItems: async (params?: {
      skip?: number;
      limit?: number;
    }): Promise<PaginatedResponse<Inventory>> => {
      const response: AxiosResponse<PaginatedResponse<Inventory>> = await this.api.get('/inventory/out-of-stock', { params });
      return response.data;
    },
  };

  // Locations API
  locations = {
    getLocations: async (params?: {
      skip?: number;
      limit?: number;
      search?: string;
      warehouse_type?: string;
      is_active?: boolean;
    }): Promise<PaginatedResponse<Location>> => {
      const response: AxiosResponse<PaginatedResponse<Location>> = await this.api.get('/locations/', { params });
      return response.data;
    },

    getLocation: async (id: number): Promise<Location> => {
      const response: AxiosResponse<Location> = await this.api.get(`/locations/${id}`);
      return response.data;
    },

    createLocation: async (locationData: LocationCreate): Promise<Location> => {
      const response: AxiosResponse<Location> = await this.api.post('/locations/', locationData);
      return response.data;
    },

    updateLocation: async (id: number, locationData: LocationUpdate): Promise<Location> => {
      const response: AxiosResponse<Location> = await this.api.put(`/locations/${id}`, locationData);
      return response.data;
    },

    deleteLocation: async (id: number): Promise<void> => {
      await this.api.delete(`/locations/${id}`);
    },
  };

  // Suppliers API
  suppliers = {
    getSuppliers: async (params?: {
      skip?: number;
      limit?: number;
      search?: string;
      is_active?: boolean;
    }): Promise<PaginatedResponse<Supplier>> => {
      const response: AxiosResponse<PaginatedResponse<Supplier>> = await this.api.get('/suppliers/', { params });
      return response.data;
    },

    getSupplier: async (id: number): Promise<Supplier> => {
      const response: AxiosResponse<Supplier> = await this.api.get(`/suppliers/${id}`);
      return response.data;
    },

    createSupplier: async (supplierData: SupplierCreate): Promise<Supplier> => {
      const response: AxiosResponse<Supplier> = await this.api.post('/suppliers/', supplierData);
      return response.data;
    },

    updateSupplier: async (id: number, supplierData: SupplierUpdate): Promise<Supplier> => {
      const response: AxiosResponse<Supplier> = await this.api.put(`/suppliers/${id}`, supplierData);
      return response.data;
    },

    deleteSupplier: async (id: number): Promise<void> => {
      await this.api.delete(`/suppliers/${id}`);
    },
  };

  // Purchase Orders API
  purchaseOrders = {
    getPurchaseOrders: async (params?: {
      skip?: number;
      limit?: number;
      status?: string;
      supplier_id?: number;
      start_date?: string;
      end_date?: string;
    }): Promise<PaginatedResponse<PurchaseOrder>> => {
      const response: AxiosResponse<PaginatedResponse<PurchaseOrder>> = await this.api.get('/purchase-orders/', { params });
      return response.data;
    },

    getPurchaseOrder: async (id: number): Promise<PurchaseOrder> => {
      const response: AxiosResponse<PurchaseOrder> = await this.api.get(`/purchase-orders/${id}`);
      return response.data;
    },

    createPurchaseOrder: async (poData: PurchaseOrderCreate): Promise<PurchaseOrder> => {
      const response: AxiosResponse<PurchaseOrder> = await this.api.post('/purchase-orders/', poData);
      return response.data;
    },

    updatePurchaseOrder: async (id: number, poData: PurchaseOrderUpdate): Promise<PurchaseOrder> => {
      const response: AxiosResponse<PurchaseOrder> = await this.api.put(`/purchase-orders/${id}`, poData);
      return response.data;
    },

    updatePurchaseOrderWithItems: async (id: number, poData: PurchaseOrderCreate): Promise<PurchaseOrder> => {
      const response: AxiosResponse<PurchaseOrder> = await this.api.put(`/purchase-orders/${id}/with-items`, poData);
      return response.data;
    },

    cancelPurchaseOrder: async (id: number): Promise<void> => {
      await this.api.post(`/purchase-orders/${id}/cancel`);
    },

    addPurchaseOrderItem: async (poId: number, itemData: PurchaseOrderItemCreate): Promise<PurchaseOrderItem> => {
      const response: AxiosResponse<PurchaseOrderItem> = await this.api.post(`/purchase-orders/${poId}/items`, itemData);
      return response.data;
    },

    updatePurchaseOrderItem: async (poId: number, itemId: number, itemData: Partial<PurchaseOrderItem>): Promise<PurchaseOrderItem> => {
      const response: AxiosResponse<PurchaseOrderItem> = await this.api.put(`/purchase-orders/${poId}/items/${itemId}`, itemData);
      return response.data;
    },

    changePurchaseOrderStatus: async (poId: number, newStatus: PurchaseOrderStatus): Promise<PurchaseOrder> => {
      const response: AxiosResponse<PurchaseOrder> = await this.api.post(`/purchase-orders/${poId}/status`, {
        new_status: newStatus
      });
      return response.data;
    },

    receivePurchaseOrder: async (poId: number, receivedItems: any[], locationId: number): Promise<PurchaseOrder> => {
      const response: AxiosResponse<PurchaseOrder> = await this.api.post(`/purchase-orders/${poId}/receive`, {
        received_items: receivedItems,
        location_id: locationId
      });
      return response.data;
    },
  };

  // Stock Alerts API
  stockAlerts = {
    getStockAlerts: async (params?: {
      skip?: number;
      limit?: number;
      status?: string;
      alert_type?: string;
      product_id?: number;
      location_id?: number;
    }): Promise<PaginatedResponse<StockAlert>> => {
      const response: AxiosResponse<PaginatedResponse<StockAlert>> = await this.api.get('/stock-alerts/alerts/', { params });
      return response.data;
    },

    getActiveAlerts: async (): Promise<StockAlert[]> => {
      const response: AxiosResponse<StockAlert[]> = await this.api.get('/stock-alerts/alerts/active');
      return response.data;
    },

    createStockAlert: async (alertData: StockAlertCreate): Promise<StockAlert> => {
      const response: AxiosResponse<StockAlert> = await this.api.post('/stock-alerts/alerts/', alertData);
      return response.data;
    },

    updateStockAlert: async (id: number, alertData: StockAlertUpdate): Promise<StockAlert> => {
      const response: AxiosResponse<StockAlert> = await this.api.put(`/stock-alerts/alerts/${id}`, alertData);
      return response.data;
    },

    getAlertRules: async (params?: {
      skip?: number;
      limit?: number;
      alert_type?: string;
      is_active?: boolean;
    }): Promise<PaginatedResponse<AlertRule>> => {
      const response: AxiosResponse<PaginatedResponse<AlertRule>> = await this.api.get('/stock-alerts/rules/', { params });
      return response.data;
    },

    createAlertRule: async (ruleData: AlertRuleCreate): Promise<AlertRule> => {
      const response: AxiosResponse<AlertRule> = await this.api.post('/stock-alerts/rules/', ruleData);
      return response.data;
    },

    updateAlertRule: async (id: number, ruleData: AlertRuleUpdate): Promise<AlertRule> => {
      const response: AxiosResponse<AlertRule> = await this.api.put(`/stock-alerts/rules/${id}`, ruleData);
      return response.data;
    },

    deleteAlertRule: async (id: number): Promise<void> => {
      await this.api.delete(`/stock-alerts/rules/${id}`);
    },

    checkAlerts: async (): Promise<{ message: string }> => {
      const response: AxiosResponse<{ message: string }> = await this.api.post('/stock-alerts/check-alerts');
      return response.data;
    },

    cleanupDuplicates: async (): Promise<{ message: string }> => {
      const response: AxiosResponse<{ message: string }> = await this.api.post('/stock-alerts/cleanup-duplicates');
      return response.data;
    },
  };
}

export const apiService = new ApiService();
export default apiService; 