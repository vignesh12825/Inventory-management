import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock the API service
jest.mock('../../services/api', () => ({
  __esModule: true,
  default: {
    auth: {
      login: jest.fn(),
      register: jest.fn(),
      forgotPassword: jest.fn(),
      resetPassword: jest.fn(),
    },
    users: {
      getCurrentUser: jest.fn(),
      getUsers: jest.fn(),
      getUser: jest.fn(),
      createUser: jest.fn(),
      updateUser: jest.fn(),
      deleteUser: jest.fn(),
      changePassword: jest.fn(),
      getAvailableRoles: jest.fn(),
    },
    categories: {
      getCategories: jest.fn(),
      getCategory: jest.fn(),
      createCategory: jest.fn(),
      updateCategory: jest.fn(),
      deleteCategory: jest.fn(),
    },
    products: {
      getProducts: jest.fn(),
      getProduct: jest.fn(),
      createProduct: jest.fn(),
      updateProduct: jest.fn(),
      deleteProduct: jest.fn(),
    },
    suppliers: {
      getSuppliers: jest.fn(),
      getSupplier: jest.fn(),
      createSupplier: jest.fn(),
      updateSupplier: jest.fn(),
      deleteSupplier: jest.fn(),
    },
    locations: {
      getLocations: jest.fn(),
      getLocation: jest.fn(),
      createLocation: jest.fn(),
      updateLocation: jest.fn(),
      deleteLocation: jest.fn(),
    },
    inventory: {
      getInventoryItems: jest.fn(),
      getInventoryItem: jest.fn(),
      createInventoryItem: jest.fn(),
      updateInventoryItem: jest.fn(),
      deleteInventoryItem: jest.fn(),
    },
    purchaseOrders: {
      getPurchaseOrders: jest.fn(),
      getPurchaseOrder: jest.fn(),
      createPurchaseOrder: jest.fn(),
      updatePurchaseOrder: jest.fn(),
      deletePurchaseOrder: jest.fn(),
      approvePurchaseOrder: jest.fn(),
      rejectPurchaseOrder: jest.fn(),
    },
    stockAlerts: {
      getStockAlerts: jest.fn(),
      getStockAlert: jest.fn(),
      createStockAlert: jest.fn(),
      updateStockAlert: jest.fn(),
      deleteStockAlert: jest.fn(),
    },
  },
}));

// Create a new QueryClient for each test
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
    mutations: {
      retry: false,
    },
  },
});

// Custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient();
  
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          {children}
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react';

// Override render method
export { customRender as render };

// Test data helpers
export const mockUser = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  full_name: 'Test User',
  role: 'staff' as const,
  department: 'Testing',
  phone: '+1234567890',
  is_active: true,
  is_superuser: false,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  can_approve_po: false,
  can_cancel_po: false,
  can_receive_po: true,
  can_edit_po: true,
  can_manage_users: false,
  can_view_reports: false,
};

export const mockAdminUser = {
  ...mockUser,
  id: 2,
  email: 'admin@example.com',
  username: 'admin',
  full_name: 'Admin User',
  role: 'admin' as const,
  is_superuser: true,
  can_approve_po: true,
  can_cancel_po: true,
  can_receive_po: true,
  can_edit_po: true,
  can_manage_users: true,
  can_view_reports: true,
};

export const mockCategory = {
  id: 1,
  name: 'Test Category',
  description: 'Test category description',
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

export const mockProduct = {
  id: 1,
  name: 'Test Product',
  description: 'Test product description',
  sku: 'TEST-001',
  category_id: 1,
  category: mockCategory,
  unit_price: 10.99,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

export const mockInventoryItem = {
  id: 1,
  product_id: 1,
  product: mockProduct,
  location_id: 1,
  quantity: 100,
  min_quantity: 10,
  max_quantity: 1000,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

export const mockSupplier = {
  id: 1,
  name: 'Test Supplier',
  contact_person: 'John Doe',
  email: 'john@supplier.com',
  phone: '+1234567890',
  address: '123 Supplier St',
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

export const mockPurchaseOrder = {
  id: 1,
  supplier_id: 1,
  supplier: mockSupplier,
  status: 'pending' as const,
  total_amount: 1099.00,
  created_by: 1,
  approved_by: null,
  approved_at: null,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  items: [
    {
      id: 1,
      product_id: 1,
      product: mockProduct,
      quantity: 100,
      unit_price: 10.99,
      total_price: 1099.00,
    },
  ],
};

export const mockStockAlert = {
  id: 1,
  product_id: 1,
  product: mockProduct,
  alert_type: 'low_stock' as const,
  threshold: 10,
  current_quantity: 5,
  is_active: true,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
}; 