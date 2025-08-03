import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
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

describe('Users Page', () => {
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

  describe('User List Display', () => {
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
  });

  describe('User Creation', () => {
    it('should open create user modal when Create User button is clicked', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Create User')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Create User'));

      // Check if modal form elements are present
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/role/i)).toBeInTheDocument();
    });

    it('should create user successfully', async () => {
      const newUser = {
        id: 3,
        email: 'newuser@example.com',
        username: 'newuser',
        full_name: 'New User',
        role: UserRole.STAFF,
        department: 'Testing',
        phone: '+1234567890',
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
      };

      (mockApiService.users.createUser as jest.Mock).mockResolvedValue(newUser);

      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Create User')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Create User'));

      // Fill form
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: 'newuser@example.com' },
      });
      fireEvent.change(screen.getByLabelText(/username/i), {
        target: { value: 'newuser' },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: 'password123' },
      });
      fireEvent.change(screen.getByLabelText(/full name/i), {
        target: { value: 'New User' },
      });

      // Submit form
      fireEvent.click(screen.getByText('Create'));

      await waitFor(() => {
        expect(mockApiService.users.createUser).toHaveBeenCalledWith({
          email: 'newuser@example.com',
          username: 'newuser',
          password: 'password123',
          full_name: 'New User',
          role: UserRole.STAFF,
          department: '',
          phone: '',
          is_active: true,
        });
      });
    });
  });

  describe('User Editing', () => {
    it('should open edit modal when edit button is clicked', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Staff User')).toBeInTheDocument();
      });

      // Find and click edit button for staff user
      const editButtons = screen.getAllByTestId('edit-button');
      fireEvent.click(editButtons[1]); // Second user (staff)

      // Check if modal opens with user data
      expect(screen.getByDisplayValue('staff@example.com')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Staff User')).toBeInTheDocument();
    });

    it('should update user successfully', async () => {
      const updatedUser = { ...mockUsers[1], full_name: 'Updated Staff User' };
      (mockApiService.users.updateUser as jest.Mock).mockResolvedValue(updatedUser);

      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Staff User')).toBeInTheDocument();
      });

      // Open edit modal
      const editButtons = screen.getAllByTestId('edit-button');
      fireEvent.click(editButtons[1]);

      // Update form
      fireEvent.change(screen.getByLabelText(/full name/i), {
        target: { value: 'Updated Staff User' },
      });

      // Submit form
      fireEvent.click(screen.getByText('Update'));

      await waitFor(() => {
        expect(mockApiService.users.updateUser).toHaveBeenCalledWith(2, {
          email: 'staff@example.com',
          username: 'staff',
          full_name: 'Updated Staff User',
          role: UserRole.STAFF,
          department: 'Operations',
          phone: '+0987654321',
          is_active: true,
        });
      });
    });
  });

  describe('User Deletion', () => {
    it('should show confirmation dialog when delete button is clicked', async () => {
      const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(false);

      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Staff User')).toBeInTheDocument();
      });

      // Find and click delete button
      const deleteButtons = screen.getAllByTestId('delete-button');
      fireEvent.click(deleteButtons[1]); // Second user (staff)

      expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this user?');
      confirmSpy.mockRestore();
    });

    it('should delete user when confirmed', async () => {
      const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
      (mockApiService.users.deleteUser as jest.Mock).mockResolvedValue({});

      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Staff User')).toBeInTheDocument();
      });

      // Find and click delete button
      const deleteButtons = screen.getAllByTestId('delete-button');
      fireEvent.click(deleteButtons[1]);

      await waitFor(() => {
        expect(mockApiService.users.deleteUser).toHaveBeenCalledWith(2);
      });

      confirmSpy.mockRestore();
    });
  });

  describe('Search and Filtering', () => {
    it('should filter users by search term', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Admin User')).toBeInTheDocument();
        expect(screen.getByText('Staff User')).toBeInTheDocument();
      });

      // Search for admin
      const searchInput = screen.getByPlaceholderText(/search users/i);
      fireEvent.change(searchInput, { target: { value: 'admin' } });

      // Should only show admin user
      expect(screen.getByText('Admin User')).toBeInTheDocument();
      expect(screen.queryByText('Staff User')).not.toBeInTheDocument();
    });

    it('should filter users by role', async () => {
      renderWithQueryClient(<Users />);

      await waitFor(() => {
        expect(screen.getByText('Admin User')).toBeInTheDocument();
        expect(screen.getByText('Staff User')).toBeInTheDocument();
      });

      // Filter by staff role
      const roleFilter = screen.getByLabelText(/role filter/i);
      fireEvent.change(roleFilter, { target: { value: 'staff' } });

      // Should only show staff user
      expect(screen.queryByText('Admin User')).not.toBeInTheDocument();
      expect(screen.getByText('Staff User')).toBeInTheDocument();
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
}); 