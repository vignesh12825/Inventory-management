import React, { useState } from 'react';
import { useMutation, useQuery } from 'react-query';
import { toast } from 'react-toastify';
import { EyeIcon, EyeSlashIcon, UserIcon, EnvelopeIcon, BuildingOfficeIcon, PhoneIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import { UserWithPermissions } from '../types';

interface PasswordChangeData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

const Profile: React.FC = () => {
  const { user, refetchUser } = useAuth();
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordData, setPasswordData] = useState<PasswordChangeData>({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Use user from AuthContext
  const currentUser = user;

  const changePasswordMutation = useMutation(
    (data: { current_password: string; new_password: string }) =>
      apiService.users.changePassword(data),
    {
      onSuccess: () => {
        toast.success('Password changed successfully!');
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_password: '',
        });
        setErrors({});
      },
      onError: (error: any) => {
        const errorMessage = error.response?.data?.detail || 'Failed to change password.';
        toast.error(errorMessage);
      },
    }
  );

  const validatePasswordForm = () => {
    const newErrors: Record<string, string> = {};

    if (!passwordData.current_password) {
      newErrors.current_password = 'Current password is required';
    }

    if (!passwordData.new_password) {
      newErrors.new_password = 'New password is required';
    } else if (passwordData.new_password.length < 6) {
      newErrors.new_password = 'New password must be at least 6 characters';
    }

    if (!passwordData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your new password';
    } else if (passwordData.new_password !== passwordData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault();
    if (validatePasswordForm()) {
      changePasswordMutation.mutate({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });
    }
  };

  const handlePasswordInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value,
    }));
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const getRoleDescription = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return 'Full system access - can manage users, approve orders, and access all features';
      case 'MANAGER':
        return 'Management access - can approve orders, manage inventory, and view reports';
      case 'STAFF':
        return 'Staff access - can create orders, receive items, and manage basic operations';
      case 'VIEWER':
        return 'Read-only access - can only view data and reports';
      default:
        return '';
    }
  };

  if (!currentUser) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Profile</h1>
          <p className="text-sm text-gray-600 mt-1">
            Manage your account information and security settings
          </p>
        </div>
        <button
          onClick={() => refetchUser()}
          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profile Information */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h2>
          
          <div className="space-y-4">
                         <div className="flex items-center">
               <UserIcon className="h-5 w-5 text-gray-400 mr-3" />
               <div>
                 <p className="text-sm font-medium text-gray-900">Full Name</p>
                 <p className="text-sm text-gray-600">{currentUser.full_name || 'Not provided'}</p>
               </div>
             </div>

             <div className="flex items-center">
               <EnvelopeIcon className="h-5 w-5 text-gray-400 mr-3" />
               <div>
                 <p className="text-sm font-medium text-gray-900">Email</p>
                 <p className="text-sm text-gray-600">{currentUser.email}</p>
               </div>
             </div>

             <div className="flex items-center">
               <UserIcon className="h-5 w-5 text-gray-400 mr-3" />
               <div>
                 <p className="text-sm font-medium text-gray-900">Username</p>
                 <p className="text-sm text-gray-600">{currentUser.username}</p>
               </div>
             </div>

             <div className="flex items-center">
               <BuildingOfficeIcon className="h-5 w-5 text-gray-400 mr-3" />
               <div>
                 <p className="text-sm font-medium text-gray-900">Department</p>
                 <p className="text-sm text-gray-600">{currentUser.department || 'Not assigned'}</p>
               </div>
             </div>

             <div className="flex items-center">
               <PhoneIcon className="h-5 w-5 text-gray-400 mr-3" />
               <div>
                 <p className="text-sm font-medium text-gray-900">Phone</p>
                 <p className="text-sm text-gray-600">{currentUser.phone || 'Not provided'}</p>
               </div>
             </div>

             <div className="flex items-center">
               <div className="h-5 w-5 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                 <span className="text-xs font-medium text-blue-600">
                   {currentUser.role?.charAt(0).toUpperCase()}
                 </span>
               </div>
               <div>
                 <p className="text-sm font-medium text-gray-900">Role</p>
                 <p className="text-sm text-gray-600 capitalize">{currentUser.role}</p>
                 <p className="text-xs text-gray-500 mt-1">
                   {getRoleDescription(currentUser.role)}
                 </p>
               </div>
             </div>

             <div className="flex items-center">
               <div className={`h-3 w-3 rounded-full mr-3 ${currentUser.is_active ? 'bg-green-400' : 'bg-red-400'}`}></div>
               <div>
                 <p className="text-sm font-medium text-gray-900">Status</p>
                 <p className="text-sm text-gray-600">
                   {currentUser.is_active ? 'Active' : 'Inactive'}
                 </p>
               </div>
             </div>
          </div>
        </div>

        {/* Change Password */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Change Password</h2>
          
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div>
              <label htmlFor="current_password" className="block text-sm font-medium text-gray-700 mb-1">
                Current Password
              </label>
              <div className="relative">
                <input
                  id="current_password"
                  name="current_password"
                  type={showCurrentPassword ? 'text' : 'password'}
                  required
                  className={`appearance-none relative block w-full pl-3 pr-10 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.current_password ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Enter current password"
                  value={passwordData.current_password}
                  onChange={handlePasswordInputChange}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                >
                  {showCurrentPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              {errors.current_password && (
                <p className="mt-1 text-sm text-red-600">{errors.current_password}</p>
              )}
            </div>

            <div>
              <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-1">
                New Password
              </label>
              <div className="relative">
                <input
                  id="new_password"
                  name="new_password"
                  type={showNewPassword ? 'text' : 'password'}
                  required
                  className={`appearance-none relative block w-full pl-3 pr-10 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.new_password ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Enter new password"
                  value={passwordData.new_password}
                  onChange={handlePasswordInputChange}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                >
                  {showNewPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              {errors.new_password && (
                <p className="mt-1 text-sm text-red-600">{errors.new_password}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm New Password
              </label>
              <div className="relative">
                <input
                  id="confirm_password"
                  name="confirm_password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  className={`appearance-none relative block w-full pl-3 pr-10 py-2 border rounded-md placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.confirm_password ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="Confirm new password"
                  value={passwordData.confirm_password}
                  onChange={handlePasswordInputChange}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              {errors.confirm_password && (
                <p className="mt-1 text-sm text-red-600">{errors.confirm_password}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={changePasswordMutation.isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {changePasswordMutation.isLoading ? 'Changing Password...' : 'Change Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile; 