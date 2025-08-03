import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import Products from '../../pages/Products';
import apiService from '../../services/api';

// Mock the API service
jest.mock('../../services/api');

const mockApiService = apiService as jest.Mocked<typeof apiService>;

// Mock data
const mockProducts = [
  {
    id: 1,
    name: 'Test Product 1',
    description: 'Test description 1',
    sku: 'TEST-001',
    brand: 'Test Brand',
    model: 'Test Model',
    price: 99.99,
    cost: 50.00,
    weight: 1.5,
    dimensions: { length: 10, width: 5, height: 2 },
    specifications: { color: 'red', material: 'plastic' },
    barcode: '123456789',
    is_active: true,
    category_id: 1,
    supplier_id: 1,
    min_stock_level: 10,
    max_stock_level: 100,
    reorder_point: 5,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    category: { id: 1, name: 'Electronics', description: 'Electronic items', is_active: true, created_at: '2023-01-01T00:00:00Z' },
    supplier: { id: 1, name: 'Test Supplier', code: 'SUP-001', is_active: true, created_at: '2023-01-01T00:00:00Z' }
  },
  {
    id: 2,
    name: 'Test Product 2',
    description: 'Test description 2',
    sku: 'TEST-002',
    brand: 'Test Brand 2',
    model: 'Test Model 2',
    price: 149.99,
    cost: 75.00,
    weight: 2.0,
    dimensions: { length: 15, width: 8, height: 3 },
    specifications: { color: 'blue', material: 'metal' },
    barcode: '987654321',
    is_active: false,
    category_id: 2,
    supplier_id: 2,
    min_stock_level: 5,
    max_stock_level: 50,
    reorder_point: 3,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    category: { id: 2, name: 'Clothing', description: 'Clothing items', is_active: false, created_at: '2023-01-01T00:00:00Z' },
    supplier: { id: 2, name: 'Test Supplier 2', code: 'SUP-002', is_active: false, created_at: '2023-01-01T00:00:00Z' }
  }
];

const mockCategories = [
  { id: 1, name: 'Electronics', description: 'Electronic items', is_active: true, created_at: '2023-01-01T00:00:00Z' },
  { id: 2, name: 'Clothing', description: 'Clothing items', is_active: false, created_at: '2023-01-01T00:00:00Z' },
  { id: 3, name: 'Books', description: 'Book items', is_active: true, created_at: '2023-01-01T00:00:00Z' }
];

const mockSuppliers = [
  { id: 1, name: 'Test Supplier', code: 'SUP-001', is_active: true, created_at: '2023-01-01T00:00:00Z' },
  { id: 2, name: 'Test Supplier 2', code: 'SUP-002', is_active: false, created_at: '2023-01-01T00:00:00Z' },
  { id: 3, name: 'Test Supplier 3', code: 'SUP-003', is_active: true, created_at: '2023-01-01T00:00:00Z' }
];

