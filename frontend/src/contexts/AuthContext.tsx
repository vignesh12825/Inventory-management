import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import apiService from '../services/api';
import { UserWithPermissions } from '../types';
import { websocketService } from '../services/websocket';

interface AuthContextType {
  user: UserWithPermissions | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (token: string, userData: UserWithPermissions) => void;
  logout: () => void;
  refetchUser: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const queryClient = useQueryClient();

  const { data: user, isLoading, refetch } = useQuery(
    ['currentUser', localStorage.getItem('access_token')],
    apiService.users.getCurrentUser,
    {
      retry: false,
      enabled: !!localStorage.getItem('access_token'),
      onSuccess: (data) => {
        console.log('AuthContext: User data received successfully:', data.username);
        setIsAuthenticated(true);
        // Connect WebSocket for real-time alerts
        websocketService.connect(data.id);
      },
      onError: (error: any) => {
        console.error('AuthContext error:', error);
        console.error('AuthContext error details:', error.response?.data);
        setIsAuthenticated(false);
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        // Disconnect WebSocket on error
        websocketService.disconnect();
      },
    }
  );

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      console.log('Token found in localStorage, setting authenticated state');
      setIsAuthenticated(true);
    } else {
      console.log('No token found in localStorage');
    }
  }, []);

  const login = (token: string, userData: UserWithPermissions) => {
    // Clear any cached user data before setting new user
    queryClient.removeQueries(['currentUser']);
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setIsAuthenticated(true);
  };

  const logout = () => {
    // Clear cached user data on logout
    queryClient.removeQueries(['currentUser']);
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    // Disconnect WebSocket on logout
    websocketService.disconnect();
    window.location.href = '/login';
  };

  const refetchUser = () => {
    // Clear cache and refetch fresh data
    queryClient.removeQueries(['currentUser']);
    refetch();
  };

  const value: AuthContextType = {
    user: user || null,
    isLoading,
    isAuthenticated,
    login,
    logout,
    refetchUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 