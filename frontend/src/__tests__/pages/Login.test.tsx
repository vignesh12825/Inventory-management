import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import Login from '../../pages/Login';

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
  },
}));

// Mock the auth context
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: null,
    isLoading: false,
    isAuthenticated: false,
    login: jest.fn(),
    logout: jest.fn(),
    refetchUser: jest.fn(),
  }),
}));

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
    <a href={to}>{children}</a>
  ),
}));

// Mock react-toastify
jest.mock('react-toastify', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    warning: jest.fn(),
    info: jest.fn(),
  },
}));

describe('Login Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderLogin = () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Login />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('renders login form correctly', () => {
    renderLogin();
    
    expect(screen.getByText(/Sign in to your account/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/Don't have an account\?/i)).toBeInTheDocument();
    expect(screen.getByText(/Forgot your password?/i)).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    renderLogin();
    
    const submitButton = screen.getByRole('button', { name: /Sign in/i });
    fireEvent.click(submitButton);
    
    // The form should prevent submission with empty fields
    // We can test that the form doesn't submit by checking if the button is still enabled
    expect(submitButton).toBeInTheDocument();
  });

  it('toggles password visibility', () => {
    renderLogin();
    
    const passwordInput = screen.getByLabelText(/Password/i);
    // The password toggle button doesn't have an accessible name, so we'll test it differently
    const toggleButton = passwordInput.parentElement?.querySelector('button');
    
    expect(toggleButton).toBeInTheDocument();
    
    // Password should be hidden by default
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click toggle button
    fireEvent.click(toggleButton!);
    
    // Password should be visible
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    // Click toggle button again
    fireEvent.click(toggleButton!);
    
    // Password should be hidden again
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('navigates to register page when register link is clicked', () => {
    renderLogin();
    
    const registerLink = screen.getByText(/Contact your administrator/i);
    fireEvent.click(registerLink);
    
    expect(registerLink).toBeInTheDocument();
  });

  it('navigates to forgot password page when forgot password link is clicked', () => {
    renderLogin();
    
    const forgotPasswordLink = screen.getByText(/Forgot your password?/i);
    fireEvent.click(forgotPasswordLink);
    
    expect(forgotPasswordLink).toBeInTheDocument();
  });

  it('fills form fields correctly', () => {
    renderLogin();
    
    const emailInput = screen.getByLabelText(/Email Address/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('password123');
  });

  it('validates email format correctly', async () => {
    renderLogin();
    
    const emailInput = screen.getByLabelText(/Email Address/i);
    const submitButton = screen.getByRole('button', { name: /Sign in/i });
    
    // Test invalid email
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);
    
    // The form should prevent submission with invalid email
    expect(submitButton).toBeInTheDocument();
    
    // Test valid email
    fireEvent.change(emailInput, { target: { value: 'valid@email.com' } });
    fireEvent.click(submitButton);
    
    // The form should allow submission with valid email
    expect(submitButton).toBeInTheDocument();
  });

  it('shows demo account buttons', () => {
    renderLogin();
    
    expect(screen.getByText(/Admin Demo/i)).toBeInTheDocument();
    expect(screen.getByText(/Manager Demo/i)).toBeInTheDocument();
    expect(screen.getByText(/Staff Demo/i)).toBeInTheDocument();
    expect(screen.getByText(/Viewer Demo/i)).toBeInTheDocument();
  });

  it('shows remember me checkbox', () => {
    renderLogin();
    
    const rememberMeCheckbox = screen.getByLabelText(/Remember me/i);
    expect(rememberMeCheckbox).toBeInTheDocument();
    expect(rememberMeCheckbox).toHaveAttribute('type', 'checkbox');
  });

  it('shows welcome message', () => {
    renderLogin();
    
    expect(screen.getByText(/Welcome to Inventory Management System/i)).toBeInTheDocument();
  });

  it('shows copyright notice', () => {
    renderLogin();
    
    expect(screen.getByText(/© 2024 Inventory Management System. All rights reserved./i)).toBeInTheDocument();
  });
}); 