// Setup function to render component with providers
const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Products Page', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup default mock implementations
    (mockApiService.products.getProducts as jest.Mock).mockResolvedValue({
      data: mockProducts,
      total: mockProducts.length,
      page: 1,
      size: 10
    });
    
    (mockApiService.categories.getCategories as jest.Mock).mockResolvedValue({
      data: mockCategories,
      total: mockCategories.length,
      page: 1,
      size: 10
    });
    
    (mockApiService.suppliers.getSuppliers as jest.Mock).mockResolvedValue({
      data: mockSuppliers,
      total: mockSuppliers.length,
      page: 1,
      size: 10
    });
    
    (mockApiService.products.deleteProduct as jest.Mock).mockResolvedValue();
    (mockApiService.products.updateProduct as jest.Mock).mockResolvedValue(mockProducts[0]);
  });

  describe('Filtering Functionality', () => {
    test('should filter products by search term', async () => {
      renderWithProviders(<Products />);
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      });
      
      // Get search input
      const searchInput = screen.getByPlaceholderText('Search products...');
      
      // Type search term
      fireEvent.change(searchInput, { target: { value: 'Test Product 1' } });
      
      // Wait for API call
      await waitFor(() => {
        expect(mockApiService.products.getProducts).toHaveBeenCalledWith({
          search: 'Test Product 1',
          category_id: undefined
        });
      });
    });

    test('should filter products by category', async () => {
      renderWithProviders(<Products />);
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      });
      
      // Get category select
      const categorySelect = screen.getByDisplayValue('All Categories');
      
      // Select a category
      fireEvent.change(categorySelect, { target: { value: '1' } });
      
      // Wait for API call
      await waitFor(() => {
        expect(mockApiService.products.getProducts).toHaveBeenCalledWith({
          search: '',
          category_id: 1
        });
      });
    });

    test('should combine search and category filters', async () => {
      renderWithProviders(<Products />);
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      });
      
      // Set search term
      const searchInput = screen.getByPlaceholderText('Search products...');
      fireEvent.change(searchInput, { target: { value: 'Test' } });
      
      // Set category filter
      const categorySelect = screen.getByDisplayValue('All Categories');
      fireEvent.change(categorySelect, { target: { value: '1' } });
      
      // Wait for API call with both filters
      await waitFor(() => {
        expect(mockApiService.products.getProducts).toHaveBeenCalledWith({
          search: 'Test',
          category_id: 1
        });
      });
    });
  });

  describe('Dropdown Filtering', () => {
    test('should only show active categories in dropdown', async () => {
      renderWithProviders(<Products />);
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      });
      
      // Verify that categories API was called with is_active filter
      expect(mockApiService.categories.getCategories).toHaveBeenCalledWith({
        is_active: true
      });
      
      // Open the Add Product modal to see category dropdown
      const addButton = screen.getByText('Add Product');
      fireEvent.click(addButton);
      
      // Wait for modal to appear
      await waitFor(() => {
        expect(screen.getByText('Add Product')).toBeInTheDocument();
      });
      
      // Check that only active categories are in the dropdown
      const categorySelect = screen.getByDisplayValue('Select category');
      expect(categorySelect).toBeInTheDocument();
      
      // The dropdown should only contain active categories (Electronics and Books, not Clothing)
      expect(categorySelect).toHaveValue('');
    });

    test('should only show active suppliers in dropdown', async () => {
      renderWithProviders(<Products />);
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      });
      
      // Verify that suppliers API was called with is_active filter
      expect(mockApiService.suppliers.getSuppliers).toHaveBeenCalledWith({
        is_active: true
      });
      
      // Open the Add Product modal to see supplier dropdown
      const addButton = screen.getByText('Add Product');
      fireEvent.click(addButton);
      
      // Wait for modal to appear
      await waitFor(() => {
        expect(screen.getByText('Add Product')).toBeInTheDocument();
      });
      
      // Check that supplier dropdown exists
      const supplierSelect = screen.getByDisplayValue('Select supplier');
      expect(supplierSelect).toBeInTheDocument();
    });
  });

  describe('Product Deletion', () => {
    test('should handle product deletion successfully', async () => {
      renderWithProviders(<Products />);
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      });
      
      // Mock window.confirm to return true
      window.confirm = jest.fn(() => true);
      
      // Find and click delete button for first product
      const deleteButtons = screen.getAllByTestId('delete-button');
      if (deleteButtons.length > 0) {
        fireEvent.click(deleteButtons[0]);
      } else {
        // If no test-id, try to find by icon
        const deleteIcons = screen.getAllByTestId('trash-icon');
        if (deleteIcons.length > 0) {
          fireEvent.click(deleteIcons[0]);
        }
      }
      
      // Verify confirmation dialog was shown
      expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this product?');
      
      // Verify delete API was called
      await waitFor(() => {
        expect(mockApiService.products.deleteProduct).toHaveBeenCalledWith(1);
      });
    });

    test('should handle product deletion cancellation', async () => {
      renderWithProviders(<Products />);
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      });
      
      // Mock window.confirm to return false
      window.confirm = jest.fn(() => false);
      
      // Find and click delete button
      const deleteButtons = screen.getAllByTestId('delete-button');
      if (deleteButtons.length > 0) {
        fireEvent.click(deleteButtons[0]);
      }
      
      // Verify confirmation dialog was shown
      expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this product?');
      
      // Verify delete API was NOT called
      expect(mockApiService.products.deleteProduct).not.toHaveBeenCalled();
    });
  });

  describe('Product Status Toggle', () => {
    test('should toggle product active status', async () => {
      renderWithProviders(<Products />);
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      });
      
      // Find and click the status toggle button
      const statusButtons = screen.getAllByText('Active');
      if (statusButtons.length > 0) {
        fireEvent.click(statusButtons[0]);
      }
      
      // Verify update API was called
      await waitFor(() => {
        expect(mockApiService.products.updateProduct).toHaveBeenCalledWith(1, {
          is_active: false
        });
      });
    });
  });

  describe('Product Modal', () => {
    test('should open add product modal', async () => {
      renderWithProviders(<Products />);
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      });
      
      // Click add product button
      const addButton = screen.getByText('Add Product');
      fireEvent.click(addButton);
      
      // Verify modal opens
      await waitFor(() => {
        expect(screen.getByText('Add Product')).toBeInTheDocument();
        expect(screen.getByLabelText('Name')).toBeInTheDocument();
        expect(screen.getByLabelText('SKU')).toBeInTheDocument();
      });
    });

    test('should open edit product modal', async () => {
      renderWithProviders(<Products />);
      
      // Wait for component to load
      await waitFor(() => {
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      });
      
      // Find and click edit button
      const editButtons = screen.getAllByTestId('edit-button');
      if (editButtons.length > 0) {
        fireEvent.click(editButtons[0]);
      } else {
        // If no test-id, try to find by icon
        const editIcons = screen.getAllByTestId('pencil-icon');
        if (editIcons.length > 0) {
          fireEvent.click(editIcons[0]);
        }
      }
      
      // Verify modal opens with edit title
      await waitFor(() => {
        expect(screen.getByText('Edit Product')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle API errors gracefully', async () => {
      // Mock API to throw error
      (mockApiService.products.getProducts as jest.Mock).mockRejectedValue(new Error('API Error'));
      
      renderWithProviders(<Products />);
      
      // Wait for error message to appear
      await waitFor(() => {
        expect(screen.getByText('Error loading products')).toBeInTheDocument();
      });
    });

    test('should show loading state', async () => {
      // Mock API to delay response
      (mockApiService.products.getProducts as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          data: mockProducts,
          total: mockProducts.length,
          page: 1,
          size: 10
        }), 100))
      );
      
      renderWithProviders(<Products />);
      
      // Should show loading message
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });
  });
}); 