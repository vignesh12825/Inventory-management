import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  CubeIcon, 
  TagIcon, 
  ArchiveBoxIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  ClipboardDocumentListIcon,
  BellIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowTrendingUpIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  ChartPieIcon
} from '@heroicons/react/24/outline';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import apiService from '../services/api';

const Dashboard: React.FC = () => {
  const { data: productsData } = useQuery(['products'], () => apiService.products.getProducts());
  const { data: categoriesData } = useQuery(['categories'], () => apiService.categories.getCategories());
  const { data: inventoryData } = useQuery(['inventory'], () => apiService.inventory.getInventory());
  const { data: suppliersData } = useQuery(['suppliers'], () => apiService.suppliers.getSuppliers());
  const { data: locationsData } = useQuery(['locations'], () => apiService.locations.getLocations());
  const { data: purchaseOrdersData } = useQuery(['purchase-orders'], () => apiService.purchaseOrders.getPurchaseOrders());
  const { data: activeAlertsData } = useQuery(['active-alerts'], () => apiService.stockAlerts.getActiveAlerts());

  const products = productsData?.data || [];
  const categories = categoriesData?.data || [];
  const inventory = inventoryData?.data || [];
  const suppliers = suppliersData?.data || [];
  const locations = locationsData?.data || [];
  const purchaseOrders = purchaseOrdersData?.data || [];
  const activeAlerts = activeAlertsData || [];

  // Calculate stock status with detailed information
  const inStockItems = inventory.filter(item => {
    const product = products.find(p => p.id === item.product_id);
    return item.available_quantity > (product?.min_stock_level || 0);
  });

  const lowStockItems = inventory.filter(item => {
    const product = products.find(p => p.id === item.product_id);
    return item.available_quantity > 0 && item.available_quantity <= (product?.min_stock_level || 0);
  });

  const outOfStockItems = inventory.filter(item => item.available_quantity <= 0);

  const pendingPOs = purchaseOrders.filter(po => 
    po.status === 'pending_approval' || po.status === 'approved'
  );

  // Stock Status Chart Data with detailed information
  const stockStatusData = [
    { 
      name: 'In Stock', 
      value: inStockItems.length, 
      fill: '#10B981', 
      stroke: '#059669',
      details: inStockItems.map(item => {
        const product = products.find(p => p.id === item.product_id);
        const location = locations.find(l => l.id === item.location_id);
        return `${product?.name || 'Unknown'} - ${item.available_quantity} units at ${location?.name || 'Unknown'}`;
      })
    },
    { 
      name: 'Low Stock', 
      value: lowStockItems.length, 
      fill: '#F59E0B', 
      stroke: '#D97706',
      details: lowStockItems.map(item => {
        const product = products.find(p => p.id === item.product_id);
        const location = locations.find(l => l.id === item.location_id);
        const minLevel = product?.min_stock_level || 0;
        return `${product?.name || 'Unknown'} - ${item.available_quantity}/${minLevel} units at ${location?.name || 'Unknown'}`;
      })
    },
    { 
      name: 'Out of Stock', 
      value: outOfStockItems.length, 
      fill: '#EF4444', 
      stroke: '#DC2626',
      details: outOfStockItems.map(item => {
        const product = products.find(p => p.id === item.product_id);
        const location = locations.find(l => l.id === item.location_id);
        return `${product?.name || 'Unknown'} - ${item.available_quantity} units at ${location?.name || 'Unknown'}`;
      })
    }
  ];

  // Purchase Order Status Chart Data with detailed information
  const poStatusData = [
    { 
      name: 'Draft', 
      value: purchaseOrders.filter(po => po.status === 'draft').length, 
      fill: '#6B7280',
      details: purchaseOrders.filter(po => po.status === 'draft').map(po => `PO-${po.id}: ${po.supplier?.name || 'Unknown Supplier'}`)
    },
    { 
      name: 'Pending', 
      value: purchaseOrders.filter(po => po.status === 'pending_approval').length, 
      fill: '#F59E0B',
      details: purchaseOrders.filter(po => po.status === 'pending_approval').map(po => `PO-${po.id}: ${po.supplier?.name || 'Unknown Supplier'}`)
    },
    { 
      name: 'Approved', 
      value: purchaseOrders.filter(po => po.status === 'approved').length, 
      fill: '#3B82F6',
      details: purchaseOrders.filter(po => po.status === 'approved').map(po => `PO-${po.id}: ${po.supplier?.name || 'Unknown Supplier'}`)
    },
    { 
      name: 'Ordered', 
      value: purchaseOrders.filter(po => po.status === 'ordered').length, 
      fill: '#8B5CF6',
      details: purchaseOrders.filter(po => po.status === 'ordered').map(po => `PO-${po.id}: ${po.supplier?.name || 'Unknown Supplier'}`)
    },
    { 
      name: 'Received', 
      value: purchaseOrders.filter(po => po.status === 'received').length, 
      fill: '#10B981',
      details: purchaseOrders.filter(po => po.status === 'received').map(po => `PO-${po.id}: ${po.supplier?.name || 'Unknown Supplier'}`)
    },
    { 
      name: 'Cancelled', 
      value: purchaseOrders.filter(po => po.status === 'cancelled').length, 
      fill: '#EF4444',
      details: purchaseOrders.filter(po => po.status === 'cancelled').map(po => `PO-${po.id}: ${po.supplier?.name || 'Unknown Supplier'}`)
    }
  ];

  const stats = [
    {
      name: 'Total Products',
      value: products.length,
      icon: CubeIcon,
      color: 'bg-blue-500',
      href: '/products'
    },
    {
      name: 'Inventory Items',
      value: inventory.length,
      icon: ArchiveBoxIcon,
      color: 'bg-purple-500',
      href: '/inventory'
    },
    {
      name: 'Purchase Orders',
      value: purchaseOrders.length,
      icon: ClipboardDocumentListIcon,
      color: 'bg-pink-500',
      href: '/purchase-orders'
    },
    {
      name: 'Active Alerts',
      value: activeAlerts.length,
      icon: BellIcon,
      color: 'bg-red-500',
      href: '/stock-alerts'
    }
  ];

  // Custom Tooltip for Stock Status Chart
  const StockStatusTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-bold text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">Count: {data.value}</p>
          <p className="text-sm text-gray-600">Percentage: {((data.value / stockStatusData.reduce((sum, item) => sum + item.value, 0)) * 100).toFixed(1)}%</p>
          {data.details && data.details.length > 0 && (
            <div className="mt-2">
              <p className="text-xs font-semibold text-gray-700 mb-1">Details:</p>
              <div className="max-h-32 overflow-y-auto">
                {data.details.slice(0, 5).map((detail: string, index: number) => (
                  <p key={index} className="text-xs text-gray-600">• {detail}</p>
                ))}
                {data.details.length > 5 && (
                  <p className="text-xs text-gray-500">... and {data.details.length - 5} more</p>
                )}
              </div>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  // Custom Tooltip for Purchase Order Chart
  const PurchaseOrderTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-bold text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">Count: {data.value}</p>
          <p className="text-sm text-gray-600">Percentage: {((data.value / poStatusData.reduce((sum, item) => sum + item.value, 0)) * 100).toFixed(1)}%</p>
          {data.details && data.details.length > 0 && (
            <div className="mt-2">
              <p className="text-xs font-semibold text-gray-700 mb-1">Purchase Orders:</p>
              <div className="max-h-32 overflow-y-auto">
                {data.details.slice(0, 5).map((detail: string, index: number) => (
                  <p key={index} className="text-xs text-gray-600">• {detail}</p>
                ))}
                {data.details.length > 5 && (
                  <p className="text-xs text-gray-500">... and {data.details.length - 5} more</p>
                )}
              </div>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome to your Inventory Management System</p>
        </div>
        <div className="flex items-center space-x-2">
          <ChartBarIcon className="h-6 w-6 text-blue-600" />
          <span className="text-sm text-gray-500">Real-time Analytics</span>
        </div>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Link
            key={stat.name}
            to={stat.href}
            className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
          >
            <div className="p-6">
              <div className="flex items-center">
                <div className={`flex-shrink-0 p-3 rounded-xl ${stat.color} shadow-lg`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                  <dd className="text-2xl font-bold text-gray-900">{stat.value}</dd>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stock Status Pie Chart */}
        <div className="bg-white shadow-lg rounded-xl overflow-hidden">
          <div className="px-6 py-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">Stock Status Overview</h3>
              <ChartPieIcon className="h-6 w-6 text-blue-600" />
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stockStatusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={100}
                  innerRadius={60}
                  fill="#8884d8"
                  dataKey="value"
                  animationDuration={1000}
                  animationBegin={0}
                >
                  {stockStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} stroke={entry.stroke} strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip content={<StockStatusTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Purchase Order Status Bar Chart */}
        <div className="bg-white shadow-lg rounded-xl overflow-hidden">
          <div className="px-6 py-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">Purchase Order Status</h3>
              <ChartBarIcon className="h-6 w-6 text-green-600" />
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={poStatusData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip content={<PurchaseOrderTooltip />} />
                <Bar dataKey="value" fill="#8884d8">
                  {poStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow-lg rounded-xl p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/inventory"
            className="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <ArchiveBoxIcon className="h-6 w-6 text-blue-600 mr-3" />
            <span className="font-medium text-blue-900">Manage Inventory</span>
          </Link>
          <Link
            to="/purchase-orders"
            className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
          >
            <ClipboardDocumentListIcon className="h-6 w-6 text-green-600 mr-3" />
            <span className="font-medium text-green-900">View Purchase Orders</span>
          </Link>
          <Link
            to="/stock-alerts"
            className="flex items-center p-4 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
          >
            <BellIcon className="h-6 w-6 text-red-600 mr-3" />
            <span className="font-medium text-red-900">Check Alerts</span>
          </Link>
          <Link
            to="/products"
            className="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
          >
            <CubeIcon className="h-6 w-6 text-purple-600 mr-3" />
            <span className="font-medium text-purple-900">Manage Products</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 