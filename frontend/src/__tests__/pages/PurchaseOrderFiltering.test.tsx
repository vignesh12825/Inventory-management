import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import PurchaseOrders from '../../pages/PurchaseOrders';
import { Product, Supplier } from '../../types';

// Mock the API service
const mockApiService = {
  purchaseOrders: {
    getPurchaseOrders: jest.fn(),
    createPurchaseOrder: jest.fn(),
    updatePurchaseOrderWithItems: jest.fn(),
    cancelPurchaseOrder: jest.fn(),
    changePurchaseOrderStatus: jest.fn(),
  },
  suppliers: {
    getSuppliers: jest.fn(),
  },
  products: {
    getProducts: jest.fn(),
  },
  users: {
    getCurrentUser: jest.fn(),
  },
};

jest.mock('../../services/api', () => ({
  __esModule: true,
  default: mockApiService,
}));

const mockSuppliers: Supplier[] = [
  { id: 1, name: 'Tech Supplies Ltd', code: 'TECH001', email: 'tech@example.com', phone: '123-456-7890', address: 'Tech Street', is_active: true, created_at: '2024-01-01', updated_at: undefined },
  { id: 2, name: 'Trends', code: 'TREND001', email: 'trends@example.com', phone: '098-765-4321', address: 'Trends Avenue', is_active: true, created_at: '2024-01-01', updated_at: undefined },
  { id: 3, name: 'Camel', code: 'CAMEL001', email: 'camel@example.com', phone: '555-123-4567', address: 'Camel Road', is_active: true, created_at: '2024-01-01', updated_at: undefined },
];

const mockProducts: Product[] = [
  { id: 1, name: 'Laptop', description: 'High-end laptop', sku: 'LAP001', brand: 'Dell', model: 'XPS 13', price: 120000, cost: 100000, weight: 1.5, dimensions: { length: 30, width: 20, height: 2 }, specifications: { color: 'Silver', material: 'Aluminum' }, barcode: '123456789', is_active: true, category_id: 1, supplier_id: 1, min_stock_level: 5, max_stock_level: 50, reorder_point: 10, created_at: '2024-01-01', updated_at: undefined },
  { id: 2, name: 'Shirt', description: 'Cotton shirt', sku: 'SHR001', brand: 'Nike', model: 'Classic', price: 900, cost: 600, weight: 0.2, dimensions: { length: 70, width: 50, height: 1 }, specifications: { color: 'Blue', material: 'Cotton' }, barcode: '987654321', is_active: true, category_id: 2, supplier_id: 2, min_stock_level: 10, max_stock_level: 100, reorder_point: 20, created_at: '2024-01-01', updated_at: undefined },
];

const mockUser = {
  id: 1,
  username: 'admin',
  email: 'admin@example.com',
  is_active: true,
  can_approve_po: true,
  can_cancel_po: true,
  can_receive_po: true,
  can_edit_po: true,
  created_at: '2024-01-01',
  updated_at: undefined,
};

describe('PurchaseOrder Filtering', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    // Setup mock responses
    (mockApiService.users.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
    (mockApiService.suppliers.getSuppliers as jest.Mock).mockResolvedValue({
      data: mockSuppliers,
      total: mockSuppliers.length,
      page: 1,
      size: 10,
    });
    (mockApiService.products.getProducts as jest.Mock).mockResolvedValue({
      data: mockProducts,
      total: mockProducts.length,
      page: 1,
      size: 10,
    });
    (mockApiService.purchaseOrders.getPurchaseOrders as jest.Mock).mockResolvedValue({
      data: [],
      total: 0,
      page: 1,
      size: 10,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('should show "Please select a supplier first" when no supplier is selected', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PurchaseOrders />
      </QueryClientProvider>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Purchase Orders')).toBeInTheDocument();
    });

    // Click create button to open modal
    const createButton = screen.getByText('Create Purchase Order');
    fireEvent.click(createButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Create Purchase Order')).toBeInTheDocument();
    });

    // Check that the product dropdown shows the correct message
    const productDropdown = screen.getByDisplayValue('Please select a supplier first');
    expect(productDropdown).toBeInTheDocument();
  });

  test('should filter products when supplier is selected', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PurchaseOrders />
      </QueryClientProvider>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Purchase Orders')).toBeInTheDocument();
    });

    // Click create button to open modal
    const createButton = screen.getByText('Create Purchase Order');
    fireEvent.click(createButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Create Purchase Order')).toBeInTheDocument();
    });

    // Select a supplier
    const supplierDropdown = screen.getByDisplayValue('Select supplier');
    fireEvent.change(supplierDropdown, { target: { value: '1' } });

    // Wait for the product dropdown to update
    await waitFor(() => {
      expect(screen.getByDisplayValue('Select product')).toBeInTheDocument();
    });

    // Check that only products from the selected supplier are shown
    const productDropdown = screen.getByDisplayValue('Select product');
    fireEvent.click(productDropdown);

    // Should only show products from supplier 1 (Tech Supplies Ltd)
    expect(screen.getByText('Laptop ($120000)')).toBeInTheDocument();
    expect(screen.queryByText('Shirt ($900)')).not.toBeInTheDocument();
  });

  test('should show "No products available" for supplier with no products', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PurchaseOrders />
      </QueryClientProvider>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Purchase Orders')).toBeInTheDocument();
    });

    // Click create button to open modal
    const createButton = screen.getByText('Create Purchase Order');
    fireEvent.click(createButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Create Purchase Order')).toBeInTheDocument();
    });

    // Select supplier 3 (Camel) which has no products
    const supplierDropdown = screen.getByDisplayValue('Select supplier');
    fireEvent.change(supplierDropdown, { target: { value: '3' } });

    // Wait for the product dropdown to update
    await waitFor(() => {
      expect(screen.getByDisplayValue('No products available for this supplier')).toBeInTheDocument();
    });

    // Check that the message is displayed
    expect(screen.getByText('No products are available for the selected supplier')).toBeInTheDocument();
  });

  test('should disable "Add Item" button when no supplier is selected', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PurchaseOrders />
      </QueryClientProvider>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Purchase Orders')).toBeInTheDocument();
    });

    // Click create button to open modal
    const createButton = screen.getByText('Create Purchase Order');
    fireEvent.click(createButton);

    // Wait for modal to open
    await waitFor(() => {
      expect(screen.getByText('Create Purchase Order')).toBeInTheDocument();
    });

    // Check that Add Item button is disabled
    const addItemButton = screen.getByText('Add Item');
    expect(addItemButton).toBeDisabled();
  });
}); 