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
  ResponsiveContainer
} from 'recharts';

const ChartTest: React.FC = () => {
  // Sample data for testing
  const sampleData = [
    { name: 'Electronics', value: 400, fill: '#3B82F6' },
    { name: 'Clothing', value: 300, fill: '#10B981' },
    { name: 'Books', value: 200, fill: '#F59E0B' },
    { name: 'Home & Garden', value: 150, fill: '#EF4444' }
  ];

  const barData = [
    { name: 'Jan', value: 400 },
    { name: 'Feb', value: 300 },
    { name: 'Mar', value: 200 },
    { name: 'Apr', value: 278 },
    { name: 'May', value: 189 },
    { name: 'Jun', value: 239 }
  ];

  return (
    <div className="space-y-6 p-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Chart Test Component</h2>
        <p className="text-gray-600">This is a test to verify charts are working</p>
      </div>

      {/* Pie Chart Test */}
      <div className="bg-white shadow-lg rounded-xl overflow-hidden">
        <div className="px-6 py-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Sample Pie Chart</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sampleData}
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
                {sampleData.map((entry, index) => (
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

      {/* Bar Chart Test */}
      <div className="bg-white shadow-lg rounded-xl overflow-hidden">
        <div className="px-6 py-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Sample Bar Chart</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: 'none',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
        <strong>Success!</strong> If you can see the charts above, the chart implementation is working correctly.
      </div>
    </div>
  );
};

export default ChartTest; 