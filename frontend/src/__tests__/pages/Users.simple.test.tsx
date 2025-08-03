import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import Users from '../../pages/Users';
import { UserWithPermissions, UserRole } from '../../types';

// Mock the API service
jest.mock('../../services/api', () => ({
  __esModule: true,
  default: {
    users: {
      getUsers: jest.fn(),
      createUser: jest.fn(),
      updateUser: jest.fn(),
      deleteUser: jest.fn(),
      getAvailableRoles: jest.fn(),
    },
  },
}));

// Import the mocked API service
import apiService from '../../services/api';
const mockApiService = apiService as jest.Mocked<typeof apiService>;

const mockUsers: UserWithPermissions[] = [
  {
    id: 1,
    email: 'admin@example.com',
    username: 'admin',
    full_name: 'Admin User',
    role: UserRole.ADMIN,
    department: 'IT',
    phone: '+1234567890',
    is_active: true,
    is_superuser: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: undefined,
    can_approve_po: true,
    can_cancel_po: true,
    can_receive_po: true,
    can_edit_po: true,
    can_manage_users: true,
    can_view_reports: true,
  },
  {
    id: 2,
    email: 'staff@example.com',
    username: 'staff',
    full_name: 'Staff User',
    role: UserRole.STAFF,
    department: 'Operations',
    phone: '+0987654321',
    is_active: true,
    is_superuser: false,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: undefined,
    can_approve_po: false,
    can_cancel_po: false,
    can_receive_po: true,
    can_edit_po: true,
    can_manage_users: false,
    can_view_reports: false,
  },
];

const mockRoles = ['admin', 'manager', 'staff', 'viewer'];

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('Users Page - Simple Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API responses
    (mockApiService.users.getUsers as jest.Mock).mockResolvedValue({
      data: mockUsers,
      total: mockUsers.length,
      page: 1,
      size: 10,
    });
    
    (mockApiService.users.getAvailableRoles as jest.Mock).mockResolvedValue(mockRoles);
  });

  describe('Basic Rendering', () => {
    it('should display users list correctly', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('User Management')).toBeInTheDocument();
        expect(screen.getByText('Create User')).toBeInTheDocument();
      });

      // Check if users are displayed
      expect(screen.getByText('Admin User')).toBeInTheDocument();
      expect(screen.getByText('Staff User')).toBeInTheDocument();
      expect(screen.getByText('admin@example.com')).toBeInTheDocument();
      expect(screen.getByText('staff@example.com')).toBeInTheDocument();
    });

    it('should display user statistics', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Total Users')).toBeInTheDocument();
        expect(screen.getByText('2')).toBeInTheDocument(); // Total users count
        expect(screen.getByText('Active Users')).toBeInTheDocument();
        expect(screen.getByText('Inactive Users')).toBeInTheDocument();
      });
    });

    it('should display user roles correctly', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('ADMIN')).toBeInTheDocument();
        expect(screen.getByText('STAFF')).toBeInTheDocument();
      });
    });

    it('should display user permissions as badges', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        // Admin user should have multiple permission badges
        expect(screen.getByText('Approve PO')).toBeInTheDocument();
        expect(screen.getByText('Cancel PO')).toBeInTheDocument();
        expect(screen.getByText('Manage Users')).toBeInTheDocument();
        expect(screen.getByText('View Reports')).toBeInTheDocument();
      });
    });

    it('should display action buttons for each user', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        // Should have edit and delete buttons for each user
        const editButtons = screen.getAllByTestId('edit-button');
        const deleteButtons = screen.getAllByTestId('delete-button');
        
        expect(editButtons).toHaveLength(2); // One for each user
        expect(deleteButtons).toHaveLength(2); // One for each user
      });
    });
  });

  describe('Search and Filtering', () => {
    it('should have search input field', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        const searchInput = screen.getByTestId('search-input');
        expect(searchInput).toBeInTheDocument();
        expect(searchInput).toHaveAttribute('placeholder', 'Search by name, email, username, or department...');
      });
    });

    it('should have role filter dropdown', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        const roleFilter = screen.getByTestId('role-filter');
        expect(roleFilter).toBeInTheDocument();
      });
    });

    it('should have clear filters button', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Clear Filters')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error message when API fails', async () => {
      (mockApiService.users.getUsers as jest.Mock).mockRejectedValue(
        new Error('Failed to fetch users')
      );

      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Error loading users')).toBeInTheDocument();
      });
    });

    it('should show loading state', async () => {
      (mockApiService.users.getUsers as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderWithQueryClient(<Users />);

      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });
  });

  describe('API Integration', () => {
    it('should call getUsers API on component mount', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(mockApiService.users.getUsers).toHaveBeenCalled();
      });
    });

    it('should call getAvailableRoles API on component mount', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(mockApiService.users.getAvailableRoles).toHaveBeenCalled();
      });
    });
  });
}); 