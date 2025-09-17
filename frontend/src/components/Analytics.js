import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

function Analytics({ analytics, monthlyTrends }) {
  if (!analytics) {
    return <div>No analytics data available</div>;
  }

  // Prepare data for pie chart
  const categoryData = Object.entries(analytics.by_category).map(([category, amount]) => ({
    name: category,
    value: amount
  }));

  return (
    <div className="grid">
      <div className="card">
        <h2>Spending Summary</h2>
        <div style={{ marginTop: '20px' }}>
          <p><strong>Total Amount:</strong> €{analytics.total_amount}</p>
          <p><strong>Total Receipts:</strong> {analytics.total_receipts}</p>
        </div>
      </div>

      <div className="card">
        <h2>Spending by Category</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={categoryData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: €${value}`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {categoryData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <h2>Monthly Trends</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthlyTrends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="total_amount" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Analytics;