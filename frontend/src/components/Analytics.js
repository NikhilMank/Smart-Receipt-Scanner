import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = [
  '#0088FE', // Blue
  '#00C49F', // Green
  '#FFBB28', // Yellow
  '#FF8042', // Orange
  '#8884D8', // Purple
  '#82CA9D', // Light Green
  '#FFC658', // Gold
  '#FF7C7C', // Light Red
  '#8DD1E1', // Light Blue
  '#D084D0', // Pink
  '#87D068', // Lime
  '#FFB347', // Peach
  '#B19CD9', // Lavender
  '#FFD700', // Bright Gold
  '#FF6B6B'  // Coral
];

function Analytics({ analytics, monthlyTrends }) {
  if (!analytics) {
    return <div>No analytics data available</div>;
  }

  // Debug: Log the data structure
  console.log('Monthly trends data:', monthlyTrends);
  
  // Get all unique categories across all months
  const allCategories = new Set();
  monthlyTrends.forEach(month => {
    Object.keys(month)
      .filter(key => !['month', 'total_amount', 'receipt_count'].includes(key))
      .forEach(category => allCategories.add(category));
  });
  const categories = Array.from(allCategories);
  console.log('All categories found:', categories);

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
        <h2>Monthly Trends by Category</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthlyTrends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            {/* Dynamic bars for all categories */}
            {categories.map((category, index) => (
              <Bar 
                key={category} 
                dataKey={category} 
                stackId="a" 
                fill={COLORS[index % COLORS.length]} 
                name={category}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Analytics;