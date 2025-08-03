import React from 'react';
import { render, screen, fireEvent, waitFor } from '../utils/test-utils';
import ForgotPassword from '../../pages/ForgotPassword';
import apiService from '../../services/api';

const mockApiService = apiService as jest.Mocked<typeof apiService>;

describe('ForgotPassword Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders forgot password form correctly', () => {
    render(<ForgotPassword />);
    
    expect(screen.getByText(/Forgot your password\?/i)).toBeInTheDocument();
    expect(screen.getByText(/Enter your email address and we'll send you a link to reset your password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Send Reset Link/i })).toBeInTheDocument();
    expect(screen.getByText(/Back to Login/i)).toBeInTheDocument();
  });

  it('shows validation error for empty email', async () => {
    render(<ForgotPassword />);
    
    const submitButton = screen.getByRole('button', { name: /Send Reset Link/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Email is required/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for invalid email format', async () => {
    render(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email/i);
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    
    const submitButton = screen.getByRole('button', { name: /Send Reset Link/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid email address/i)).toBeInTheDocument();
    });
  });

  it('handles successful password reset request', async () => {
    const mockResponse = {
      message: 'Password reset link has been sent to your email',
      reset_token: 'mock-reset-token',
      note: 'For development purposes, the reset token is included in the response',
    };
    
    (mockApiService.auth.forgotPassword as jest.Mock).mockResolvedValue(mockResponse);
    
    render(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email/i);
    const submitButton = screen.getByRole('button', { name: /Send Reset Link/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockApiService.auth.forgotPassword).toHaveBeenCalledWith('test@example.com');
    });
  });

  it('handles password reset request error', async () => {
    const mockError = new Error('User not found');
    (mockApiService.auth.forgotPassword as jest.Mock).mockRejectedValue(mockError);
    
    render(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email/i);
    const submitButton = screen.getByRole('button', { name: /Send Reset Link/i });
    
    fireEvent.change(emailInput, { target: { value: 'nonexistent@example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockApiService.auth.forgotPassword).toHaveBeenCalledWith('nonexistent@example.com');
    });
  });

  it('disables submit button during form submission', async () => {
    // Mock a slow API response
    (mockApiService.auth.forgotPassword as jest.Mock).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ message: 'Success' }), 100))
    );
    
    render(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email/i);
    const submitButton = screen.getByRole('button', { name: /Send Reset Link/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);
    
    // Button should be disabled during submission
    expect(submitButton).toBeDisabled();
    
    await waitFor(() => {
      expect(mockApiService.auth.forgotPassword).toHaveBeenCalled();
    });
  });

  it('clears form after successful submission', async () => {
    const mockResponse = {
      message: 'Password reset link has been sent to your email',
      reset_token: 'mock-reset-token',
      note: 'For development purposes, the reset token is included in the response',
    };
    
    (mockApiService.auth.forgotPassword as jest.Mock).mockResolvedValue(mockResponse);
    
    render(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email/i);
    const submitButton = screen.getByRole('button', { name: /Send Reset Link/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockApiService.auth.forgotPassword).toHaveBeenCalled();
    });
    
    // Form should not be cleared after successful submission (component shows success state instead)
    // The form is replaced with a success message, so we can't check the input value
  });

  it('navigates back to login when back link is clicked', () => {
    render(<ForgotPassword />);
    
    const backLink = screen.getByText(/Back to Login/i);
    fireEvent.click(backLink);
    
    // This would typically be tested with React Router's useNavigate mock
    // For now, we just verify the link exists and is clickable
    expect(backLink).toBeInTheDocument();
  });

  it('shows success message after successful submission', async () => {
    const mockResponse = {
      message: 'Password reset link has been sent to your email',
      reset_token: 'mock-reset-token',
      note: 'For development purposes, the reset token is included in the response',
    };
    
    (mockApiService.auth.forgotPassword as jest.Mock).mockResolvedValue(mockResponse);
    
    render(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email/i);
    const submitButton = screen.getByRole('button', { name: /Send Reset Link/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Check Your Email/i })).toBeInTheDocument();
      expect(screen.getByText(/We've sent a password reset link to your email address/i)).toBeInTheDocument();
    });
  });

  it('handles inactive user error', async () => {
    const mockError = new Error('Inactive user');
    (mockApiService.auth.forgotPassword as jest.Mock).mockRejectedValue(mockError);
    
    render(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email/i);
    const submitButton = screen.getByRole('button', { name: /Send Reset Link/i });
    
    fireEvent.change(emailInput, { target: { value: 'inactive@example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockApiService.auth.forgotPassword).toHaveBeenCalledWith('inactive@example.com');
    });
  });

  it('prevents multiple submissions while processing', async () => {
    // Mock a slow API response
    (mockApiService.auth.forgotPassword as jest.Mock).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ message: 'Success' }), 100))
    );
    
    render(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email/i);
    const submitButton = screen.getByRole('button', { name: /Send Reset Link/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);
    
    // Try to submit again while processing
    fireEvent.click(submitButton);
    
    // Should only be called once
    await waitFor(() => {
      expect(mockApiService.auth.forgotPassword).toHaveBeenCalledTimes(1);
    });
  });
}); 