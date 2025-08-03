import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useQuery } from 'react-query';
import apiService from '../services/api';

interface NotificationContextType {
  activeAlertsCount: number;
  unreadAlertsCount: number;
  refreshAlerts: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [activeAlertsCount, setActiveAlertsCount] = useState(0);
  const [unreadAlertsCount, setUnreadAlertsCount] = useState(0);

  // Fetch active alerts count
  const { data: activeAlertsData, refetch: refreshAlerts } = useQuery(
    ['active-alerts-count'],
    () => apiService.stockAlerts.getActiveAlerts(),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      onSuccess: (data) => {
        setActiveAlertsCount(data?.length || 0);
        setUnreadAlertsCount(data?.length || 0);
      },
    }
  );

  // Listen for WebSocket notifications
  useEffect(() => {
    const handleStockAlert = (event: CustomEvent) => {
      const alertData = event.detail;
      console.log('Received stock alert via WebSocket:', alertData);
      
      // Increment the count for new alerts
      setActiveAlertsCount(prev => prev + 1);
      setUnreadAlertsCount(prev => prev + 1);
      
      // Refresh the alerts data
      refreshAlerts();
    };

    const handleAlertResolved = (event: CustomEvent) => {
      const alertData = event.detail;
      console.log('Alert resolved via WebSocket:', alertData);
      
      // Decrement the count for resolved alerts
      setActiveAlertsCount(prev => Math.max(0, prev - 1));
      setUnreadAlertsCount(prev => Math.max(0, prev - 1));
      
      // Refresh the alerts data
      refreshAlerts();
    };

    // Add event listeners
    window.addEventListener('stockAlert', handleStockAlert as EventListener);
    window.addEventListener('alertResolved', handleAlertResolved as EventListener);

    // Cleanup
    return () => {
      window.removeEventListener('stockAlert', handleStockAlert as EventListener);
      window.removeEventListener('alertResolved', handleAlertResolved as EventListener);
    };
  }, [refreshAlerts]);

  const value: NotificationContextType = {
    activeAlertsCount,
    unreadAlertsCount,
    refreshAlerts,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}; 