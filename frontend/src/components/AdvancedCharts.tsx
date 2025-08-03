import React from 'react';
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
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ComposedChart,
  Scatter,
  ScatterChart,
  ZAxis,
  FunnelChart,
  Funnel,
  Sector,
  Cell as RechartsCell
} from 'recharts';

interface AdvancedChartsProps {
  inventory: any[];
  products: any[];
  categories: any[];
  purchaseOrders: any[];
  suppliers: any[];
}

const AdvancedCharts: React.FC<AdvancedChartsProps> = ({
  inventory,
  products,
  categories,
  purchaseOrders,
  suppliers
}) => {
  // Generate funnel chart data for purchase order funnel
  const poFunnelData = [
    { name: 'Draft', value: purchaseOrders.filter(po => po.status === 'draft').length, fill: '#6B7280' },
    { name: 'Pending Approval', value: purchaseOrders.filter(po => po.status === 'pending_approval').length, fill: '#F59E0B' },
    { name: 'Approved', value: purchaseOrders.filter(po => po.status === 'approved').length, fill: '#3B82F6' },
    { name: 'Ordered', value: purchaseOrders.filter(po => po.status === 'ordered').length, fill: '#8B5CF6' },
    { name: 'Received', value: purchaseOrders.filter(po => po.status === 'received').length, fill: '#10B981' }
  ];

  // Generate stock level distribution
  const stockLevelData = [
    { name: 'Critical (0-10%)', value: inventory.filter(item => {
      const product = products.find(p => p.id === item.product_id);
      const maxStock = product?.max_stock_level || 100;
      return item.quantity <= maxStock * 0.1;
    }).length, fill: '#EF4444' },
    { name: 'Low (10-25%)', value: inventory.filter(item => {
      const product = products.find(p => p.id === item.product_id);
      const maxStock = product?.max_stock_level || 100;
      return item.quantity > maxStock * 0.1 && item.quantity <= maxStock * 0.25;
    }).length, fill: '#F59E0B' },
    { name: 'Medium (25-75%)', value: inventory.filter(item => {
      const product = products.find(p => p.id === item.product_id);
      const maxStock = product?.max_stock_level || 100;
      return item.quantity > maxStock * 0.25 && item.quantity <= maxStock * 0.75;
    }).length, fill: '#3B82F6' },
    { name: 'High (75-100%)', value: inventory.filter(item => {
      const product = products.find(p => p.id === item.product_id);
      const maxStock = product?.max_stock_level || 100;
      return item.quantity > maxStock * 0.75 && item.quantity <= maxStock;
    }).length, fill: '#10B981' },
    { name: 'Overstocked (>100%)', value: inventory.filter(item => {
      const product = products.find(p => p.id === item.product_id);
      const maxStock = product?.max_stock_level || 100;
      return item.quantity > maxStock;
    }).length, fill: '#8B5CF6' }
  ];

  // Generate supplier performance data
  const supplierPerformanceData = suppliers.map(supplier => {
    const supplierPOs = purchaseOrders.filter(po => po.supplier_id === supplier.id);
    const totalValue = supplierPOs.reduce((sum, po) => sum + (po.total_amount || 0), 0);
    const avgDeliveryTime = supplierPOs.length > 0 ? 
      supplierPOs.reduce((sum, po) => {
        if (po.status === 'received' && po.created_at && po.updated_at) {
          const created = new Date(po.created_at);
          const received = new Date(po.updated_at);
          return sum + (received.getTime() - created.getTime()) / (1000 * 60 * 60 * 24); // days
        }
        return sum;
      }, 0) / supplierPOs.filter(po => po.status === 'received').length : 0;
    
    return {
      name: supplier.name,
      orders: supplierPOs.length,
      value: totalValue,
      avgDeliveryTime: avgDeliveryTime || 0,
      fill: getRandomColor()
    };
  }).sort((a, b) => b.value - a.value).slice(0, 8);

  // Generate monthly revenue trend
  const monthlyRevenueData = Array.from({ length: 12 }, (_, i) => {
    const month = new Date(2024, i, 1);
    const monthPOs = purchaseOrders.filter(po => {
      const poDate = new Date(po.created_at);
      return poDate.getMonth() === i && poDate.getFullYear() === 2024;
    });
    
    return {
      month: month.toLocaleDateString('en-US', { month: 'short' }),
      revenue: monthPOs.reduce((sum, po) => sum + (po.total_amount || 0), 0),
      orders: monthPOs.length,
      avgOrderValue: monthPOs.length > 0 ? 
        monthPOs.reduce((sum, po) => sum + (po.total_amount || 0), 0) / monthPOs.length : 0
    };
  });

  return (
    <div className="space-y-6">
      {/* Purchase Order Funnel Chart */}
      <div className="bg-white shadow-lg rounded-xl overflow-hidden">
        <div className="px-6 py-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-900">Purchase Order Funnel</h3>
            <div className="text-sm text-gray-500">Conversion Analysis</div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <FunnelChart>
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: 'none',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Funnel
                dataKey="value"
                data={poFunnelData}
                isAnimationActive={true}
                animationDuration={1000}
              >
                {poFunnelData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Funnel>
            </FunnelChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stock Level Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow-lg rounded-xl overflow-hidden">
          <div className="px-6 py-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">Stock Level Distribution</h3>
              <div className="text-sm text-gray-500">Inventory Health</div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stockLevelData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  animationDuration={1000}
                  animationBegin={0}
                >
                  {stockLevelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: 'none',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Supplier Performance */}
        <div className="bg-white shadow-lg rounded-xl overflow-hidden">
          <div className="px-6 py-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">Supplier Performance</h3>
              <div className="text-sm text-gray-500">Top Suppliers</div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={supplierPerformanceData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 12 }} />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'value' ? `$${Number(value).toFixed(2)}` : value,
                    name === 'value' ? 'Total Value' : name === 'orders' ? 'Orders' : 'Avg Delivery (days)'
                  ]}
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: 'none',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Bar dataKey="value" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Monthly Revenue Trends */}
      <div className="bg-white shadow-lg rounded-xl overflow-hidden">
        <div className="px-6 py-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-900">Monthly Revenue Trends</h3>
            <div className="text-sm text-gray-500">2024 Performance</div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={monthlyRevenueData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
                             <Tooltip 
                 formatter={(value, name) => [
                   name === 'revenue' ? `$${Number(value).toFixed(2)}` : 
                   name === 'avgOrderValue' ? `$${Number(value).toFixed(2)}` : value,
                   name === 'revenue' ? 'Revenue' : 
                   name === 'orders' ? 'Orders' : 'Avg Order Value'
                 ]}
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: 'none',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend />
              <Bar yAxisId="left" dataKey="orders" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              <Line yAxisId="right" type="monotone" dataKey="revenue" stroke="#10B981" strokeWidth={3} />
              <Line yAxisId="right" type="monotone" dataKey="avgOrderValue" stroke="#F59E0B" strokeWidth={2} strokeDasharray="5 5" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

// Helper function for random colors
function getRandomColor() {
  const colors = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6366F1'
  ];
  return colors[Math.floor(Math.random() * colors.length)];
}

export default AdvancedCharts; 