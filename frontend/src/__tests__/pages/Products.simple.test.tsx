import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import Products from '../../pages/Products';

// Mock the API service
jest.mock('../../services/api', () => ({
  products: {
    getProducts: jest.fn(),
    createProduct: jest.fn(),
    updateProduct: jest.fn(),
    deleteProduct: jest.fn(),
  },
  categories: {
    getCategories: jest.fn(),
  },
  suppliers: {
    getSuppliers: jest.fn(),
  },
}));

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

describe('Products Page - Basic Functionality', () => {
  test('should render products page with title', () => {
    renderWithProviders(<Products />);
    expect(screen.getByText('Products')).toBeInTheDocument();
  });

  test('should render add product button', () => {
    renderWithProviders(<Products />);
    expect(screen.getByText('Add Product')).toBeInTheDocument();
  });

  test('should render search input', () => {
    renderWithProviders(<Products />);
    expect(screen.getByPlaceholderText('Search products...')).toBeInTheDocument();
  });

  test('should render category filter dropdown', () => {
    renderWithProviders(<Products />);
    expect(screen.getByDisplayValue('All Categories')).toBeInTheDocument();
  });
}); 