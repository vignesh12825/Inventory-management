import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { BellIcon, ExclamationTriangleIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import apiService from '../services/api';
import { StockAlert, AlertStatus, AlertType } from '../types';

const StockAlerts: React.FC = () => {
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const queryClient = useQueryClient();

  const { data: alertsData, isLoading, error } = useQuery(
    ['stock-alerts', selectedStatus, selectedType],
    () => apiService.stockAlerts.getStockAlerts({ 
      status: selectedStatus || undefined,
      alert_type: selectedType || undefined
    })
  );

  const { data: activeAlerts } = useQuery(
    ['active-alerts'],
    () => apiService.stockAlerts.getActiveAlerts()
  );

  const updateAlertMutation = useMutation(
    ({ id, data }: { id: number; data: { status: AlertStatus } }) =>
      apiService.stockAlerts.updateStockAlert(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('stock-alerts');
        queryClient.invalidateQueries('active-alerts');
      },
    }
  );

  const checkAlertsMutation = useMutation(
    () => apiService.stockAlerts.checkAlerts(),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('stock-alerts');
        queryClient.invalidateQueries('active-alerts');
      },
    }
  );

  const cleanupDuplicatesMutation = useMutation(
    () => apiService.stockAlerts.cleanupDuplicates(),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('stock-alerts');
        queryClient.invalidateQueries('active-alerts');
      },
    }
  );

  const handleStatusChange = (alertId: number, status: AlertStatus) => {
    updateAlertMutation.mutate({ id: alertId, data: { status } });
  };

  const getAlertIcon = (type: AlertType) => {
    switch (type) {
      case AlertType.LOW_STOCK:
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case AlertType.OUT_OF_STOCK:
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case AlertType.OVERSTOCK:
        return <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />;
      case AlertType.EXPIRY_WARNING:
        return <ExclamationTriangleIcon className="h-5 w-5 text-purple-500" />;
      default:
        return <BellIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: AlertStatus) => {
    switch (status) {
      case AlertStatus.ACTIVE:
        return 'bg-red-100 text-red-800';
      case AlertStatus.ACKNOWLEDGED:
        return 'bg-yellow-100 text-yellow-800';
      case AlertStatus.RESOLVED:
        return 'bg-green-100 text-green-800';
      case AlertStatus.DISMISSED:
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-center py-8 text-red-600">Error loading stock alerts</div>;

  const alerts = alertsData?.data || [];
  const activeAlertsCount = activeAlerts?.length || 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Stock Alerts</h1>
          <p className="text-sm text-gray-600 mt-1">
            Real-time alerts are automatically sent via WebSocket. No need to manually check for alerts.
          </p>
        </div>
        <div className="flex space-x-4">
          <button
            onClick={() => cleanupDuplicatesMutation.mutate()}
            disabled={cleanupDuplicatesMutation.isLoading}
            className="bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700 disabled:opacity-50 flex items-center"
          >
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            {cleanupDuplicatesMutation.isLoading ? 'Cleaning...' : 'Clean Duplicates'}
          </button>
        </div>
      </div>

      {/* Alert Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-full">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Alerts</p>
              <p className="text-2xl font-semibold text-gray-900">{activeAlertsCount}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-full">
              <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Low Stock</p>
              <p className="text-2xl font-semibold text-gray-900">
                {alerts.filter(a => a.alert_type === AlertType.LOW_STOCK && a.status === AlertStatus.ACTIVE).length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-full">
              <XCircleIcon className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Out of Stock</p>
              <p className="text-2xl font-semibold text-gray-900">
                {alerts.filter(a => a.alert_type === AlertType.OUT_OF_STOCK && a.status === AlertStatus.ACTIVE).length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-full">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Resolved</p>
              <p className="text-2xl font-semibold text-gray-900">
                {alerts.filter(a => a.status === AlertStatus.RESOLVED).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex space-x-4">
        <div>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            {Object.values(AlertStatus).map((status) => (
              <option key={status} value={status}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            {Object.values(AlertType).map((type) => (
              <option key={type} value={type}>
                {type.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Product
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Current Stock
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Threshold
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {alerts.map((alert) => (
              <tr key={alert.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    {getAlertIcon(alert.alert_type)}
                    <span className="ml-2 text-sm text-gray-900">
                      {alert.alert_type.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {alert.product?.name || `Product ID: ${alert.product_id}`}
                  </div>
                  {alert.product && (
                    <div className="text-xs text-gray-500">
                      SKU: {alert.product.sku} • Brand: {alert.product.brand}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {alert.location?.name || 'All Locations'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{alert.current_quantity}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{alert.threshold_quantity}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(alert.status)}`}>
                    {alert.status.charAt(0).toUpperCase() + alert.status.slice(1)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {new Date(alert.created_at).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  {(alert.status === AlertStatus.ACTIVE || alert.status === AlertStatus.ACKNOWLEDGED) && (
                    <div className="flex justify-end space-x-2">
                      {alert.status === AlertStatus.ACTIVE && (
                        <button
                          onClick={() => handleStatusChange(alert.id, AlertStatus.ACKNOWLEDGED)}
                          className="text-yellow-600 hover:text-yellow-900 text-xs"
                        >
                          Acknowledge
                        </button>
                      )}
                      <button
                        onClick={() => handleStatusChange(alert.id, AlertStatus.RESOLVED)}
                        className="text-green-600 hover:text-green-900 text-xs"
                      >
                        Resolve
                      </button>
                      <button
                        onClick={() => handleStatusChange(alert.id, AlertStatus.DISMISSED)}
                        className="text-gray-600 hover:text-gray-900 text-xs"
                      >
                        Dismiss
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {alerts.length === 0 && (
        <div className="text-center py-8">
          <BellIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No alerts found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {selectedStatus || selectedType ? 'Try adjusting your filters.' : 'All clear! No stock alerts at the moment.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default StockAlerts; 